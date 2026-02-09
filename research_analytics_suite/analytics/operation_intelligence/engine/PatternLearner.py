"""
PatternLearner Module

Learns from user behavior and simulation results to improve recommendations.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Development
"""
import pickle
import numpy as np
from pathlib import Path
from typing import Dict, Type, Any, List
from datetime import datetime

from research_analytics_suite.utils.CustomLogger import CustomLogger
from research_analytics_suite.utils.Config import Config
from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation
from research_analytics_suite.analytics.operation_intelligence.models import (
    UserFeedback,
    SimulationResult
)

# Scikit-learn imports
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import LabelEncoder
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class PatternLearner:
    """
    Learns from feedback and simulations.

    Key Features:
    - Tracks user acceptance/rejection patterns
    - Learns from simulation outcomes
    - Updates recommendation models
    - Incremental learning
    """

    def __init__(self):
        """
        Initialize pattern learner.

        Args:
            config: Configuration object
        """
        self._logger = CustomLogger()
        from research_analytics_suite.utils.Config import Config
        self._config = Config()

        # ML Model
        self._model = None
        self._label_encoder = None
        self._is_trained = False

        # Training data storage
        self._training_data: List[Dict[str, Any]] = []
        self._feedback_history: List[UserFeedback] = []
        self._simulation_history: List[SimulationResult] = []

        # Model path
        workspace_dir = self._config.WORKSPACE_DIR #if self._config.WORKSPACE_DIR else "workspace"
        self._model_dir = Path(workspace_dir) / "operation_intelligence" / "models"
        try:
            self._model_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self._logger.warning(f"Could not create model directory: {e}, using temp directory")
            import tempfile
            self._model_dir = Path(tempfile.gettempdir()) / "ras_operation_intelligence" / "models"
            self._model_dir.mkdir(parents=True, exist_ok=True)

        # Initialize model if sklearn available
        if SKLEARN_AVAILABLE:
            self._model = RandomForestClassifier(
                n_estimators=50,
                max_depth=10,
                random_state=42
            )
            self._label_encoder = LabelEncoder()
        else:
            self._logger.warning("scikit-learn not available, pattern learning disabled")

    async def train_on_feedback(self, feedback: UserFeedback) -> None:
        """
        Trains on user feedback.

        Args:
            feedback: User feedback
        """
        self._logger.debug(f"Training on feedback: {feedback.recommendation_id}")

        if not SKLEARN_AVAILABLE:
            return

        try:
            # Store feedback
            self._feedback_history.append(feedback)

            # Create training example
            training_example = {
                'timestamp': feedback.timestamp,
                'accepted': feedback.accepted,
                'context': feedback.context,
            }
            self._training_data.append(training_example)

            # Retrain if enough data
            if self._should_retrain():
                await self.update_recommendation_model()

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    async def train_on_simulation(self, simulation_result: SimulationResult) -> None:
        """
        Trains on simulation results.

        Args:
            simulation_result: Simulation result
        """
        self._logger.debug("Training on simulation result")

        if not SKLEARN_AVAILABLE:
            return

        try:
            # Store simulation result
            self._simulation_history.append(simulation_result)

            # Create training example from simulation
            training_example = {
                'timestamp': datetime.now(),
                'accepted': simulation_result.success,  # Use success as proxy for acceptance
                'context': {
                    'operation_type': simulation_result.operation_type.__name__ if simulation_result.operation_type else 'unknown',
                    'execution_time': simulation_result.execution_time,
                    'memory_used': simulation_result.memory_used,
                    'success': simulation_result.success
                },
            }
            self._training_data.append(training_example)

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    async def update_recommendation_model(self) -> None:
        """
        Updates recommendation models.
        """
        self._logger.info("Updating recommendation model")

        if not SKLEARN_AVAILABLE or len(self._training_data) < self._config.PATTERN_LEARNING_MIN_SAMPLES:
            return

        try:
            # Prepare training data
            X = []  # Features
            y = []  # Labels (accepted/rejected)

            for example in self._training_data:
                # Extract features from context
                context = example.get('context', {})
                features = [
                    hash(context.get('operation_type', 'unknown')) % 10000,  # Operation type hash
                    context.get('execution_time', 0.0),
                    context.get('memory_used', 0.0),
                    1.0 if context.get('success', False) else 0.0,
                ]
                X.append(features)
                y.append(1 if example['accepted'] else 0)

            if len(X) == 0 or len(set(y)) < 2:  # Need at least 2 classes
                self._logger.warning("Insufficient data for training (need both accepted and rejected examples)")
                return

            # Convert to numpy arrays
            X = np.array(X)
            y = np.array(y)

            # Train the model
            self._model.fit(X, y)
            self._is_trained = True

            self._logger.info(f"Model trained on {len(X)} examples")

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    def predict_user_preference(
        self,
        operation: Type[BaseOperation],
        context: Dict[str, Any]
    ) -> float:
        """
        Predicts user preference for operation.

        Args:
            operation: Operation type
            context: Context information

        Returns:
            Preference score (0.0 to 1.0)
        """
        if not SKLEARN_AVAILABLE or not self._is_trained:
            return 0.5  # Neutral score if model not available

        try:
            # Prepare features
            features = [
                hash(operation.__name__) % 10000,
                context.get('execution_time', 0.0),
                context.get('memory_used', 0.0),
                1.0 if context.get('success', False) else 0.0,
            ]

            # Get prediction probability
            X = np.array([features])
            probabilities = self._model.predict_proba(X)

            # Return probability of acceptance (class 1)
            if probabilities.shape[1] > 1:
                return float(probabilities[0][1])
            else:
                return 0.5

        except Exception as e:
            self._logger.warning(f"Failed to predict user preference: {e}")
            return 0.5

    async def save_model(self) -> None:
        """
        Persists trained models.
        """
        self._logger.debug("Saving pattern learning model")

        if not SKLEARN_AVAILABLE or not self._is_trained:
            return

        try:
            # Save model
            model_path = self._model_dir / "pattern_learner_model.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump({
                    'model': self._model,
                    'is_trained': self._is_trained,
                    'training_data': self._training_data,
                }, f)

            self._logger.info(f"Model saved to {model_path}")

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    async def load_model(self) -> None:
        """
        Loads persisted models.
        """
        self._logger.debug("Loading pattern learning model")

        if not SKLEARN_AVAILABLE:
            return

        try:
            model_path = self._model_dir / "pattern_learner_model.pkl"

            if not model_path.exists():
                self._logger.debug("No saved model found, starting fresh")
                return

            # Load model
            with open(model_path, 'rb') as f:
                data = pickle.load(f)

            self._model = data.get('model')
            self._is_trained = data.get('is_trained', False)
            self._training_data = data.get('training_data', [])

            self._logger.info(f"Model loaded from {model_path} with {len(self._training_data)} training examples")

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    def _should_retrain(self) -> bool:
        """
        Determines if model should be retrained.

        Returns:
            True if retraining recommended
        """
        min_samples = self._config.PATTERN_LEARNING_MIN_SAMPLES
        return len(self._training_data) >= min_samples

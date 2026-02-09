"""
IntelligenceEngine Module

Main orchestrator for the operation intelligence system.
Coordinates analysis, simulation, and recommendation processes.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Development
"""
import asyncio
from typing import List, Optional

from research_analytics_suite.utils.CustomLogger import CustomLogger
from research_analytics_suite.utils.Config import Config
from research_analytics_suite.data_engine.Workspace import Workspace
from research_analytics_suite.analytics.operation_intelligence.models import Recommendation, UserFeedback


class IntelligenceEngine:
    """
    Main orchestrator for operation intelligence system.

    Coordinates:
    - Operation analysis and matching
    - Simulation in sandbox environments
    - Result evaluation
    - Pattern learning from feedback
    - Recommendation generation

    Key Features:
    - Async processing
    - Configuration-driven behavior
    - Event-driven architecture
    - Graceful shutdown
    """

    _instance: Optional['IntelligenceEngine'] = None
    _lock: asyncio.Lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        """Singleton pattern for system-wide access."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize intelligence engine."""
        if not hasattr(self, '_initialized'):
            self._logger = CustomLogger()
            self._config: Optional[Config] = None

            # Components (initialized in initialize())
            self._analyzer = None
            self._simulator = None
            self._evaluator = None
            self._learner = None

            # State
            self._is_running = False
            self._background_task: Optional[asyncio.Task] = None
            self._recommendation_queue: List[Recommendation] = []

            self._initialized = False

    async def initialize(self) -> None:
        """
        Initializes intelligence engine.
        """
        if self._initialized:
            return

        self._logger.debug("Initializing Intelligence Engine")

        # Get Config singleton
        from research_analytics_suite.utils.Config import Config
        self._config = Config()

        try:
            # Initialize components
            from research_analytics_suite.analytics.operation_intelligence.engine.OperationAnalyzer import (
                OperationAnalyzer
            )
            from research_analytics_suite.analytics.operation_intelligence.simulation.OperationSimulator import (
                OperationSimulator
            )
            from research_analytics_suite.analytics.operation_intelligence.simulation.ResultEvaluator import (
                ResultEvaluator
            )
            from research_analytics_suite.analytics.operation_intelligence.engine.PatternLearner import (
                PatternLearner
            )

            self._analyzer = OperationAnalyzer()
            self._simulator = OperationSimulator()
            self._evaluator = ResultEvaluator()
            self._learner = PatternLearner()

            await self._learner.load_model()

            self._initialized = True
            self._logger.debug("Intelligence Engine initialized successfully")

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)
            raise

    async def analyze_workspace(self, workspace: Workspace) -> List[Recommendation]:
        """
        Analyzes workspace and generates recommendations.

        Args:
            workspace: Workspace to analyze

        Returns:
            List of recommendations
        """
        if not self._initialized:
            raise RuntimeError("Intelligence Engine not initialized")

        self._logger.info("Analyzing workspace for recommendations")

        try:
            recommendations = []

            # Step 1: Create sandbox from workspace
            from research_analytics_suite.data_engine.sandbox.SandboxWorkspace import SandboxWorkspace
            from research_analytics_suite.data_engine.sandbox.WorkspaceCloner import WorkspaceCloner

            sandbox = SandboxWorkspace(
                name=f"Sandbox_{workspace._config.WORKSPACE_NAME}_{asyncio.get_event_loop().time()}"
            )
            await sandbox.create_from_workspace(workspace)

            cloner = WorkspaceCloner()
            await cloner.clone_workspace(workspace, sandbox)

            self._logger.debug("Sandbox workspace created and cloned")

            # Step 2: Analyze data characteristics
            data_profiles = await sandbox.get_data_profiles()

            if not data_profiles:
                self._logger.info("No data profiles available for analysis")
                await sandbox.cleanup()
                return recommendations

            self._logger.debug(f"Analyzing {len(data_profiles)} data profiles")

            # Step 3: Find compatible operations for each data profile
            from research_analytics_suite.analytics.operation_intelligence.simulation.OperationSimulator import OperationConfig

            operations_to_simulate = []

            for profile in data_profiles[:3]:  # Limit to first 3 profiles for efficiency
                characteristics = await self._analyzer.analyze_data_profile(profile)
                compatible_ops = await self._analyzer.find_compatible_operations(characteristics)

                # Take top 5 operations per profile
                for op_match in compatible_ops[:5]:
                    operations_to_simulate.append(
                        OperationConfig(
                            operation_type=op_match.operation_type,
                            parameters={}  # Default parameters
                        )
                    )

            if not operations_to_simulate:
                self._logger.info("No compatible operations found")
                await sandbox.cleanup()
                return recommendations

            self._logger.debug(f"Found {len(operations_to_simulate)} operations to simulate")

            # Step 4: Simulate operations
            simulation_results = await self._simulator.simulate_batch(operations_to_simulate, sandbox)

            self._logger.debug(f"Completed {len(simulation_results)} simulations")

            # Step 5: Evaluate results
            for sim_result in simulation_results:
                evaluation = self._evaluator.evaluate_result(sim_result)

                # Step 6: Generate recommendations for high-quality results
                if evaluation.should_recommend:
                    # Get user preference prediction
                    context = {
                        'execution_time': sim_result.execution_time,
                        'memory_used': sim_result.memory_used,
                        'success': sim_result.success
                    }
                    user_preference = self._learner.predict_user_preference(
                        sim_result.operation_type,
                        context
                    )

                    # Combine evaluation confidence with user preference
                    final_confidence = (evaluation.confidence + user_preference) / 2.0

                    if final_confidence >= self._config.RECOMMENDATION_CONFIDENCE_THRESHOLD:
                        recommendation = Recommendation(
                            operation_type=sim_result.operation_type,
                            parameters={},
                            confidence=final_confidence,
                            explanation=evaluation.explanation,
                            expected_benefits=[
                                f"Performance score: {evaluation.performance_score:.2f}",
                                f"Execution time: {sim_result.execution_time:.2f}s",
                                f"Memory usage: {sim_result.memory_used:.1f}MB"
                            ],
                            simulation_result=sim_result
                        )
                        recommendations.append(recommendation)

            # Cleanup sandbox
            await sandbox.cleanup()

            # Sort recommendations by confidence
            recommendations.sort(key=lambda r: r.confidence, reverse=True)

            # Limit to top N recommendations
            max_recommendations = self._config.RECOMMENDATION_MAX_QUEUE_SIZE
            recommendations = recommendations[:max_recommendations]

            self._logger.info(f"Generated {len(recommendations)} recommendations")
            return recommendations

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)
            return []

    async def process_user_feedback(self, recommendation_id: str, accepted: bool) -> None:
        """
        Processes user feedback for learning.

        Args:
            recommendation_id: ID of recommendation
            accepted: Whether user accepted the recommendation
        """
        self._logger.info(f"Processing feedback for recommendation: {recommendation_id}")

        try:
            feedback = UserFeedback(
                recommendation_id=recommendation_id,
                accepted=accepted
            )

            await self._learner.train_on_feedback(feedback)

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    async def start_background_analysis(self) -> None:
        """
        Starts background analysis tasks.
        """
        if self._is_running:
            return

        self._logger.debug("Starting background analysis")
        self._is_running = True

        self._background_task = asyncio.create_task(self._background_loop())

    async def _background_loop(self) -> None:
        """
        Background loop for periodic analysis.
        """
        # Ensure interval is a valid number
        interval = self._config.BACKGROUND_ANALYSIS_INTERVAL_SECONDS
        if interval is None or not isinstance(interval, (int, float)):
            try:
                interval = int(interval)
            except (ValueError, TypeError):
                interval = 300  # Default to 5 minutes
                self._logger.warning(f"Invalid BACKGROUND_ANALYSIS_INTERVAL_SECONDS, using default: {interval}")

        while self._is_running:
            try:
                # TODO: Perform periodic analysis
                await asyncio.sleep(interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(e, self.__class__.__name__)
                await asyncio.sleep(interval)

    async def stop(self) -> None:
        """
        Stops intelligence engine.
        """
        self._logger.info("Stopping Intelligence Engine")
        self._is_running = False

        if self._background_task:
            self._background_task.cancel()
            try:
                await self._background_task
            except asyncio.CancelledError:
                pass

        # Save learned patterns
        if self._learner:
            await self._learner.save_model()

        self._logger.info("Intelligence Engine stopped")

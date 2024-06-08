from neurobehavioral_analytics_suite.machine_learning import Model
from neurobehavioral_analytics_suite.operation_manager.operations.Operation import Operation
from sklearn.model_selection import train_test_split
import asyncio


class MLTrainingOperation(Operation):
    def __init__(self, model: Model, data, target, test_size=0.2, random_state=42):
        super().__init__(func=None, name="MLTrainingOperation")
        self.model = model
        self.data = data
        self.target = target
        self.test_size = test_size
        self.random_state = random_state
        self.train_data = None
        self.val_data = None

    def start(self):
        """Initialize training parameters and split data."""
        X_train, X_val, y_train, y_val = train_test_split(
            self.data, self.target, test_size=self.test_size, random_state=self.random_state
        )
        self.train_data = (X_train, y_train)
        self.val_data = (X_val, y_val)
        self._status = "started"
        self.add_log_entry("Training operation started")

    async def execute(self):
        """Train the machine learning model."""
        try:
            self._status = "running"
            X_train, y_train = self.train_data
            self.model.train(X_train, y_train)
            self._status = "completed"
            self.add_log_entry("Training completed successfully")
        except Exception as e:
            self._logger.error(e, self)
            self._status = "error"
            self.add_log_entry(f"Error during training: {e}")

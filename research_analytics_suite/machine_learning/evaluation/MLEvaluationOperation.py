from research_analytics_suite.machine_learning import Evaluator
from research_analytics_suite.operation_manager.operations.Operation import Operation


class MLEvaluationOperation(Operation):
    def __init__(self, model, test_data, test_target):
        super().__init__(func=None, name="MLEvaluationOperation")
        self.model = model
        self.test_data = test_data
        self.test_target = test_target

    def start(self):
        """Initialize evaluation parameters."""
        self.status = "started"
        self.add_log_entry("Evaluation operation started")

    async def execute(self):
        """Evaluate the machine learning model."""
        try:
            self.status = "running"
            metrics = await Evaluator.evaluate(self.model, self.test_data, self.test_target)
            self.status = "completed"
            self.add_log_entry("Evaluation completed successfully")
            return metrics
        except Exception as e:
            self._logger.error(e, self)
            self.status = "error"
            self.add_log_entry(f"Error during evaluation: {e}")

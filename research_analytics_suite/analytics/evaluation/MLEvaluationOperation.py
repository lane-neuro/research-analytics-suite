from research_analytics_suite.operation_manager.operations.core import BaseOperation


class MLEvaluationOperation(BaseOperation):
    def __init__(self, *args, **kwargs):
        super().__init__(action=None, name="MLEvaluationOperation")
        self.model = args[0]
        self.test_data = args[1]
        self.test_target = args[2]

    def start_operation(self):
        """Initialize evaluation parameters."""
        self.status = "started"
        self.add_log_entry("Evaluation operation started")

    async def execute(self):
        """Evaluate the machine learning model."""
        try:
            self.status = "running"
            from research_analytics_suite.analytics.evaluation import Evaluator
            metrics = await Evaluator.evaluate(self.model, self.test_data, self.test_target)
            self.status = "completed"
            self.add_log_entry("Evaluation completed successfully")
            return metrics
        except Exception as e:
            self._logger.error(e, self)
            self.status = "error"
            self.add_log_entry(f"Error during evaluation: {e}")

from research_analytics_suite.data_engine.project.save_project import save_project
from research_analytics_suite.operation_manager.operations.Operation import Operation


class SaveProjectOperation(Operation):
    def __init__(self, error_handler, data_engine):
        super().__init__(name="SaveProjectOperation")
        self.error_handler = error_handler
        self.data_engine = data_engine

    async def execute(self):
        try:
            self.data_engine = save_project(param1, param2, ...)  # replace with actual parameters
            self.status = "completed"
        except Exception as e:
            self._logger.error(e, self)
            self.status = "error"

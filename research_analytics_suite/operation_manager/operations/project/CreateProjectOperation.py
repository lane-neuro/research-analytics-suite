from research_analytics_suite.operation_manager.operations.Operation import Operation


class CreateProjectOperation(Operation):
    def __init__(self, error_handler, data_engine):
        super().__init__(name="CreateProjectOperation")
        self.error_handler = error_handler
        self.data_engine = data_engine

    async def execute(self):
        try:
            self.data_engine = None # new_project(param1, param2, ...)  # replace with actual parameters
            self.status = "completed"
        except Exception as e:
            self._logger.error(e, self)
            self.status = "error"

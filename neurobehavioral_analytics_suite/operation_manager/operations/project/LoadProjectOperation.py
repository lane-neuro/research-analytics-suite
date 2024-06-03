from neurobehavioral_analytics_suite.data_engine.project.load_project import load_project
from neurobehavioral_analytics_suite.operation_manager.operations.Operation import Operation


class LoadProjectOperation(Operation):
    def __init__(self, error_handler, data_engine):
        super().__init__(name="LoadProjectOperation")
        self.error_handler = error_handler
        self.data_engine = data_engine

    async def execute(self):
        try:
            self.data_engine = None  # load_project(param1, param2, ...)  # replace with actual parameters
            self.status = "completed"
        except Exception as e:
            self.error_handler.handle_error(e, self)
            self.status = "error"

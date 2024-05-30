from neurobehavioral_analytics_suite.data_engine.project.save_project import save_project
from neurobehavioral_analytics_suite.operation_manager.operation.Operation import Operation


class SaveProjectOperation(Operation):
    def __init__(self, error_handler, data_engine):
        super().__init__(name="SaveProjectOperation")
        self.error_handler = error_handler
        self.data_engine = data_engine

    async def execute(self):
        save_project(self.data_engine, ...)  # fill in the file path as needed

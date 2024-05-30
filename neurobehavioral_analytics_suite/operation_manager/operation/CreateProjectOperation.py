from neurobehavioral_analytics_suite.data_engine.project.new_project import new_project
from neurobehavioral_analytics_suite.operation_manager.operation.Operation import Operation


class CreateProjectOperation(Operation):
    def __init__(self, error_handler, data_engine):
        super().__init__(name="CreateProjectOperation")
        self.error_handler = error_handler
        self.data_engine = data_engine

    async def execute(self):
        self.data_engine = new_project(...)  # fill in the parameters as needed

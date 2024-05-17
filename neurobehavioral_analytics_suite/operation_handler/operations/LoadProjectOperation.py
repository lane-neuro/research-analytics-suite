from neurobehavioral_analytics_suite.data_engine.project.load_project import load_project
from neurobehavioral_analytics_suite.operation_handler.Operation import Operation


class LoadProjectOperation(Operation):
    def __init__(self, error_handler, data_engine):
        super().__init__(name="LoadProjectOperation")
        self.error_handler = error_handler
        self.data_engine = data_engine

    async def execute(self):
        self.data_engine = load_project(...)  # fill in the file path as needed
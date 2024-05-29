# neurobehavioral_analytics_suite/gui/ProjectManagerGui.py
import dearpygui.dearpygui as dpg
import asyncio
from neurobehavioral_analytics_suite.data_engine.project.load_project import load_project
from neurobehavioral_analytics_suite.data_engine.project.save_project import save_project
from neurobehavioral_analytics_suite.data_engine.DataEngine import DataEngine
from neurobehavioral_analytics_suite.operation_handler.OperationHandler import OperationHandler
from neurobehavioral_analytics_suite.operation_handler.operations.CreateProjectOperation import CreateProjectOperation
from neurobehavioral_analytics_suite.operation_handler.operations.LoadProjectOperation import LoadProjectOperation
from neurobehavioral_analytics_suite.operation_handler.operations.SaveProjectOperation import SaveProjectOperation


class ProjectManagerGui:
    def __init__(self, data_engine: DataEngine, operation_handler: OperationHandler):
        self.window = dpg.add_window(label="Project Manager")
        dpg.add_button(label="Create Project", callback=self.create_project_wrapper, parent=self.window)
        dpg.add_button(label="Load Project", callback=self.load_project_wrapper, parent=self.window)
        dpg.add_button(label="Save Project", callback=self.save_project_wrapper, parent=self.window)
        self.data_engine = data_engine
        self.operation_handler = operation_handler

    async def create_project(self, sender, data):
        print("Creating a new project...")
        await asyncio.sleep(3)

    async def load_project(self, sender, data):
        file_path = dpg.open_file_dialog(directory='.', extensions='.json')
        if file_path:
            self.data_engine = load_project(file_path[0])
            print(f"Loaded project from {file_path[0]}")

    async def save_project(self, sender, data):
        if self.data_engine:
            file_path = dpg.save_file_dialog(directory='.', extensions='.json')
            if file_path:
                save_project(self.data_engine, file_path[0])
                print(f"Saved project to {file_path[0]}")
        else:
            print("No project to save")

    def create_project_wrapper(self, sender, data):
        operation = CreateProjectOperation(self.operation_handler.error_handler, self.data_engine)

    def load_project_wrapper(self, sender, data):
        operation = LoadProjectOperation(self.operation_handler.error_handler, self.data_engine)

    def save_project_wrapper(self, sender, data):
        operation = SaveProjectOperation(self.operation_handler.error_handler, self.data_engine)
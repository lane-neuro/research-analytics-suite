# neurobehavioral_analytics_suite/gui/ProjectManagerDialog.py

import dearpygui.dearpygui as dpg
import asyncio
from neurobehavioral_analytics_suite.data_engine.project.load_project import load_project
from neurobehavioral_analytics_suite.data_engine.project.save_project import save_project
from neurobehavioral_analytics_suite.data_engine.DataEngine import DataEngine
from neurobehavioral_analytics_suite.operation_manager.OperationControl import OperationControl
from neurobehavioral_analytics_suite.operation_manager.operation.project.CreateProjectOperation import CreateProjectOperation
from neurobehavioral_analytics_suite.operation_manager.operation.project.LoadProjectOperation import LoadProjectOperation
from neurobehavioral_analytics_suite.operation_manager.operation.project.SaveProjectOperation import SaveProjectOperation


class ProjectManagerDialog:
    """A class to manage the dialog for creating, loading, and saving projects."""

    def __init__(self, data_engine: DataEngine, operation_control: OperationControl):
        """Initializes the ProjectManagerDialog with the given data engine and operation control.

        Args:
            data_engine: Instance of DataEngine to manage project data.
            operation_control: Control interface for operations.
        """
        self.window = dpg.add_window(label="Project Manager")
        dpg.add_button(label="Create Project", callback=self.create_project_wrapper, parent=self.window)
        dpg.add_button(label="Load Project", callback=self.load_project_wrapper, parent=self.window)
        dpg.add_button(label="Save Project", callback=self.save_project_wrapper, parent=self.window)
        self.data_engine = data_engine
        self.operation_control = operation_control

    async def create_project(self, sender, data):
        """Creates a new project.

        Args:
            sender: The sender of the create project event.
            data: Additional application data.
        """
        print("Creating a new project...")
        await asyncio.sleep(3)

    async def load_project(self, sender, data):
        """Loads an existing project.

        Args:
            sender: The sender of the load project event.
            data: Additional application data.
        """
        file_path = dpg.open_file_dialog(directory='.', extensions='.json')
        if file_path:
            self.data_engine = load_project(file_path[0])
            print(f"Loaded project from {file_path[0]}")

    async def save_project(self, sender, data):
        """Saves the current project.

        Args:
            sender: The sender of the save project event.
            data: Additional application data.
        """
        if self.data_engine:
            file_path = dpg.save_file_dialog(directory='.', extensions='.json')
            if file_path:
                save_project(self.data_engine, file_path[0])
                print(f"Saved project to {file_path[0]}")
        else:
            print("No project to save")

    def create_project_wrapper(self, sender, data):
        """Wrapper to create a project operation.

        Args:
            sender: The sender of the create project event.
            data: Additional application data.
        """
        operation = CreateProjectOperation(self.operation_control.error_handler, self.data_engine)

    def load_project_wrapper(self, sender, data):
        """Wrapper to load a project operation.

        Args:
            sender: The sender of the load project event.
            data: Additional application data.
        """
        operation = LoadProjectOperation(self.operation_control.error_handler, self.data_engine)

    def save_project_wrapper(self, sender, data):
        """Wrapper to save a project operation.

        Args:
            sender: The sender of the save project event.
            data: Additional application data.
        """
        operation = SaveProjectOperation(self.operation_control.error_handler, self.data_engine)
        
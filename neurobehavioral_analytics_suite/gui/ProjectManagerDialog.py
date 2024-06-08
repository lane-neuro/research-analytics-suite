"""
ProjectManagerDialog Module.

This module defines the ProjectManagerDialog class, which is responsible for managing the dialog for creating, loading, 
and saving projects within the neurobehavioral analytics suite. It initializes the project manager dialog, handles 
project creation, loading, and saving operations, and provides the necessary GUI elements.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

import dearpygui.dearpygui as dpg
import asyncio
from neurobehavioral_analytics_suite.data_engine.project.load_project import load_project
from neurobehavioral_analytics_suite.data_engine.project.save_project import save_project
from neurobehavioral_analytics_suite.data_engine.UnifiedDataEngine import DataEngine
from neurobehavioral_analytics_suite.operation_manager.OperationControl import OperationControl
from neurobehavioral_analytics_suite.operation_manager.operations.project.CreateProjectOperation import (
    CreateProjectOperation)
from neurobehavioral_analytics_suite.operation_manager.operations.project.LoadProjectOperation import (
    LoadProjectOperation)
from neurobehavioral_analytics_suite.operation_manager.operations.project.SaveProjectOperation import (
    SaveProjectOperation)


class ProjectManagerDialog:
    """A class to manage the dialog for creating, loading, and saving projects."""

    def __init__(self, data_engine: DataEngine, operation_control: OperationControl):
        """
        Initializes the ProjectManagerDialog with the given data engine and operations control.

        Args:
            data_engine (DataEngine): Instance to manage project data.
            operation_control (OperationControl): Control interface for operations.
        """
        self.window = dpg.add_window(label="Project Manager")
        dpg.add_button(label="Create Project", callback=self.create_project_wrapper, parent=self.window)
        dpg.add_button(label="Load Project", callback=self.load_project_wrapper, parent=self.window)
        dpg.add_button(label="Save Project", callback=self.save_project_wrapper, parent=self.window)
        self.data_engine = data_engine
        self.operation_control = operation_control

    async def create_project(self, sender: str, data: dict) -> None:
        """
        Creates a new project.

        Args:
            sender (str): The sender of the create project event.
            data (dict): Additional application data.
        """
        print("Creating a new project...")
        await asyncio.sleep(3)

    async def load_project(self, sender: str, data: dict) -> None:
        """
        Loads an existing project.

        Args:
            sender (str): The sender of the load project event.
            data (dict): Additional application data.
        """
        file_path = dpg.open_file_dialog(directory='.', extensions='.json')
        if file_path:
            self.data_engine = load_project(file_path[0])
            print(f"Loaded project from {file_path[0]}")

    async def save_project(self, sender: str, data: dict) -> None:
        """
        Saves the current project.

        Args:
            sender (str): The sender of the save project event.
            data (dict): Additional application data.
        """
        if self.data_engine:
            file_path = dpg.save_file_dialog(directory='.', extensions='.json')
            if file_path:
                save_project(self.data_engine, file_path[0])
                print(f"Saved project to {file_path[0]}")
        else:
            print("No project to save")

    def create_project_wrapper(self, sender: str, data: dict) -> None:
        """
        Wrapper to create a project operations.

        Args:
            sender (str): The sender of the create project event.
            data (dict): Additional application data.
        """
        CreateProjectOperation(self.operation_control.error_handler, self.data_engine)

    def load_project_wrapper(self, sender: str, data: dict) -> None:
        """
        Wrapper to load a project operations.

        Args:
            sender (str): The sender of the load project event.
            data (dict): Additional application data.
        """
        LoadProjectOperation(self.operation_control.error_handler, self.data_engine)

    def save_project_wrapper(self, sender: str, data: dict) -> None:
        """
        Wrapper to save a project operations.

        Args:
            sender (str): The sender of the save project event.
            data (dict): Additional application data.
        """
        SaveProjectOperation(self.operation_control.error_handler, self.data_engine)

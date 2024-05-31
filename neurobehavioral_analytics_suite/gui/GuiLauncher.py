"""
This is the GuiLauncher module.

This module is responsible for launching the GUI of the NeuroBehavioral Analytics Suite. It initializes the necessary
classes and starts the DearPyGui event loop, keeping it running until the DearPyGui window is closed.

Author: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

import asyncio
import dearpygui.dearpygui as dpg
from dearpygui_async import DearPyGuiAsync

from neurobehavioral_analytics_suite.data_engine.DataEngine import DataEngine
from neurobehavioral_analytics_suite.gui.ConsoleDialog import ConsoleDialog
from neurobehavioral_analytics_suite.gui.OperationManagerDialog import OperationManagerDialog
from neurobehavioral_analytics_suite.gui.ProjectManagerDialog import ProjectManagerDialog
from neurobehavioral_analytics_suite.gui.ResourceMonitorDialog import ResourceMonitorDialog
from neurobehavioral_analytics_suite.operation_manager.OperationControl import OperationControl
from neurobehavioral_analytics_suite.operation_manager.operation.Operation import Operation


class GuiLauncher:
    """A class used to launch the GUI of the NeuroBehavioral Analytics Suite.

    Attributes:
        resource_monitor (ResourceMonitorDialog): An instance of the ResourceMonitorGui class.
        console (ConsoleDialog): An instance of the ConsoleDialog class.
        operation_window (OperationManagerDialog): An instance of the OperationManagerGui class.
        project_manager (ProjectManagerDialog): An instance of the ProjectManagerDialog class.
        dpg_async (DearPyGuiAsync): An instance of the DearPyGuiAsync class.
    """

    def __init__(self, data_engine: DataEngine, operation_control: OperationControl, logger):
        """Initializes the GuiLauncher with instances of the necessary classes."""
        self.logger = logger
        self.operation_control = operation_control
        self.data_engine = data_engine
        self.resource_monitor = None
        self.console = None
        self.operation_window = None
        self.project_manager = None

        self.update_operations = []

        self.dpg_async = DearPyGuiAsync()

    def generate_layout(self):
        """Generates a grid-like layout for all subwindows."""
        window_width, window_height = dpg.get_viewport_width() // 2 - 10, dpg.get_viewport_height() // 2 - 10

        # Set the position and size of each subwindow
        dpg.configure_item(self.project_manager.window, pos=(0, 0), width=window_width,
                           height=window_height)
        dpg.configure_item(self.operation_window.window, pos=(window_width, 0), width=window_width,
                           height=window_height)
        dpg.configure_item(self.console.window, pos=(0, window_height), width=window_width,
                           height=window_height)
        dpg.configure_item(self.resource_monitor.window, pos=(window_width, window_height), width=window_width,
                           height=window_height)

        self.resource_monitor.update_layout()

    async def launch(self):
        """Launches the GUI.

        This method sets up the DearPyGui context, creates the viewport, sets up DearPyGui,
        initializes the GUI components, and starts the DearPyGui event loop. It keeps the event
        loop running until the DearPyGui window is closed.
        """
        dpg.create_context()
        dpg.create_viewport()
        dpg.setup_dearpygui()

        self.project_manager = ProjectManagerDialog(self.data_engine, self.operation_control)
        self.console = ConsoleDialog(self.operation_control.user_input_handler, self.operation_control, self,
                                     self.logger)
        self.resource_monitor = ResourceMonitorDialog(self.operation_control, self, self.logger)
        self.operation_window = OperationManagerDialog(self.operation_control)

        dpg.show_viewport()
        self.generate_layout()

        await self.dpg_async.start()

        await self.console.initialize()
        await self.console.update_operation.execute()

        await self.resource_monitor.initialize()
        await self.resource_monitor.update_operation.execute()

        # Keep the event loop running until the DearPyGui window is closed
        while dpg.is_dearpygui_running():
            await asyncio.sleep(0.01)

        dpg.destroy_context()

"""
GUILauncher Module.

This module defines the GuiLauncher class, which is responsible for launching the GUI for the NeuroBehavioral Analytics
Suite. It sets up various panes, including data analysis, visualization, and operation management, and handles the
navigation between these panes.

Author: Lane
Copyright: Lane
Credits: Lane
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
from neurobehavioral_analytics_suite.operation_manager.OperationControl import OperationControl
from neurobehavioral_analytics_suite.utils.Logger import Logger


class GuiLauncher:
    """Class to launch the GUI for the NeuroBehavioral Analytics Suite."""

    def __init__(self, data_engine: DataEngine, operation_control: OperationControl, logger: Logger):
        """
        Initializes the GUI launcher with necessary components.

        Args:
            data_engine (DataEngine): The data engine for handling data operation.
            operation_control (OperationControl): The control manager for operations.
            logger (Logger): The logger for logging information and errors.
        """
        self.logger = logger
        self.operation_control = operation_control
        self.data_engine = data_engine
        self.resource_monitor = None
        self.console = None
        self.operation_window = None
        self.project_manager = None
        self.update_operations = []
        self.dpg_async = DearPyGuiAsync()

    def setup_navigation_menu(self) -> None:
        """Sets up the navigation menu on the left pane."""
        with dpg.group(parent="left_pane"):
            dpg.add_button(label="Import Data", callback=lambda: self.switch_pane("import_data"))
            dpg.add_button(label="Operation Manager", callback=lambda: self.switch_pane("operation"))
            dpg.add_button(label="Analyze Data", callback=lambda: self.switch_pane("analyze_data"))
            dpg.add_button(label="Visualize Data", callback=lambda: self.switch_pane("visualize_data"))
            dpg.add_button(label="Manage Projects", callback=lambda: self.switch_pane("manage_projects"))
            dpg.add_button(label="Reports", callback=lambda: self.switch_pane("reports"))
            dpg.add_button(label="Settings", callback=lambda: self.switch_pane("settings"))

    def switch_pane(self, pane_name: str) -> None:
        """
        Switches between different panes in the GUI.

        Args:
            pane_name (str): The name of the pane to switch to.
        """
        # Hide all panes first
        for pane in ["import_data_pane", "operation_pane", "analyze_data_pane", "visualize_data_pane",
                     "manage_projects_pane", "reports_pane", "settings_pane"]:
            dpg.configure_item(pane, show=False)

        # Show the selected pane
        dpg.configure_item(f"{pane_name}_pane", show=True)

    async def setup_data_analysis_pane(self) -> None:
        """Sets up the data analysis pane asynchronously."""
        with dpg.group(parent="analyze_data_pane"):
            dpg.add_text("Data Analysis Tools")
            # Add more widgets for data analysis

    async def setup_visualization_pane(self) -> None:
        """Sets up the data visualization pane asynchronously."""
        with dpg.group(parent="visualize_data_pane"):
            dpg.add_text("Data Visualization Tools")
            # Add more widgets for data visualization

    async def setup_console_log_viewer(self) -> None:
        """Sets up the console/log viewer asynchronously."""
        with dpg.group(parent="bottom_pane"):
            dpg.add_text("Console/Log Output", tag="console_log_output")

        self.console = ConsoleDialog(self.operation_control.user_input_handler, self.operation_control, self.logger)
        await self.console.initialize()

    async def setup_operation_pane(self) -> None:
        """Sets up the operations pane asynchronously."""
        with dpg.group(parent="operation_pane"):
            dpg.add_text("Operation Manager")

        self.operation_window = OperationManagerDialog(self.operation_control, self.logger)
        await self.operation_window.initialize()

    async def setup_panes(self) -> None:
        """Sets up all the panes asynchronously."""
        with dpg.child_window(tag="import_data_pane", parent="right_pane", show=True):
            dpg.add_text("Import Data Pane")

        with dpg.child_window(tag="operation_pane", parent="right_pane", show=False):
            await self.setup_operation_pane()

        with dpg.child_window(tag="analyze_data_pane", parent="right_pane", show=False):
            await self.setup_data_analysis_pane()

        with dpg.child_window(tag="visualize_data_pane", parent="right_pane", show=False):
            await self.setup_visualization_pane()

        with dpg.child_window(tag="manage_projects_pane", parent="right_pane", show=False):
            dpg.add_text("Manage Projects Pane")

        with dpg.child_window(tag="reports_pane", parent="right_pane", show=False):
            dpg.add_text("Reports Pane")

        with dpg.child_window(tag="settings_pane", parent="right_pane", show=False):
            dpg.add_text("Settings Pane")

    async def setup_main_window(self) -> None:
        """Sets up the main window of the GUI and runs the event loop."""
        dpg.create_context()
        dpg.create_viewport(title='NeuroBehavioral Analytics Suite', width=1920, height=1080)
        dpg.setup_dearpygui()

        dpg.show_viewport()
        await self.dpg_async.start()

        with dpg.window(label="NBAS", tag="main_window"):
            with dpg.group(horizontal=True, tag="main_pane", height=dpg.get_viewport_height() - 370):
                with dpg.child_window(tag="left_pane", width=200):
                    self.setup_navigation_menu()

                with dpg.child_window(tag="right_pane"):
                    await self.setup_panes()

            with dpg.child_window(tag="bottom_pane", height=300, parent="main_window"):
                await self.setup_console_log_viewer()

        dpg.set_primary_window("main_window", True)

        # Keep the event loop running until the DearPyGui window is closed
        while dpg.is_dearpygui_running():
            await asyncio.sleep(0.01)

        dpg.destroy_context()

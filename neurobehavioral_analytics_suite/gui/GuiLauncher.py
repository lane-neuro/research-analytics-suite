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
import os

import dearpygui.dearpygui as dpg
from dearpygui_async import DearPyGuiAsync
from neurobehavioral_analytics_suite.data_engine.DataEngineOptimized import DataEngineOptimized
from neurobehavioral_analytics_suite.gui.ConsoleDialog import ConsoleDialog
from neurobehavioral_analytics_suite.gui.DataEngineDialog import DataEngineDialog
from neurobehavioral_analytics_suite.gui.DataImportWizard import DataImportWizard
from neurobehavioral_analytics_suite.gui.OperationManagerDialog import OperationManagerDialog
from neurobehavioral_analytics_suite.gui.RealTimeDataVisualization import RealTimeDataVisualization
from neurobehavioral_analytics_suite.gui.SettingsDialog import SettingsDialog
from neurobehavioral_analytics_suite.operation_manager.OperationControl import OperationControl
from neurobehavioral_analytics_suite.utils.CustomLogger import CustomLogger
from neurobehavioral_analytics_suite.data_engine.live_input.LiveDataHandler import LiveDataHandler
from neurobehavioral_analytics_suite.data_engine.Workspace import Workspace


class GuiLauncher:
    """Class to launch the GUI for the NeuroBehavioral Analytics Suite."""

    def __init__(self, data_engine: DataEngineOptimized, operation_control: OperationControl, workspace: Workspace):
        """
        Initializes the GUI launcher with necessary components.

        Args:
            data_engine (DataEngineOptimized): The data engine for handling data operation.
            operation_control (OperationControl): The control manager for operations.
            workspace (Workspace): The workspace manager for saving and loading workspaces.
        """
        self.dpg_async = DearPyGuiAsync()
        self._logger = CustomLogger()
        self.operation_control = operation_control
        self.data_engine = data_engine
        self.workspace = workspace
        self.visualization_dialog = None
        self.data_engine_dialog = None
        self.data_import_wizard = None
        self.real_time_data_visualization = None
        self.settings_dialog = SettingsDialog()
        self.console = None
        self.operation_window = None

        # Initialize live data handler
        self.data_engine.live_data_handler = LiveDataHandler(data_engine)

    def setup_navigation_menu(self) -> None:
        """Sets up the navigation menu on the left pane."""
        with dpg.group(parent="left_pane"):
            dpg.add_button(label="Operation Manager", callback=lambda: self.switch_pane("operation"))
            dpg.add_button(label="Analyze Data", callback=lambda: self.switch_pane("analyze_data"))
            dpg.add_button(label="Visualize Data", callback=lambda: self.switch_pane("visualize_data"))
            dpg.add_button(label="Manage Projects", callback=lambda: self.switch_pane("manage_projects"))
            dpg.add_button(label="Reports", callback=lambda: self.switch_pane("reports"))
            dpg.add_button(label="Settings", callback=lambda: self.switch_pane("settings"))
            dpg.add_button(label="Save Workspace", callback=self.save_workspace)
            dpg.add_button(label="Configuration", callback=self.settings_dialog.show)

    def switch_pane(self, pane_name: str) -> None:
        """
        Switches between different panes in the GUI.

        Args:
            pane_name (str): The name of the pane to switch to.
        """
        # Hide all panes first
        for pane in ["operation_pane", "analyze_data_pane", "visualize_data_pane",
                     "manage_projects_pane", "reports_pane", "settings_pane"]:
            dpg.configure_item(pane, show=False)

        # Show the selected pane
        dpg.configure_item(f"{pane_name}_pane", show=True)

    def apply_theme(self):
        """Applies the custom theme to the GUI and loads fonts dynamically."""
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                # dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (30, 30, 30))
                # dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255))
                # dpg.add_theme_color(dpg.mvThemeCol_Button, (50, 50, 150))
                # dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (70, 70, 170))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (90, 90, 190))
                # Add more theme settings as needed

        dpg.bind_theme(global_theme)

        # Load and set custom fonts
        font_paths = []
        for root, _, files in os.walk("fonts"):
            for file in files:
                if file.endswith(".ttf"):
                    font_paths.append(os.path.join(root, file))

        with dpg.font_registry():
            default_font = None
            for font_path in font_paths:
                font = dpg.add_font(font_path, 20)
                if default_font is None:
                    default_font = font

            # Set default font
            if default_font is not None:
                dpg.bind_font(default_font)

    async def setup_main_window(self) -> None:
        """Sets up the main window of the GUI and runs the event loop."""
        dpg.create_context()
        dpg.create_viewport(title='NeuroBehavioral Analytics Suite', width=1920, height=1080)
        dpg.setup_dearpygui()
        self.apply_theme()  # Apply theme after setup

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

    async def setup_panes(self) -> None:
        """Sets up all the panes asynchronously."""
        with dpg.child_window(tag="operation_pane", parent="right_pane", show=True):
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

    async def setup_data_analysis_pane(self) -> None:
        """Sets up the data analysis pane asynchronously."""
        with dpg.group(parent="analyze_data_pane"):
            dpg.add_text("Data Analysis Tools")
            # Add more widgets for data analysis

    async def setup_visualization_pane(self) -> None:
        """Sets up the data visualization pane asynchronously."""
        with dpg.group(parent="visualize_data_pane"):
            dpg.add_text("Data Visualization Tools")

    async def setup_console_log_viewer(self) -> None:
        """Sets up the console/log viewer asynchronously."""
        with dpg.group(parent="bottom_pane"):
            dpg.add_text("Console/Log Output", tag="console_log_output")

        self.console = ConsoleDialog(self.operation_control.user_input_manager, self.operation_control)
        await self.console.initialize()

    async def setup_operation_pane(self) -> None:
        """Sets up the operations pane asynchronously."""
        with dpg.group(parent="operation_pane"):
            dpg.add_text("Operation Manager")

        self.operation_window = OperationManagerDialog(self.operation_control, dpg.get_item_width("operation_pane"))
        await self.operation_window.initialize_dialog()

    async def setup_data_engine_pane(self) -> None:
        """Sets up the data engine pane asynchronously."""
        with dpg.group(parent="import_data_pane"):
            dpg.add_text("Data Engine")
            self.data_engine_dialog = DataEngineDialog(self.data_engine)
            await self.data_engine_dialog.initialize()

    async def setup_data_import_wizard_pane(self) -> None:
        """Sets up the data import wizard pane asynchronously."""
        with dpg.group(parent="data_import_pane"):
            dpg.add_text("Data Import Wizard")
            self.data_import_wizard = DataImportWizard(self.data_engine)
            await self.data_import_wizard.initialize()

    def save_workspace(self):
        """
        Saves the current workspace, including data, configuration settings, and user information.
        """
        workspace_name = dpg.get_value("workspace_name_input")
        if workspace_name is None or workspace_name == "":
            workspace_name = "default_name"
        self.workspace.save_current_workspace()
        # dpg.set_value("workspace_status", f"Workspace '{workspace_name}' saved successfully")
        self._logger.info(f"Workspace '{workspace_name}' saved successfully")

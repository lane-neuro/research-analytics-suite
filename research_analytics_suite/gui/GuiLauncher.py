"""
GUILauncher Module.

This module defines the GuiLauncher class, which is responsible for launching the GUI for the Research Analytics
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
import ctypes
import os

import dearpygui.dearpygui as dpg
from dearpygui_async import DearPyGuiAsync

from research_analytics_suite.data_engine.DataEngineOptimized import DataEngineOptimized
from research_analytics_suite.data_engine.Workspace import Workspace
from research_analytics_suite.gui.ConsoleDialog import ConsoleDialog
from research_analytics_suite.gui.DataEngineDialog import DataEngineDialog
from research_analytics_suite.gui.DataImportWizard import DataImportWizard
from research_analytics_suite.gui.OperationManagerDialog import OperationManagerDialog
from research_analytics_suite.gui.SettingsDialog import SettingsDialog
from research_analytics_suite.gui.modules.CreateOperationModule import CreateOperationModule
from research_analytics_suite.gui.modules.TimelineModule import TimelineModule
from research_analytics_suite.gui.modules.WorkspaceModule import WorkspaceModule
from research_analytics_suite.operation_manager.OperationControl import OperationControl
from research_analytics_suite.utils.CustomLogger import CustomLogger


class GuiLauncher:
    """Class to launch the GUI for the Research Analytics Suite."""

    def __init__(self, data_engine: DataEngineOptimized, operation_control: OperationControl):
        """
        Initializes the GUI launcher with necessary components.

        Args:
            data_engine (DataEngineOptimized): The data engine for handling data operation.
            operation_control (OperationControl): The control manager for operations.
        """
        self.timeline = None
        self.dpg_async = DearPyGuiAsync()
        self._logger = CustomLogger()
        self.operation_control = operation_control
        self.data_engine = data_engine
        self.workspace = Workspace()
        self.visualization_dialog = None
        self.data_engine_dialog = None
        self.data_import_wizard = None
        self.real_time_data_visualization = None
        self.settings_dialog = SettingsDialog()
        self.create_operation_module = CreateOperationModule(operation_control=self.operation_control,
                                                             height=400, width=800,
                                                             parent_operation=None)
        self.console = None
        self.operation_window = None
        self.workspace_dialog = None

    def setup_navigation_menu(self) -> None:
        """Sets up the navigation menu on the left pane."""
        with dpg.group(parent="left_pane"):
            dpg.add_button(label="Operation Manager", callback=lambda: self.switch_pane("operation"))
            dpg.add_button(label="Analyze Data", callback=lambda: self.switch_pane("analyze_data"))
            dpg.add_button(label="Visualize Data", callback=lambda: self.switch_pane("visualize_data"))
            dpg.add_button(label="Manage Projects", callback=lambda: self.switch_pane("manage_projects"))
            dpg.add_button(label="Reports", callback=lambda: self.switch_pane("reports"))
            dpg.add_button(label="Settings", callback=lambda: self.switch_pane("settings"))
            dpg.add_button(label="Configuration", callback=self.settings_dialog.show)
            dpg.add_button(label="Console/Log", callback=lambda: self.switch_pane("console_log_output"))
            dpg.add_button(label="Exit", callback=dpg.stop_dearpygui)

    def switch_pane(self, pane_name: str) -> None:
        """
        Switches between different panes in the GUI.

        Args:
            pane_name (str): The name of the pane to switch to.
        """
        # Hide all panes first
        for pane in ["operation_pane", "analyze_data_pane", "visualize_data_pane",
                     "manage_projects_pane", "reports_pane", "settings_pane", "console_log_output_pane"]:
            dpg.configure_item(pane, show=False)

        # Show the selected pane
        dpg.configure_item(f"{pane_name}_pane", show=True)

    async def apply_theme(self):
        """Applies the custom theme to the GUI and loads fonts dynamically."""
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (90, 90, 190))

        dpg.bind_theme(global_theme)

        font_paths = []
        font_directory = "gui/fonts"

        if os.path.exists(font_directory) and os.path.isdir(font_directory):
            for root, _, files in os.walk(font_directory):
                for file in files:
                    if file.endswith(".ttf"):
                        font_paths.append(os.path.join(root, file))
        else:
            self._logger.error(Exception(f"Font directory {font_directory} does not exist."), self)

        await self.load_fonts(font_paths)

    async def load_fonts(self, font_paths):
        with dpg.font_registry():
            default_font = None
            self._logger.info(f"Loading {len(font_paths)} fonts")

            for font_path in font_paths:
                try:
                    if "OpenSans-Regular.ttf" in font_path:
                        font = dpg.add_font(font_path, 16)
                        default_font = font
                        dpg.set_global_font_scale(1.0)
                    await asyncio.sleep(0)  # Yield control to the event loop
                except Exception as e:
                    self._logger.error(Exception(f"Failed to load font {font_path}: {e}"), self)

            if default_font is not None:
                dpg.bind_font(default_font)
                self._logger.info(f"Font set: {default_font}")
            else:
                self._logger.error(Exception("No default font found, using DearPyGui's default font."), self)

            # dpg.show_font_manager()

    async def setup_main_window(self) -> None:
        """Sets up the main window of the GUI and runs the event loop."""
        dpg.create_context()
        dpg.create_viewport(title='Research Analytics Suite', width=1920, height=1080)
        dpg.setup_dearpygui()
        await self.apply_theme()  # Apply theme after setup
        dpg.show_metrics()

        dpg.show_viewport()
        await self.dpg_async.start()

        with dpg.window(label="RAS", tag="main_window",
                        width=dpg.get_viewport_width(), height=dpg.get_viewport_height()):
            with dpg.group(horizontal=True, tag="main_pane", height=dpg.get_viewport_height() - 370):
                with dpg.child_window(tag="left_pane", width=200):
                    self.setup_navigation_menu()

                with dpg.child_window(tag="right_pane"):
                    await self.setup_panes()

            with dpg.child_window(tag="bottom_pane", parent="main_window"):
                with dpg.group(horizontal=True, tag="bottom_pane_group"):
                    await self.setup_timeline_pane()
                    await self.setup_workspace_pane()

        dpg.set_primary_window("main_window", True)

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

        with dpg.child_window(tag="console_log_output_pane", parent="right_pane", show=False):
            await self.setup_console_log_viewer_pane()

    async def setup_data_analysis_pane(self) -> None:
        """Sets up the data analysis pane asynchronously."""
        with dpg.group(parent="analyze_data_pane"):
            dpg.add_text("Data Analysis Tools")

    async def setup_visualization_pane(self) -> None:
        """Sets up the data visualization pane asynchronously."""
        with dpg.group(parent="visualize_data_pane"):
            dpg.add_text("Data Visualization Tools")

    async def setup_console_log_viewer_pane(self) -> None:
        """Sets up the console/log viewer asynchronously."""
        with dpg.group(parent="console_log_output_pane"):
            dpg.add_text("Console/Log Output", tag="console_log_output")

        self.console = ConsoleDialog(self.operation_control.user_input_manager, self.operation_control)
        await self.console.initialize()

    async def setup_operation_pane(self) -> None:
        """Sets up the operations pane asynchronously."""
        with dpg.group(parent="operation_pane", horizontal=True):
            dpg.add_text("Operation Manager")
            self.create_operation_module.draw_button(parent="operation_pane", label="Create New Operation")

        self.operation_window = OperationManagerDialog(operation_control=self.operation_control)
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

    async def setup_timeline_pane(self) -> None:
        """Sets up the timeline pane asynchronously."""
        with dpg.group(parent="bottom_pane_group", tag="timeline_group", horizontal=True):
            self.timeline = TimelineModule(width=int(dpg.get_viewport_width() * 0.5),
                                           height=300,
                                           operation_control=self.operation_control,
                                           operation_queue=self.operation_control.queue)
            await self.timeline.initialize_dialog()

    async def setup_workspace_pane(self) -> None:
        """Sets up the workspace pane asynchronously."""
        with dpg.group(parent="bottom_pane_group", horizontal=True, tag="workspace_group"):
            self.workspace_dialog = WorkspaceModule(operation_control=self.operation_control,
                                                    height=300, width=int(dpg.get_viewport_width() * 0.5))
            await self.workspace_dialog.initialize()
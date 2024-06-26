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
import os

import dearpygui.dearpygui as dpg
from dearpygui_async import DearPyGuiAsync
from research_analytics_suite.data_engine.Workspace import Workspace
from research_analytics_suite.gui.dialogs.management.ResourceMonitorDialog import ResourceMonitorDialog
from research_analytics_suite.gui.dialogs.data_handling.CollectionViewDialog import CollectionViewDialog
from research_analytics_suite.gui.dialogs.management.ConsoleDialog import ConsoleDialog
from research_analytics_suite.gui.dialogs.management.OperationManagerDialog import OperationManagerDialog
from research_analytics_suite.gui.dialogs.settings.SettingsDialog import SettingsDialog
from research_analytics_suite.gui.modules.TimelineModule import TimelineModule
from research_analytics_suite.gui.modules.WorkspaceModule import WorkspaceModule
from research_analytics_suite.operation_manager.control.OperationControl import OperationControl
from research_analytics_suite.utils.CustomLogger import CustomLogger
from research_analytics_suite.gui.dialogs.management.PlanningDialog import PlanningDialog
from research_analytics_suite.gui.dialogs.data_handling.AnalyzeDataDialog import AnalyzeDataDialog
from research_analytics_suite.gui.dialogs.visualization.VisualizeDataDialog import VisualizeDataDialog
from research_analytics_suite.gui.dialogs.management.ProjectManagerDialog import ProjectManagerDialog
from research_analytics_suite.gui.dialogs.management.ReportsDialog import ReportsDialog


class GuiLauncher:
    """Class to launch the GUI for the Research Analytics Suite."""

    def __init__(self):
        """
        Initializes the GUI launcher with necessary components.
        """
        self._dpg_async = DearPyGuiAsync()

        self._logger = CustomLogger()
        self._operation_control = OperationControl()
        self._workspace = Workspace()

        self._timeline_dialog = None
        self._visualization_dialog = None
        self._data_engine_dialog = None
        self._data_import_wizard = None
        self._real_time_data_dialog = None
        self._settings_dialog = None
        self._console_dialog = None
        self._operation_window = None
        self._workspace_dialog = None
        self._collection_view_dialog = None
        self._visualize_data_dialog = None
        self._resource_monitor_dialog = None
        self._reports_dialog = None
        self._manage_project_dialog = None
        self._planning_dialog = None
        self._analyze_data_dialog = None

    async def setup_navigation_menu(self) -> None:
        """Sets up the navigation menu on the left pane."""
        with dpg.group(parent="left_pane"):
            dpg.add_button(label="Planning", callback=lambda: self.switch_pane("planning"))
            dpg.add_button(label="Data Collection", callback=lambda: self.switch_pane("data_collection"))
            dpg.add_button(label="Data Analysis", callback=lambda: self.switch_pane("analyze_data"))
            dpg.add_button(label="Data Visualization", callback=lambda: self.switch_pane("visualize_data"))
            dpg.add_button(label="Project Management", callback=lambda: self.switch_pane("manage_projects"))
            dpg.add_button(label="Reports", callback=lambda: self.switch_pane("reports"))
            dpg.add_button(label="Configuration", callback=self.settings_popup)
            dpg.add_button(label="Logs", callback=lambda: self.switch_pane("console_log_output"))
            dpg.add_button(label="Exit", callback=dpg.stop_dearpygui)

    def switch_pane(self, pane_name: str) -> None:
        """
        Switches between different panes in the GUI.

        Args:
            pane_name (str): The name of the pane to switch to.
        """
        # Hide all panes first
        for pane in ["planning_pane",
                     "data_collection_pane",
                     "analyze_data_pane",
                     "visualize_data_pane",
                     "manage_projects_pane",
                     "reports_pane",
                     "settings_pane",
                     "console_log_output_pane"]:
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
        font_directory = "gui/assets/fonts"

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
            else:
                self._logger.error(Exception("No default font found, using DearPyGui's default font."), self)

    async def setup_main_window(self) -> None:
        """Sets up the main window of the GUI and runs the event loop."""
        dpg.create_context()
        dpg.create_viewport(title='Research Analytics Suite - Main Window', width=1366, height=768,
                            large_icon="gui/assets/images/logo_extra_large_dark.ico",
                            small_icon="gui/assets/images/logo_large_icon_dark.ico")
        dpg.setup_dearpygui()
        await self.apply_theme()  # Apply theme after setup
        # dpg.show_metrics()

        dpg.show_viewport()
        await self._dpg_async.start()

        with dpg.window(label="Research Analytics Suite", tag="main_window",
                        width=dpg.get_viewport_width(), height=dpg.get_viewport_height()):
            with dpg.group(horizontal=True, tag="main_pane", height=dpg.get_viewport_height() - 300):
                with dpg.child_window(tag="left_pane", width=180):
                    await self.setup_navigation_menu()

                with dpg.child_window(tag="middle_pane", width=int(dpg.get_viewport_width() * 0.50)):
                    await self.setup_panes()

                with dpg.child_window(tag="right_pane", width=-1):
                    await self.setup_operation_pane()

            with dpg.child_window(tag="bottom_pane", parent="main_window", width=-1):
                with dpg.group(horizontal=True, tag="bottom_pane_group"):
                    await self.setup_workspace_pane()

                    await self.setup_timeline_module()

                    with dpg.child_window(tag="resource_monitor_pane", width=-1,
                                          pos=(dpg.get_viewport_width() - 640, 8)):
                        dpg.add_text("Resource Monitor")
                        with dpg.group(horizontal=True, tag="resource_monitor_group"):
                            self._resource_monitor_dialog = ResourceMonitorDialog(width=-1, height=-1,
                                                                                  parent="resource_monitor_group")
                            await self._resource_monitor_dialog.initialize_gui()
                            self._resource_monitor_dialog.draw()

        dpg.set_primary_window("main_window", True)

        while dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()
            await asyncio.sleep(0.01)

        self._logger.info("Shutting down GUI...")
        await self._workspace.save_current_workspace()
        dpg.destroy_context()

    async def setup_panes(self) -> None:
        """Sets up asynchronous panes."""
        with dpg.child_window(tag="planning_pane", parent="middle_pane", show=True):
            self._planning_dialog = PlanningDialog(width=-1, height=-1, parent="planning_pane")
            await self._planning_dialog.initialize_gui()
            self._planning_dialog.draw()

        with dpg.child_window(tag="data_collection_pane", parent="middle_pane", show=False):
            await self.setup_data_collection_pane()
            self._collection_view_dialog.draw()

        with dpg.child_window(tag="analyze_data_pane", parent="middle_pane", show=False):
            self._analyze_data_dialog = AnalyzeDataDialog(width=800, height=600, parent="analyze_data_pane")
            await self._analyze_data_dialog.initialize_gui()
            self._analyze_data_dialog.draw()

        with dpg.child_window(tag="visualize_data_pane", parent="middle_pane", show=False):
            self._visualize_data_dialog = VisualizeDataDialog(width=-1, height=-1, parent="visualize_data_pane")
            await self._visualize_data_dialog.initialize_gui()
            self._visualize_data_dialog.draw()

        with dpg.child_window(tag="manage_projects_pane", parent="middle_pane", show=False):
            self._manage_project_dialog = ProjectManagerDialog(width=-1, height=-1, parent="manage_projects_pane")
            await self._manage_project_dialog.initialize_gui()
            self._manage_project_dialog.draw()

        with dpg.child_window(tag="reports_pane", parent="middle_pane", show=False):
            self._reports_dialog = ReportsDialog(width=-1, height=-1, parent="reports_pane")
            await self._reports_dialog.initialize_gui()
            self._reports_dialog.draw()

        with dpg.child_window(tag="settings_pane", parent="middle_pane", show=False):
            dpg.add_text("Settings Pane")

        with dpg.child_window(tag="console_log_output_pane", parent="middle_pane", show=False):
            await self.setup_console_log_viewer_pane()

    async def setup_operation_pane(self) -> None:
        """Sets up the operation pane."""
        self._operation_window = OperationManagerDialog(width=dpg.get_item_width("right_pane"), height=-1,
                                                        parent="right_pane")
        await self._operation_window.initialize_gui()
        self._operation_window.draw()

    async def setup_console_log_viewer_pane(self) -> None:
        """Sets up the console/log viewer."""
        with dpg.group(parent="console_log_output_pane"):
            dpg.add_text("Console/Log Output", tag="console_log_output")

        self._console_dialog = ConsoleDialog(self._operation_control.user_input_manager,
                                             parent="console_log_output_pane",
                                             width=-1, height=-1)
        await self._console_dialog.initialize_gui()
        self._console_dialog.draw()

    async def setup_workspace_pane(self) -> None:
        """Sets up the workspace pane."""
        with dpg.group(parent="bottom_pane_group", horizontal=True, tag="workspace_group"):
            self._workspace_dialog = WorkspaceModule(height=-1,
                                                     width=int(dpg.get_viewport_width() * 0.5),
                                                     parent="bottom_pane_group")
            await self._workspace_dialog.initialize_gui()
            self._workspace_dialog.draw()

    async def setup_data_collection_pane(self) -> None:
        """Sets up the data collection pane."""
        with dpg.group(parent="data_collection_pane"):
            self._collection_view_dialog = CollectionViewDialog(width=800, height=600, parent="data_collection_pane")
            dpg.add_text("Data Collection Tools")
            await self._collection_view_dialog.initialize_gui()

    async def settings_popup(self) -> None:
        """Sets up the settings popup."""
        self._settings_dialog = SettingsDialog(width=800, height=600, parent=None)
        await self._settings_dialog.initialize_gui()
        self._settings_dialog.draw()

    async def setup_timeline_module(self) -> None:
        """Sets up the timeline module."""
        self._timeline_dialog = TimelineModule(width=800, height=-1, parent="bottom_pane_group",
                                               operation_sequencer=self._operation_control.sequencer)
        await self._timeline_dialog.initialize_gui()
        self._timeline_dialog.draw()

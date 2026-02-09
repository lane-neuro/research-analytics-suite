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
from research_analytics_suite.data_engine import Workspace
from research_analytics_suite.gui.NodeEditorManager import NodeEditorManager
from research_analytics_suite.gui.dialogs.info.HardwareDialog import HardwareDialog
from research_analytics_suite.gui.dialogs.info.LibraryPane import LibraryPane
from research_analytics_suite.gui.dialogs.info.ResourceMonitorDialog import ResourceMonitorDialog
from research_analytics_suite.gui.dialogs.management.DataManagementDialog import DataManagementDialog
from research_analytics_suite.gui.dialogs.management.ConsoleDialog import ConsoleDialog
from research_analytics_suite.gui.dialogs.settings.SettingsDialog import SettingsDialog
from research_analytics_suite.hardware_manager import HardwareManager
from research_analytics_suite.operation_manager.control import OperationControl
from research_analytics_suite.utils import CustomLogger
from research_analytics_suite.gui.dialogs.management.PlanningDialog import PlanningDialog
from research_analytics_suite.gui.dialogs.info.DocumentationDialog import DocumentationDialog
from research_analytics_suite.gui.dialogs.info.AboutDialog import AboutDialog
from research_analytics_suite.utils.Resources import resource_path
from research_analytics_suite.gui.modules import (
    notification_bus,
    NotificationPanel,
    VisualizationWorkspace,
    WorkflowPanel
)


class GuiLauncher:
    """Class to launch the GUI for the Research Analytics Suite."""

    def __init__(self, hardware_manager: HardwareManager):
        """
        Initializes the GUI launcher with necessary components.
        """
        self._dpg_async = DearPyGuiAsync()

        self._logger = CustomLogger()
        self._operation_control = OperationControl()
        self._workspace = Workspace()
        self._node_manager = NodeEditorManager()

        self._hardware_manager = hardware_manager

        # GUI relaunch control
        self._should_relaunch = False
        self._is_shutting_down = False

        self._hardware_dialog = None
        self._settings_dialog = None
        self._console_dialog = None
        self._library_pane = None
        self._collection_view_dialog = None
        self._resource_monitor_dialog = None
        self._planning_dialog = None
        self._documentation_dialog = None
        self._about_dialog = None
        self._intelligence_panel = None
        self._notification_panel = None
        self._visualization_workspace = None
        self._workflow_panel = None

        self._splitter_height = 300

    def switch_pane(self, pane_name: str) -> None:
        """
        Switches between different panes in the GUI.

        Args:
            pane_name (str): The name of the pane to switch to.
        """
        # Hide all panes first
        for pane in ["planning_pane", "console_log_output_pane"]:
            dpg.configure_item(pane, show=False)

        # Show the selected pane
        dpg.configure_item(f"{pane_name}_pane", show=True)

    async def apply_theme(self):
        """Applies the custom theme to the GUI and loads fonts dynamically."""
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (90, 90, 190))

        dpg.bind_theme(global_theme)

        font_directory = resource_path("./gui/assets/fonts")
        font_paths = []

        if font_directory.exists() and font_directory.is_dir():
            for root, _, files in os.walk(font_directory):
                for file in files:
                    if file.endswith(".ttf"):
                        font_paths.append(os.path.join(root, file))
        else:
            self._logger.error(Exception(f"Font directory {font_directory} does not exist."), self.__class__.__name__)

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
                    self._logger.error(Exception(f"Failed to load font {font_path}: {e}"), self.__class__.__name__)

            if default_font is not None:
                dpg.bind_font(default_font)
            else:
                self._logger.error(Exception("No default font found, using DearPyGui's default font."),
                                   self.__class__.__name__)

    async def setup_main_window(self) -> None:
        """Sets up the main window of the GUI and runs the event loop."""
        await self._node_manager.initialize()

        # Start notification bus
        await notification_bus.start()

        # Ensure clean context creation
        try:
            dpg.destroy_context()
        except:
            pass  # Context might not exist

        dpg.create_context()
        dpg.create_viewport(title='Research Analytics Suite - Main Window', width=1366, height=768,
                            large_icon=str(resource_path("./gui/assets/images/icon_512x512.png")),
                            small_icon=str(resource_path("./gui/assets/images/icon_32x32.png")))
        dpg.setup_dearpygui()
        await self.apply_theme()

        dpg.show_viewport()
        await self._dpg_async.start()

        with dpg.window(label="Research Analytics Suite", tag="main_window",
                        width=dpg.get_viewport_width(), height=dpg.get_viewport_height()):
            with dpg.menu_bar(tag="primary_menu_bar", parent="main_window"):
                with dpg.menu(label="File"):
                    dpg.add_menu_item(label="New Workspace", callback=self.new_workspace_dialog)
                    dpg.add_menu_item(label="Open Workspace", callback=self.open_workspace_dialog)
                    dpg.add_menu_item(label="Exit", callback=lambda: asyncio.create_task(self._exit()))

                with dpg.menu(label="Edit"):
                    dpg.add_menu_item(label="Settings", callback=self.settings_popup)

                with dpg.menu(label="View"):
                    dpg.add_menu_item(label="Hardware Monitor", callback=self.show_hardware_dialog)
                    dpg.add_menu_item(label="Resource Monitor", callback=self.show_resource_monitor)
                    dpg.add_menu_item(label="Console/Logs", callback=self.show_console)

                with dpg.menu(label="Help"):
                    dpg.add_menu_item(label="Documentation", callback=self.show_documentation)
                    dpg.add_menu_item(label="About", callback=self.show_about)

            with dpg.group(horizontal=True, tag="upper_pane_group",
                           height=dpg.get_viewport_height() - self._splitter_height - 25 - dpg.get_item_height("primary_menu_bar"),
                           horizontal_spacing=5, parent="main_window"):

                # with dpg.child_window(tag="left_pane", width=200):
                #     await self.setup_workflow_pane()

                with dpg.child_window(tag="middle_pane", width=int(dpg.get_viewport_width() - 500), border=False):
                    await self.setup_visualization_workspace()

                with dpg.child_window(tag="right_pane", width=250, border=False):
                    await self.setup_library_pane()

            with dpg.group(horizontal=True, tag="bottom_pane_group", horizontal_spacing=5, parent="main_window",
                           height=150):
                # with dpg.child_window(tag="bottom_left_pane", width=200, height=-1, border=True):
                #     await self.setup_intelligence_pane()

                with dpg.child_window(tag="bottom_middle_pane", height=-1, width=int(dpg.get_viewport_width() - 510),
                                      border=True, no_scrollbar=True):
                    await self.setup_data_collection_pane()
                    self._collection_view_dialog.draw()
                    dpg.add_button(label="vvv", callback=self.splitter_callback,
                                   tag="splitter_resize", before="slots_window")

                with dpg.child_window(tag="bottom_right_pane", width=280, height=-1, border=True):
                    await self.setup_notification_pane()

        dpg.set_primary_window("main_window", True)
        dpg.set_viewport_resize_callback(self.adjust_main_window)
        self.adjust_main_window()

        while dpg.is_dearpygui_running():
            # Check for relaunch requests
            if self._should_relaunch:
                self._logger.info("Relaunch requested, shutting down GUI...")
                await self.shutdown_gui()
                break

            dpg.render_dearpygui_frame()
            await asyncio.sleep(0.0001)

        if not self._should_relaunch:
            await self._exit()

    async def setup_workflow_pane(self) -> None:
        """Sets up the workflow checklist pane."""
        self._workflow_panel = WorkflowPanel(width=-1, height=-1, parent="left_pane")
        await self._workflow_panel.initialize_gui()
        self._workflow_panel.draw()

    async def setup_visualization_workspace(self) -> None:
        """Sets up the main visualization workspace."""
        self._visualization_workspace = VisualizationWorkspace(
            width=int(dpg.get_item_width("middle_pane")),
            height=-1,
            parent="middle_pane"
        )
        await self._visualization_workspace.initialize_gui()
        self._visualization_workspace.draw()

    async def setup_notification_pane(self) -> None:
        """Sets up the notification panel."""
        self._notification_panel = NotificationPanel(width=-1, height=-1, parent="bottom_right_pane")
        await self._notification_panel.initialize_gui()
        self._notification_panel.draw()

    async def setup_library_pane(self) -> None:
        """Sets up the library pane."""
        with dpg.child_window(tag="library_pane", width=-1, height=-1, parent="right_pane", border=False):
            self._library_pane = LibraryPane(width=-1, height=-1, parent="library_pane")
            await self._library_pane.initialize_gui()
            self._library_pane.draw()

    async def setup_console_log_viewer_pane(self) -> None:
        """Sets up the console/log viewer."""
        with dpg.group(parent="console_log_output_pane"):
            dpg.add_text("Console/Log Output", tag="console_log_output")

        self._console_dialog = ConsoleDialog(parent="console_log_output_pane", width=-1, height=-1)
        await self._console_dialog.initialize_gui()
        self._console_dialog.draw()

    async def setup_intelligence_pane(self) -> None:
        """Sets up the AI/ML Intelligence pane."""
        from research_analytics_suite.gui.modules.IntelligencePanel import IntelligencePanel
        self._intelligence_panel = IntelligencePanel(parent="bottom_left_pane", width=-1, height=-1)
        await self._intelligence_panel.initialize()
        self._intelligence_panel.draw()

    async def setup_data_collection_pane(self) -> None:
        """Sets up the data collection pane."""
        self._collection_view_dialog = DataManagementDialog(width=-1, height=-1, parent="slots_window")
        dpg.add_text("Data Management")
        await self._collection_view_dialog.initialize_gui()

    async def settings_popup(self) -> None:
        """Sets up the settings popup."""
        self._settings_dialog = SettingsDialog(width=800, height=600, parent=None)
        await self._settings_dialog.initialize_gui()
        self._settings_dialog.draw()

    async def setup_resource_monitor(self) -> None:
        """Sets up the resource monitor dialog."""
        dpg.add_text("Resource Monitor")
        dpg.add_separator()
        with dpg.group(horizontal=True, tag="resource_monitor_group"):
            self._resource_monitor_dialog = ResourceMonitorDialog(width=-1, height=-1,
                                                                  parent="resource_monitor_group")
            await self._resource_monitor_dialog.initialize_gui()
            self._resource_monitor_dialog.draw()

    def adjust_main_window(self):
        dpg.configure_item("bottom_pane_group", height=self._splitter_height)

        parent_width = dpg.get_item_configuration("main_window")["width"]
        parent_height = dpg.get_item_configuration("main_window")["height"]

        top_left_width = 0      #dpg.get_item_configuration("left_pane")["width"]
        top_right_width = dpg.get_item_configuration("right_pane")["width"]
        top_middle_width = parent_width - (top_left_width + top_right_width + 25)

        bottom_left_width = 0       #dpg.get_item_configuration("bottom_left_pane")["width"]
        bottom_right_width = dpg.get_item_configuration("bottom_right_pane")["width"]
        bottom_middle_width = parent_width - (bottom_left_width + bottom_right_width + 25)

        bottom_height = dpg.get_item_configuration("bottom_pane_group")["height"]
        top_middle_height = parent_height - bottom_height - dpg.get_item_height("primary_menu_bar") - 25

        dpg.configure_item("middle_pane", width=top_middle_width)
        dpg.configure_item("upper_pane_group", height=top_middle_height)
        dpg.configure_item("bottom_middle_pane", width=bottom_middle_width)

        if self._visualization_workspace:
            asyncio.create_task(self._visualization_workspace.resize_gui(top_middle_width, top_middle_height))

        from research_analytics_suite.gui import center_in_container
        center_in_container("bottom_middle_pane", "splitter_resize")

    def splitter_callback(self):
        if self._splitter_height == 150:
            self._splitter_height = 300
            dpg.configure_item("splitter_resize", label="vvv")
        else:
            self._splitter_height = 150
            dpg.configure_item("splitter_resize", label="^^^")

        self.adjust_main_window()

    async def new_workspace_dialog(self, sender=None, app_data=None, user_data=None):
        """Opens a file dialog to create a new workspace."""
        with dpg.file_dialog(
            directory_selector=True,
            show=True,
            callback=self._create_workspace_callback,
            default_path=os.path.expanduser(f"~/Research-Analytics-Suite/workspaces/"),
            tag="new_workspace_file_dialog",
            width=700,
            height=400
        ):
            dpg.add_file_extension("", color=(150, 255, 150, 255))

    def _create_workspace_callback(self, sender, app_data):
        """
        Callback after selecting folder for new workspace.
        app_data contains {'file_path_name': str, 'current_path': str, ...}
        """
        folder_path = app_data["file_path_name"]
        # Ask for a name (popup input)
        with dpg.window(label="Workspace Name", modal=True, width=350, height=120, tag="workspace_name_popup"):
            dpg.add_input_text(label="Workspace Name", tag="workspace_name_input")
            dpg.add_button(label="Create", callback=lambda: self._finalize_new_workspace(folder_path))

    def _finalize_new_workspace(self, folder_path: str):
        name = dpg.get_value("workspace_name_input")
        if not name:
            self._logger.error(Exception("Workspace name cannot be empty."), self.__class__.__name__)
            return
        asyncio.run(self._workspace.create_workspace(workspace_name=name, workspace_directory=folder_path))
        dpg.delete_item("new_workspace_file_dialog")
        dpg.delete_item("workspace_name_popup")
        self._logger.debug(f"Workspace created at {folder_path} with name {name}.")

        # Trigger GUI relaunch for new workspace
        self.request_relaunch()

    async def open_workspace_dialog(self, sender=None, app_data=None, user_data=None):
        """Opens a file dialog to load an existing workspace config.json."""
        with dpg.file_dialog(
            directory_selector=False,
            show=True,
            callback=self._open_workspace_callback,
            default_path=os.path.expanduser(f"~/Research-Analytics-Suite/workspaces/"),
            tag="open_workspace_file_dialog",
            width=700,
            height=400
        ):
            dpg.add_file_extension(".json", color=(0, 255, 255, 255), custom_text="[Config Files]")

    def _open_workspace_callback(self, sender, app_data):
        """Callback after selecting workspace config.json"""
        config_file = app_data["file_path_name"]
        if not config_file.endswith("config.json"):
            self._logger.error(Exception("Please select a valid config.json file."), self.__class__.__name__)
            return
        asyncio.run(self._workspace.load_workspace(config_file))
        dpg.delete_item("open_workspace_file_dialog")
        self._logger.debug(f"Workspace loaded from {config_file}.")

        # Trigger GUI relaunch for workspace change
        self.request_relaunch()

    def show_documentation(self, sender=None, app_data=None, user_data=None):
        """Shows the documentation dialog."""
        if self._documentation_dialog is None:
            self._documentation_dialog = DocumentationDialog()
        self._documentation_dialog.show()

    def show_about(self, sender=None, app_data=None, user_data=None):
        """Shows the about dialog."""
        if self._about_dialog is None:
            self._about_dialog = AboutDialog()
        self._about_dialog.show()

    async def show_hardware_dialog(self, sender=None, app_data=None, user_data=None):
        """Shows hardware monitor as a popup."""
        if self._hardware_dialog is None:
            self._hardware_dialog = HardwareDialog(width=600, height=400, parent=None,
                                                   hardware_manager=self._hardware_manager)
            await self._hardware_dialog.initialize_gui()

        if dpg.does_item_exist("hardware_monitor_window"):
            dpg.delete_item("hardware_monitor_window")

        with dpg.window(label="Hardware Monitor", modal=False, width=600, height=400,
                       tag="hardware_monitor_window", pos=(100, 100)):
            self._hardware_dialog.draw()

    async def show_resource_monitor(self, sender=None, app_data=None, user_data=None):
        """Shows resource monitor as a popup."""
        if dpg.does_item_exist("resource_monitor_window"):
            dpg.delete_item("resource_monitor_window")

        with dpg.window(label="Resource Monitor", modal=False, width=600, height=400,
                       tag="resource_monitor_window", pos=(100, 100)):
            if self._resource_monitor_dialog is None:
                self._resource_monitor_dialog = ResourceMonitorDialog(width=-1, height=-1,
                                                                      parent="resource_monitor_window")
                await self._resource_monitor_dialog.initialize_gui()
            self._resource_monitor_dialog.draw()

    async def show_console(self, sender=None, app_data=None, user_data=None):
        """Shows console as a popup."""
        if dpg.does_item_exist("console_window"):
            dpg.delete_item("console_window")

        with dpg.window(label="Console/Logs", modal=False, width=800, height=500,
                       tag="console_window", pos=(100, 100)):
            if self._console_dialog is None:
                self._console_dialog = ConsoleDialog(parent="console_window", width=-1, height=-1)
                await self._console_dialog.initialize_gui()
            self._console_dialog.draw()

    async def shutdown_gui(self):
        """Cleanly shuts down the GUI for relaunch or exit."""
        if self._is_shutting_down:
            return

        self._is_shutting_down = True
        self._logger.debug("Shutting down GUI...")

        try:
            # Clean up new GUI panels
            if self._notification_panel:
                await self._notification_panel.cleanup()
            if self._visualization_workspace:
                await self._visualization_workspace.cleanup()
            if self._workflow_panel:
                await self._workflow_panel.cleanup()

            # Stop notification bus
            await notification_bus.stop()

            # Stop specific GUI update operations by finding them in the sequencer
            if hasattr(self._operation_control, 'sequencer'):
                gui_operation_names = ['gui_ResourceUpdate', 'gui_ConsoleUpdate', 'gui_DataManUpdate']
                for op_name in gui_operation_names:
                    try:
                        # Find and stop the operation by iterating through chains and nodes
                        found = False
                        for chain in self._operation_control.sequencer.sequencer:
                            for node in chain:
                                if hasattr(node.operation, 'name') and node.operation.name == op_name:
                                    await node.operation.stop()
                                    self._logger.debug(f"Stopped {op_name}")
                                    found = True
                                    break
                            if found:
                                break
                    except Exception as e:
                        self._logger.warning(f"Failed to stop {op_name}: {e}")

            # Give operations time to finish stopping
            await asyncio.sleep(0.2)

            # Stop DearPyGui async operations
            if hasattr(self._dpg_async, 'stop'):
                await self._dpg_async.stop()

            # Clean up node managers
            if self._node_manager:
                await self._node_manager.reset_for_workspace()

            # Stop DearPyGui context
            if dpg.is_dearpygui_running():
                dpg.stop_dearpygui()

            # Give DearPyGui time to cleanup properly
            await asyncio.sleep(0.1)

            # Destroy DearPyGui context completely
            try:
                dpg.destroy_context()
            except Exception as ctx_error:
                self._logger.debug(f"Context already destroyed or error during cleanup: {ctx_error}")

        except Exception as e:
            self._logger.warning(f"Error during GUI shutdown: {e}")
        finally:
            self._is_shutting_down = False

    def request_relaunch(self):
        """Request GUI relaunch for workspace changes."""
        self._should_relaunch = True
        self._logger.info("GUI relaunch requested")

    async def _exit(self):
        """Exits the application."""
        await self.shutdown_gui()
        await self._workspace.close()

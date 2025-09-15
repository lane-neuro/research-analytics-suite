"""
SettingsDialog Module

This module defines the SettingsDialog class, which provides a GUI for managing the self._configuration settings of the
Research Analytics Suite.

Author: Lane
"""
import os

import dearpygui.dearpygui as dpg

from research_analytics_suite.gui.GUIBase import GUIBase
from research_analytics_suite.utils.Config import Config
from research_analytics_suite.utils.CustomLogger import CustomLogger


class SettingsDialog(GUIBase):
    """Class to create and manage the settings dialog for self._configuration variables."""

    def __init__(self, width: int, height: int, parent):
        """
        Initializes the SettingsDialog instance.
        """
        super().__init__(width, height, parent)

    async def initialize_gui(self) -> None:
        if dpg.does_item_exist("settings_dialog"):
            dpg.delete_item("settings_dialog")

        self._config = await self._config.reload_from_file(os.path.join(self._config.BASE_DIR, 'workspaces',
                                                           self._config.WORKSPACE_NAME))

    async def _update_async(self) -> None:
        pass

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        pass

    def draw(self):
        """Shows the settings dialog."""
        with dpg.window(label="Settings", modal=True, tag="settings_dialog", width=500):
            dpg.add_text("Configuration Settings", color=(255, 255, 0))

            # Paths
            dpg.add_input_text(label="Workspace Name", default_value=self._config.WORKSPACE_NAME, tag="workspace_name")
            dpg.add_input_text(label="Data Directory", default_value=self._config.DATA_DIR, tag="data_dir")
            dpg.add_input_text(label="Log Directory", default_value=self._config.LOG_DIR, tag="log_dir")
            dpg.add_input_text(label="Workspace Directory", default_value=self._config.WORKSPACE_DIR,
                               tag="workspace_dir")
            dpg.add_input_text(label="Workspace Operations Directory",
                               default_value=self._config.WORKSPACE_OPERATIONS_DIR,
                               tag="workspace_operations_dir")
            dpg.add_input_text(label="Engine Directory", default_value=self._config.ENGINE_DIR, tag="engine_dir")
            dpg.add_input_text(label="Backup Directory", default_value=self._config.BACKUP_DIR, tag="backup_dir")
            dpg.add_input_text(label="Export Directory", default_value=self._config.EXPORT_DIR, tag="export_dir")

            dpg.add_separator()

            # Memory settings
            dpg.add_input_float(label="Memory Limit", default_value=self._config.MEMORY_LIMIT, tag="memory_limit")

            dpg.add_separator()

            # Logging settings
            dpg.add_input_text(label="Log Rotation", default_value=self._config.LOG_ROTATION, tag="log_rotation")
            dpg.add_input_text(label="Log Retention", default_value=self._config.LOG_RETENTION, tag="log_retention")

            dpg.add_separator()

            dpg.add_button(label="Save", callback=self.save_settings)
            dpg.add_button(label="Close", callback=lambda: dpg.delete_item("settings_dialog"))

    def save_settings(self):
        """Saves the updated settings."""
        self._config.WORKSPACE_NAME = dpg.get_value("workspace_name")

        self._config.DATA_DIR = dpg.get_value("data_dir")
        self._config.LOG_DIR = dpg.get_value("log_dir")
        self._config.WORKSPACE_DIR = dpg.get_value("workspace_dir")
        self._config.WORKSPACE_OPERATIONS_DIR = dpg.get_value("workspace_operations_dir")
        self._config.BACKUP_DIR = dpg.get_value("backup_dir")
        self._config.EXPORT_DIR = dpg.get_value("export_dir")
        self._config.ENGINE_DIR = dpg.get_value("engine_dir")

        self._config.MEMORY_LIMIT = dpg.get_value("memory_limit")

        self._config.LOG_ROTATION = dpg.get_value("log_rotation")
        self._config.LOG_RETENTION = dpg.get_value("log_retention")

        self._logger.info("Settings updated successfully.")
        dpg.delete_item("settings_dialog")

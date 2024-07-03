"""
DataImportWizard Module

This module defines the DataImportWizard class, which guides users through the process of importing data into the
research analytics suite. It supports various data formats and provides options to preview data before importing.

Author: Lane
"""
import asyncio

import dearpygui.dearpygui as dpg

from research_analytics_suite.data_engine.engine.UnifiedDataEngine import UnifiedDataEngine
from research_analytics_suite.gui.GUIBase import GUIBase


class DataImportWizard(GUIBase):
    """
    A class to guide users through the process of importing data.
    """

    def __init__(self, data_engine: UnifiedDataEngine, parent, width: int = 600, height: int = 400):
        """
        Initializes the DataImportWizard instance.

        Args:
            data_engine (UnifiedDataEngine): The data engine for handling data operations.
        """
        super().__init__(width, height, parent)
        self._data_engine = data_engine

    async def initialize_gui(self) -> None:
        """
        Initializes the data import wizard dialog.
        """
        pass

    async def _update_async(self) -> None:
        pass

    def draw(self) -> None:
        """Draws the GUI elements for the Data Import Wizard."""
        with dpg.group(tag="data_import_wizard", parent=self._parent):
            dpg.add_text("Data Import Wizard", color=(255, 255, 0))

            with dpg.group(horizontal=True):
                dpg.add_button(label="Choose File", callback=self._choose_file)
                dpg.add_text("Selected File:", tag="selected_file_text")

            dpg.add_separator()

            with dpg.group(horizontal=True):
                dpg.add_button(label="Preview Data", callback=self._preview_data)
                dpg.add_text("Data Preview:", tag="data_preview_text")

            dpg.add_button(label="Import Data")

    def _choose_file(self, sender, app_data, user_data):
        """
        Opens a file dialog to choose a file for importing data.

        Args:
            sender: Sender of the choose file command.
            app_data: Application data.
            user_data: User data.
        """
        if dpg.does_item_exist("selected_file"):
            dpg.delete_item("selected_file")

    def _preview_data(self, sender, app_data, user_data):
        """
        Previews the data from the selected file.

        Args:
            sender: Sender of the preview data command.
            app_data: Application data.
            user_data: User data.
        """
        file_path = dpg.get_value("selected_file_text").replace("Selected File: ", "")
        # data_preview = self._data_engine.preview_data(file_path)
        # dpg.set_value("data_preview_text", f"Data Preview:\n{data_preview}")
        self._logger.debug(f"Previewing data from: {file_path}")

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        pass

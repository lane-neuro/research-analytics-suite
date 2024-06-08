"""
DataImportWizard Module

This module defines the DataImportWizard class, which guides users through the process of importing data into the
neurobehavioral analytics suite. It supports various data formats and provides options to preview data before importing.

Author: Lane
"""

import dearpygui.dearpygui as dpg
from neurobehavioral_analytics_suite.data_engine.UnifiedDataEngine import UnifiedDataEngine
from neurobehavioral_analytics_suite.utils.CustomLogger import CustomLogger


class DataImportWizard:
    """
    A class to guide users through the process of importing data.
    """
    def __init__(self, data_engine: UnifiedDataEngine):
        """
        Initializes the DataImportWizard instance.

        Args:
            data_engine (UnifiedDataEngine): The data engine for handling data operations.
        """
        self._data_engine = data_engine
        self._logger = CustomLogger()

    async def initialize(self):
        """
        Initializes the data import wizard dialog.
        """
        with dpg.group(tag="data_import_wizard"):
            dpg.add_text("Data Import Wizard")
            dpg.add_button(label="Choose File", callback=self._choose_file)
            dpg.add_text("Selected File:", tag="selected_file_text")
            dpg.add_button(label="Preview Data", callback=self._preview_data)
            dpg.add_text("Data Preview:", tag="data_preview_text")
            dpg.add_button(label="Import Data", callback=self._import_data)

    def _choose_file(self, sender, app_data, user_data):
        """
        Opens a file dialog to choose a file for importing data.

        Args:
            sender: Sender of the choose file command.
            app_data: Application data.
            user_data: User data.
        """
        file_path = dpg.open_file_dialog()
        if file_path:
            dpg.set_value("selected_file_text", f"Selected File: {file_path}")
            self._logger.info(f"Selected file for import: {file_path}")

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
        self._logger.info(f"Previewing data from: {file_path}")

    def _import_data(self, sender, app_data, user_data):
        """
        Imports data from the selected file into the data engine.

        Args:
            sender: Sender of the import data command.
            app_data: Application data.
            user_data: User data.
        """
        file_path = dpg.get_value("selected_file_text").replace("Selected File: ", "")
        self._data_engine.load_data(file_path)
        dpg.set_value("data_preview_text", f"Data imported from {file_path}")
        self._logger.info(f"Data imported from {file_path}")

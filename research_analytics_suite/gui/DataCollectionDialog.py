"""
DataCollectionDialog

This module defines the DataCollectionDialog class, which is responsible for managing the Data Collection tools and
their GUI representation within the research analytics suite. It handles the initialization and updates the GUI
accordingly.

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
from research_analytics_suite.utils.CustomLogger import CustomLogger


class DataCollectionDialog:
    """A class to manage Data Collection tools and their GUI representation."""

    def __init__(self, width: int, height: int):
        """
        Initializes the DataCollectionDialog with the given width and height.

        Args:
            width (int): The width of the dialog.
            height (int): The height of the dialog.
        """
        self.width = width
        self.height = height
        self._logger = CustomLogger()

    def draw(self, parent):
        """Draws the GUI elements for the Data Collection section."""
        with dpg.group(parent=parent):
            dpg.add_text("Data Collection Tools", parent=parent)

            with dpg.group(horizontal=True):
                dpg.add_button(label="Data Sources", callback=self.show_data_sources)
                dpg.add_button(label="Data Import", callback=self.show_data_import)
                dpg.add_button(label="Surveys/Forms", callback=self.show_surveys_forms)
                dpg.add_button(label="Sensor Integration", callback=self.show_sensor_integration)
                dpg.add_button(label="Manual Entry", callback=self.show_manual_entry)
                dpg.add_button(label="Data Quality Checks", callback=self.show_data_quality_checks)

    def show_data_sources(self, sender, app_data, user_data):
        """Displays the Data Sources section."""
        self._logger.info("Data Sources clicked")

    def show_data_import(self, sender, app_data, user_data):
        """Displays the Data Import section."""
        self._logger.info("Data Import clicked")

    def show_surveys_forms(self, sender, app_data, user_data):
        """Displays the Surveys/Forms section."""
        self._logger.info("Surveys/Forms clicked")

    def show_sensor_integration(self, sender, app_data, user_data):
        """Displays the Sensor Integration section."""
        self._logger.info("Sensor Integration clicked")

    def show_manual_entry(self, sender, app_data, user_data):
        """Displays the Manual Entry section."""
        self._logger.info("Manual Entry clicked")

    def show_data_quality_checks(self, sender, app_data, user_data):
        """Displays the Data Quality Checks section."""
        self._logger.info("Data Quality Checks clicked")

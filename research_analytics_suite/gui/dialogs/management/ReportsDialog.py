"""
ReportsDialog

This module defines the ReportsDialog class, which is responsible for managing the Reports tools and their GUI
representation within the research analytics suite. It handles the initialization and updates the GUI accordingly.

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


class ReportsDialog:
    """A class to manage Reports tools and their GUI representation."""

    def __init__(self, width: int, height: int):
        """
        Initializes the ReportsDialog with the given width and height.

        Args:
            width (int): The width of the dialog.
            height (int): The height of the dialog.
        """
        self.width = width
        self.height = height
        self._logger = CustomLogger()

    def draw(self, parent):
        """Draws the GUI elements for the Reports section."""
        with dpg.group(parent=parent):
            dpg.add_text("Reports Tools", parent=parent)

            with dpg.group(horizontal=True):
                dpg.add_button(label="Generate Reports", callback=self.show_generate_reports)
                dpg.add_button(label="Export Options", callback=self.show_export_options)
                dpg.add_button(label="Report Templates", callback=self.show_report_templates)
                dpg.add_button(label="Summary Reports", callback=self.show_summary_reports)
                dpg.add_button(label="Detailed Reports", callback=self.show_detailed_reports)
                dpg.add_button(label="Custom Reports", callback=self.show_custom_reports)

    def show_generate_reports(self, sender, app_data, user_data):
        """Displays the Generate Reports section."""
        self._logger.info("Generate Reports clicked")

    def show_export_options(self, sender, app_data, user_data):
        """Displays the Export Options section."""
        self._logger.info("Export Options clicked")

    def show_report_templates(self, sender, app_data, user_data):
        """Displays the Report Templates section."""
        self._logger.info("Report Templates clicked")

    def show_summary_reports(self, sender, app_data, user_data):
        """Displays the Summary Reports section."""
        self._logger.info("Summary Reports clicked")

    def show_detailed_reports(self, sender, app_data, user_data):
        """Displays the Detailed Reports section."""
        self._logger.info("Detailed Reports clicked")

    def show_custom_reports(self, sender, app_data, user_data):
        """Displays the Custom Reports section."""
        self._logger.info("Custom Reports clicked")

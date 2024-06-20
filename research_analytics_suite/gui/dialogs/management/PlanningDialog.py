"""
PlanningDialog

This module defines the PlanningDialog class, which is responsible for managing the Planning tools and their GUI
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


class PlanningDialog:
    """A class to manage Planning tools and their GUI representation."""

    def __init__(self, width: int, height: int):
        """
        Initializes the PlanningDialog with the given width and height.

        Args:
            width (int): The width of the dialog.
            height (int): The height of the dialog.
        """
        self.width = width
        self.height = height
        self._logger = CustomLogger()

    def draw(self, parent):
        """Draws the GUI elements for the Planning section."""
        with dpg.group(parent=parent):
            dpg.add_text("Planning Tools", parent=parent)

            with dpg.group(horizontal=True):
                dpg.add_button(label="Project Overview", callback=self.show_project_overview)
                dpg.add_button(label="Objectives", callback=self.show_objectives)
                dpg.add_button(label="Timeline", callback=self.show_timeline)
                dpg.add_button(label="Resources", callback=self.show_resources)

    def show_project_overview(self, sender, app_data, user_data):
        """Displays the Project Overview section."""
        self._logger.info("Project Overview clicked")

    def show_objectives(self, sender, app_data, user_data):
        """Displays the Objectives section."""
        self._logger.info("Objectives clicked")

    def show_timeline(self, sender, app_data, user_data):
        """Displays the Timeline section."""
        self._logger.info("Timeline clicked")

    def show_resources(self, sender, app_data, user_data):
        """Displays the Resources section."""
        self._logger.info("Resources clicked")

"""
ProjectManagerDialog

This module defines the ProjectManagerDialog class, which is responsible for managing the Project Management tools and
their GUI representation within the research analytics suite. It handles the initialization and updates the
GUI accordingly.

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

from research_analytics_suite.gui.GUIBase import GUIBase
from research_analytics_suite.utils.CustomLogger import CustomLogger


class ProjectManagerDialog(GUIBase):
    """A class to manage Project Management tools and their GUI representation."""

    def __init__(self, width: int, height: int, parent):
        """
        Initializes the ManageProjectDialog with the given width and height.

        Args:
            width (int): The width of the dialog.
            height (int): The height of the dialog.
        """
        super().__init__(width, height, parent)

    async def initialize_gui(self) -> None:
        pass

    async def _update_async(self) -> None:
        pass

    def draw(self):
        """Draws the GUI elements for the Project Management section."""
        with dpg.group(parent=self._parent):
            dpg.add_text("Project Management Tools")
            dpg.add_separator()

            with dpg.group(horizontal=True):
                dpg.add_button(label="Task Management", callback=self.show_task_management)
                dpg.add_button(label="Team Collaboration", callback=self.show_team_collaboration)
                dpg.add_button(label="Progress Tracking", callback=self.show_progress_tracking)
                dpg.add_button(label="Risk Management", callback=self.show_risk_management)
                dpg.add_button(label="Budget Tracking", callback=self.show_budget_tracking)
                dpg.add_button(label="Documentation", callback=self.show_documentation)

    def show_task_management(self, sender, app_data, user_data):
        """Displays the Task Management section."""
        self._logger.info("Task Management clicked")

    def show_team_collaboration(self, sender, app_data, user_data):
        """Displays the Team Collaboration section."""
        self._logger.info("Team Collaboration clicked")

    def show_progress_tracking(self, sender, app_data, user_data):
        """Displays the Progress Tracking section."""
        self._logger.info("Progress Tracking clicked")

    def show_risk_management(self, sender, app_data, user_data):
        """Displays the Risk Management section."""
        self._logger.info("Risk Management clicked")

    def show_budget_tracking(self, sender, app_data, user_data):
        """Displays the Budget Tracking section."""
        self._logger.info("Budget Tracking clicked")

    def show_documentation(self, sender, app_data, user_data):
        """Displays the Documentation section."""
        self._logger.info("Documentation clicked")

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        pass

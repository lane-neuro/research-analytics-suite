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

from research_analytics_suite.gui.GUIBase import GUIBase


class PlanningDialog(GUIBase):
    """A class to manage Planning tools and their GUI representation."""

    def __init__(self, width: int, height: int, parent):
        """
        Initializes the PlanningDialog with the given width and height.

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
        """Draws the GUI elements for the Planning section."""
        with dpg.group(parent=self._parent):
            dpg.add_text("Planning Tools")
            dpg.add_separator()

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

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        pass

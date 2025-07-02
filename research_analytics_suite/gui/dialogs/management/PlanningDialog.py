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
        self._plan_space = None

    async def initialize_gui(self) -> None:
        ...
        # self._logger.debug("Initializing the Planning dialog window.")
        # from research_analytics_suite.operation_manager.operations.system.UpdateMonitor import UpdateMonitor
        # self._update_operation = await self._operation_control.operation_manager.add_operation_with_parameters(
        #     operation_type=UpdateMonitor, name="gui_PlanningUpdateMonitor", action=self._update_async,
        #     is_loop=True, parallel=True)
        # self._update_operation.is_ready = True
        # self._logger.debug("Initialized the Planning dialog window.")

    async def _update_async(self) -> None:
        """Continuously checks for new operations and updates the GUI."""
        ...

    def draw(self):
        """Draws the GUI elements for the Planning section."""
        with dpg.group(parent=self._parent, tag=self._runtime_id):
            # dpg.add_text("Planning Tools")
            # dpg.add_separator()
            #
            # with dpg.group(horizontal=True):
            #     dpg.add_button(label="Project Overview", callback=self.show_project_overview)
            #     dpg.add_button(label="Objectives", callback=self.show_objectives)
            #     dpg.add_button(label="Timeline", callback=self.show_timeline)
            #     dpg.add_button(label="Resources", callback=self.show_resources)

            dpg.add_child_window(width=-1, height=-1, border=True, tag="plan_space", parent=self._runtime_id)

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

"""
ConsoleDialog Module.

This module defines the ConsoleDialog class, which creates a console dialog for user input and operations control within 
the research analytics suite. It handles the initialization, command submission, and logger output updates, 
providing a user interface for interacting with operations.

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
import dearpygui.dearpygui as dpg

from research_analytics_suite.commands.UserInputProcessor import process_user_input
from research_analytics_suite.gui.GUIBase import GUIBase
from research_analytics_suite.operation_manager.operations.system.UpdateMonitor import UpdateMonitor


class ConsoleDialog(GUIBase):
    """A class to create a console dialog for user input and operations control."""

    def __init__(self, width: int, height: int, parent):
        """
        Initializes the ConsoleDialog with the given user input handler, operations control, and logger.
        """
        super().__init__(width, height, parent)
        self.command_history = []

    async def initialize_gui(self) -> None:
        self._update_operation = await self._operation_control.operation_manager.create_operation(
                operation_type=UpdateMonitor, name="gui_ConsoleUpdate", action=self._update_async)
        self._update_operation.is_ready = True

    async def _update_async(self) -> None:
        """Continuously updates the logger output with new messages."""
        while True:
            new_log = await self._logger.log_message_queue.get()
            current_logs = dpg.get_value("logger_output")
            updated_logs = new_log + "\n" + current_logs
            dpg.set_value("logger_output", updated_logs)
            await asyncio.sleep(0.001)

    def draw(self) -> None:
        """Draws the GUI elements for the console dialog."""
        with dpg.group(horizontal=True, parent=self._parent):
            dpg.add_input_text(label="", tag="input_text", width=500)
            dpg.add_button(label="Submit", callback=self.submit_command)
        dpg.add_separator()
        dpg.add_text(default_value="", parent=self._parent, wrap=-1, tag="logger_output")

    async def submit_command(self, sender: str, app_data: dict) -> None:
        """
        Submits the user command for processing.

        Args:
            sender (str): The sender of the submit event.
            app_data (dict): Additional application data.
        """
        command = dpg.get_value('input_text')
        _return = await process_user_input(command)
        if _return is not None and not isinstance(_return, Exception):
            dpg.set_value('input_text', "")

    def clear_logger_output(self) -> None:
        """Clears the logger output display."""
        dpg.set_value("logger_output", "")

    def search_command(self, sender: str, app_data: dict) -> None:
        """
        Searches for a text in the console output.

        Args:
            sender (str): The sender of the search event.
            app_data (dict): Additional application data.
        """
        search_text = dpg.get_value('search_text')
        console_output = dpg.get_value("logger_output")
        if search_text in console_output:
            dpg.set_value("logger_output", search_text)
        else:
            dpg.set_value("logger_output", "Text not found")

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        pass

# neurobehavioral_analytics_suite/gui/ConsoleGui.py
import asyncio

import dearpygui.dearpygui as dpg

from neurobehavioral_analytics_suite.operation_handler.OperationHandler import OperationHandler
from neurobehavioral_analytics_suite.utils.UserInputManager import UserInputManager


class ConsoleGui:
    def __init__(self, user_input_handler: UserInputManager, operation_handler: OperationHandler, logger):
        self.logger = logger
        self.window = dpg.add_window(label="Console")

        # Create a child window
        self.input_child = dpg.add_child_window(tag="input_child", parent=self.window, height=20,
                                                border=False, no_scrollbar=True)

        # Add the input text and submit button to the child window
        with dpg.group(tag="command_group", parent=self.input_child, horizontal=True):
            dpg.add_input_text(label="", tag="input_text")
            dpg.add_button(label="Submit", tag="submit_button", callback=self.submit_command)

        self.logger_output = dpg.add_text(default_value="", parent=self.window, wrap=600)
        # self.search_text = dpg.add_input_text(label="Search", parent=self.window)
        # self.search_button = dpg.add_button(label="Search", callback=self.search_command, parent=self.window)
        self.user_input_handler = user_input_handler
        self.operation_handler = operation_handler
        self.command_history = []
        self.command_help = {"command1": "This is command1", "command2": "This is command2"}
        self.command_aliases = {"c1": "command1", "c2": "command2"}

        try:
            self.update_operation = asyncio.create_task(self.update_logger_output(), name="gui_ConsoleUpdateTask")
        except Exception as e:
            self.logger.error(f"Error creating task: {e}")

    async def submit_command(self, sender, data):
        if dpg.is_key_pressed(dpg.mvKey_Return) or sender == "submit_button":
            command = dpg.get_value('input_text')
            if command in self.command_aliases:
                command = self.command_aliases[command]
            if command.startswith("help"):
                _, command = command.split()
                help_text = self.command_help.get(command, "No help available for this command")
                dpg.set_value(self.logger_output, help_text)
            else:
                try:
                    await self.user_input_handler.process_user_input(command)
                    self.command_history.append(command)
                except Exception as e:
                    self.logger.error(self, e)
            dpg.set_value('input_text', "")  # Clear the input field

    async def update_logger_output(self):
        """Continuously update the logger output with new messages."""
        while True:
            new_log = await self.logger.log_message_queue.get()
            current_logs = dpg.get_value(self.logger_output)
            updated_logs = new_log + "\n" + current_logs
            dpg.set_value(self.logger_output, updated_logs)

    def clear_logger_output(self):
        dpg.set_value(self.logger_output, "")

    def search_command(self, sender, data):
        search_text = dpg.get_value(self.search_text)
        console_output = dpg.get_value(self.logger_output)
        if search_text in console_output:
            dpg.set_value(self.logger_output, search_text)
        else:
            dpg.set_value(self.logger_output, "Text not found")

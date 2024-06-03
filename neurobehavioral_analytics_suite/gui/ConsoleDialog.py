import asyncio
import dearpygui.dearpygui as dpg
from neurobehavioral_analytics_suite.operation_manager.OperationControl import OperationControl
from neurobehavioral_analytics_suite.operation_manager.operation.CustomOperation import CustomOperation
from neurobehavioral_analytics_suite.utils.UserInputManager import UserInputManager

class ConsoleDialog:
    def __init__(self, user_input_handler: UserInputManager, operation_control: OperationControl, logger):
        self.logger = logger
        self.window = dpg.add_child_window(tag="console_window", parent="bottom_pane")

        with dpg.group(horizontal=True, parent=self.window):
            dpg.add_input_text(label="", tag="input_text")
            dpg.add_button(label="Submit", callback=self.submit_command)

        self.logger_output = dpg.add_text(default_value="", parent=self.window, wrap=600)
        self.user_input_handler = user_input_handler
        self.operation_control = operation_control
        self.command_history = []
        self.command_help = {"command1": "This is command1", "command2": "This is command2"}
        self.command_aliases = {"c1": "command1", "c2": "command2"}

        self.update_operation = None

    async def initialize(self):
        self.update_operation = await self.add_update_operation()

    async def add_update_operation(self):
        try:
            operation = await self.operation_control.operation_manager.add_operation(
                operation_type=CustomOperation, name="gui_ConsoleUpdateTask",
                local_vars=self.operation_control.local_vars, error_handler=self.operation_control.error_handler,
                func=self.update_logger_output, persistent=True)
            return operation
        except Exception as e:
            self.logger.error(f"Error creating task: {e}")
        return None

    async def submit_command(self, sender, data):
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
            await asyncio.sleep(0.01)

    def clear_logger_output(self):
        dpg.set_value(self.logger_output, "")

    def search_command(self, sender, data):
        search_text = dpg.get_value(self.search_text)
        console_output = dpg.get_value(self.logger_output)
        if search_text in console_output:
            dpg.set_value(self.logger_output, search_text)
        else:
            dpg.set_value(self.logger_output, "Text not found")

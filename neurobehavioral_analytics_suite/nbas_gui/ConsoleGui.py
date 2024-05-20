# neurobehavioral_analytics_suite/nbas_gui/ConsoleGui.py
import asyncio

import dearpygui.dearpygui as dpg
from neurobehavioral_analytics_suite.operation_handler.OperationHandler import OperationHandler


class ConsoleGui:
    def __init__(self, operation_handler: OperationHandler):
        self.window = dpg.add_window(label="Console")
        self.input_text = dpg.add_input_text(label="Command", parent=self.window)
        self.submit_button = dpg.add_button(label="Submit", callback=self.submit_command, parent=self.window)
        self.operation_handler = operation_handler

    async def submit_command(self, sender, data):
        command = dpg.get_value(self.input_text)
        await self.operation_handler.process_user_input(command)
        dpg.set_value(self.input_text, "")  # Clear the input field

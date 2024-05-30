# neurobehavioral_analytics_suite/gui/OperationManagerDialog.py
import asyncio

import dearpygui.dearpygui as dpg
from neurobehavioral_analytics_suite.operation_manager.OperationHandler import OperationHandler


class OperationManagerDialog:
    SLEEP_DURATION = 0.05

    def __init__(self, operation_handler: OperationHandler):
        self.window = dpg.add_window(label="Operation Manager")
        self.operation_handler = operation_handler
        self.operation_items = {}  # Store operation GUI items

        try:
            self.update_operation = asyncio.create_task(self.display_operations(), name="gui_OperationUpdateTask")
        except Exception as e:
            print(f"Error creating task: {e}")

    async def display_operations(self):
        while True:
            for operation_list in self.operation_handler.queue.queue:
                operation = self.operation_handler.queue.get_operation_from_chain(operation_list)
                if operation not in self.operation_items:
                    # Create new GUI elements for the operation
                    operation_id = dpg.generate_uuid()
                    with dpg.group(horizontal=True, parent=self.window):
                        dpg.add_button(label="Pause", callback=self.pause_operation, user_data=operation)
                        dpg.add_button(label="Resume", callback=self.resume_operation, user_data=operation)
                        dpg.add_button(label="Stop", callback=self.stop_operation, user_data=operation)
                        dpg.add_text(operation.name, tag=operation_id)
                    self.operation_items[operation] = operation_id
                else:
                    # Update the status of the operation
                    dpg.set_value(self.operation_items[operation], f"{operation.status} - {operation.name}")
            await asyncio.sleep(self.SLEEP_DURATION)

    async def pause_operation(self, sender, app_data, user_data):
        await self.operation_handler.pause_operation(user_data)

    async def resume_operation(self, sender, app_data, user_data):
        await self.operation_handler.resume_operation(user_data)

    async def stop_operation(self, sender, app_data, user_data):
        await self.operation_handler.stop_operation(user_data)
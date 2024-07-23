"""
UpdatedOperationModule

This module defines the UpdatedOperationModule class, which is responsible for managing operations and their GUI
representation within the research analytics suite. It handles the initialization, execution, stopping, pausing,
resuming, and resetting of operations and updates the GUI accordingly.

Author: Lane
Copyright: Lane
Credits: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from copy import copy

import dearpygui.dearpygui as dpg

from research_analytics_suite.commands.utils.text_utils import get_function_body
from research_analytics_suite.gui.GUIBase import GUIBase
from research_analytics_suite.operation_manager.operations.core.OperationAttributes import OperationAttributes


class UpdatedOperationModule(GUIBase):

    def __init__(self, operation_attributes: OperationAttributes, width: int, height: int, parent: str):
        super().__init__(width, height, parent)
        self._parent_id = f"parent_{self._runtime_id}"

        from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation
        self.__attribute_reset = copy(operation_attributes)
        self._attributes = operation_attributes
        self.operation = BaseOperation(operation_attributes)
        self.operation.attach_gui_module(self)

    async def initialize_gui(self) -> None:
        pass

    async def _update_async(self) -> None:
        pass

    def draw(self):
        with dpg.group(tag=self._parent_id, parent=self._parent, height=self.height):
            self.draw_upper_region(self._parent_id, width=self.width)
            self.draw_details_region(self._parent_id, width=self.width)
            self.draw_middle_region(self._parent_id, width=self.width)
            self.draw_lower_region(self._parent_id, width=self.width)

    def draw_upper_region(self, parent, width=200):
        # with dpg.group(tag=f"upper_{self._runtime_id}", parent=parent, width=300):
        with dpg.group(horizontal=True, tag=f"basic_{self._runtime_id}",
                       parent=parent, horizontal_spacing=20, width=width-10):
            dpg.add_text(default_value=f"v{self._attributes.version}", indent=10)
            dpg.add_input_text(default_value=self._attributes.name)

        with dpg.group(horizontal=True, parent=parent, width=width, horizontal_spacing=20, height=65,
                       tag=f"details_{self._runtime_id}"):
            dpg.add_text(default_value=self._attributes.author, indent=10)
            with dpg.group(height=-1):
                dpg.add_input_text(default_value=self._attributes.github)
                if self.operation.initialized:
                    dpg.add_input_text(default_value=self.operation.status if hasattr(
                            self.operation, "status") else "Not Initialized")

    def draw_details_region(self, parent, width=200):
        with dpg.group(horizontal=True, tag=f"more_details_{self._runtime_id}", width=width*.6,
                       horizontal_spacing=15, parent=parent):
            with dpg.group(label="Description", tag=f"description_{self._runtime_id}"):
                dpg.add_text(default_value="Description", indent=10)
                dpg.add_text(default_value=self._attributes.description, wrap=width // 2 + 30)

            with dpg.group(label="Output", tag=f"output_{self._runtime_id}", parent=f"more_details_{self._runtime_id}",
                           width=width):
                dpg.add_text(default_value="Output", indent=5)
                dpg.add_listbox(items=[], num_items=3)

        if self.operation.initialized:
            with dpg.group(horizontal=True, tag=f"execution_{self._runtime_id}", parent=parent, width=width*.40,
                           height=20):
                dpg.add_button(label="Execute", callback=self.execute_operation)
                dpg.add_button(label="Stop", callback=self.stop_operation)
                dpg.add_button(label="Reset", callback=self.reset_operation)

        with dpg.group(horizontal=True, tag=f"options_{self._runtime_id}", horizontal_spacing=35, parent=parent,
                       width=width):
            dpg.add_checkbox(label="Loop", default_value=self._attributes.is_loop, indent=10)
            dpg.add_checkbox(label="GPU", default_value=self._attributes.is_gpu_bound)
            dpg.add_checkbox(label="Parallel", default_value=self._attributes.parallel)

    def draw_middle_region(self, parent, width=200):
        with dpg.group(horizontal=True, tag=f"middle_{self._runtime_id}",
                       parent=parent, horizontal_spacing=5):
            with dpg.group(label="Required Inputs", parent=f"middle_{self._runtime_id}", width=width*.62):
                dpg.add_text(default_value="Input", indent=10)

                req_input_list = [
                    f"{str(value)}" for _, value in self._attributes.required_inputs.items()
                ] if self._attributes.required_inputs else []
                dpg.add_listbox(items=req_input_list, num_items=3)

            with dpg.group(label="Inherited Ops", width=width*.65):
                dpg.add_text(default_value="Inherited Ops", indent=10)
                dpg.add_listbox(items=self._attributes.inheritance, num_items=3)

    def draw_lower_region(self, parent, width=200):
        dpg.add_text(default_value="Action", parent=parent, indent=10)
        with dpg.group(parent=parent, tag=f"action_group_{self._runtime_id}"):
            dpg.add_input_text(default_value=get_function_body(self._attributes.action), multiline=True,
                               tab_input=True, height=100)

        if self.operation.initialized:
            with dpg.group(parent=parent, tag=f"state_mods_{self._runtime_id}"):
                dpg.add_button(label="View Result", callback=self.view_result)
                dpg.add_button(label="Reload Original Attributes", callback=self.reload_attributes)
                dpg.add_button(label="Save Operation Settings", callback=self.operation.save_operation_in_workspace,
                               tag=f"save_{self._runtime_id}")

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        """Resizes the GUI."""
        self.width = new_width
        self.height = new_height
        dpg.set_item_width(self._parent_id, new_width)
        dpg.set_item_height(self._parent_id, new_height)

    def reload_attributes(self, sender: any, app_data: any, user_data: any) -> None:
        """Reloads the original attributes of the operation."""
        from research_analytics_suite.operation_manager import BaseOperation

        self._attributes = copy(self.__attribute_reset)
        self.operation = BaseOperation(self._attributes)
        self.operation.add_log_entry("Reloaded original attributes.")

    async def execute_operation(self, sender: any, app_data: any, user_data: any) -> None:
        """Executes the operation. If the operation has not been initialized, it will be initialized first."""
        if not hasattr(self.operation, "_initialized"):
            self.operation.add_log_entry("Detected uninitialized operation. Initializing operation.")
            await self.operation.initialize_operation()

        try:
            self.operation.is_ready = True
            self.operation.add_log_entry("Marked operation for execution.")
        except Exception as e:
            self._logger.error(e, self)
            self.operation.add_log_entry(f"Error executing operation: {e}")

    async def stop_operation(self, sender: any, app_data: any, user_data: any) -> None:
        """Stops the operation."""
        if not hasattr(self.operation, "_initialized") or not self.operation.initialized:
            self.operation.add_log_entry("ERROR: Cannot stop an operation that has not been initialized.")

        try:
            await self.operation.stop()
        except Exception as e:
            self._logger.error(e, self)
            self.operation.add_log_entry(f"Error stopping operation: {e}")

    async def reset_operation(self, sender: any, app_data: any, user_data: any) -> None:
        """Resets the operation."""
        if not hasattr(self.operation, "_initialized"):
            self.operation.add_log_entry("ERROR: Cannot reset an operation that has not been initialized.")

        try:
            await self.operation.reset()
        except Exception as e:
            self._logger.error(e, self)
            self.operation.add_log_entry(f"Error resetting operation: {e}")

    async def view_result(self, sender: any, app_data: any, user_data: any) -> None:
        """Handles the event when the user clicks the 'View Result' button."""
        if not hasattr(self.operation, "_initialized"):
            self.operation.add_log_entry(
                "ERROR: Cannot view the results of an operation that has not been initialized.")

        _result = await self.operation.get_results()
        self.operation.add_log_entry(f"Viewing result: {_result}")
        print(_result)

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
import asyncio
from copy import copy

import dearpygui.dearpygui as dpg

from research_analytics_suite.commands.utils.text_utils import get_function_body
from research_analytics_suite.gui.GUIBase import GUIBase
from research_analytics_suite.operation_manager.operations.core.OperationAttributes import OperationAttributes
from research_analytics_suite.operation_manager.operations.system.UpdateMonitor import UpdateMonitor


class UpdatedOperationModule(GUIBase):

    def __init__(self, operation_attributes: OperationAttributes, width: int, height: int, parent: str):
        super().__init__(width, height, parent)
        self.initialized = False
        self._parent_id = f"parent_{self._runtime_id}"

        from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation
        self.__attribute_reset = copy(operation_attributes)
        self._attributes = operation_attributes
        self.operation = BaseOperation(operation_attributes)

        self.operation.attach_gui_module(self)

    async def initialize_gui(self) -> None:
        self._logger.debug("Initializing the operation module dialog.")
        self._update_operation = await self._operation_control.operation_manager.create_operation(
            operation_type=UpdateMonitor, name=f"gui_{self.operation.runtime_id}", action=self._update_async)
        self.operation = await self._operation_control.operation_manager.add_initialized_operation(self.operation)
        self.initialized = True
        self._logger.info(f"Operation {self.operation.name} initialized.")
        self._update_operation.is_ready = True

    async def _update_async(self) -> None:
        """Asynchronous function to update the GUI elements."""
        while self._update_operation.is_ready:
            if not self.operation.initialized:
                await self.operation.initialize_operation()

            if dpg.does_item_exist(f"req_inputs_{self._runtime_id}"):
                # Update the listbox with the current required inputs
                req_inputs_dict = self._attributes.input_ids
                _inputs = [f"{k} - {v}" for k, v in req_inputs_dict.items()]
                dpg.configure_item(f"req_inputs_{self._runtime_id}", items=_inputs)

            if dpg.does_item_exist(f"output_list_{self._runtime_id}"):
                # Update the listbox with the current output values
                outputs_dict = self._attributes.output_ids
                _outputs = [f"{k} - {v}" for k, v in outputs_dict.items()]
                dpg.configure_item(f"output_list_{self._runtime_id}", items=_outputs)

            if dpg.does_item_exist(f"status_{self._runtime_id}"):
                # Update the status text with the current operation status
                dpg.configure_item(f"status_{self._runtime_id}", default_value=self.operation.status)

            await asyncio.sleep(0.001)

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
            with dpg.group(height=-1, width=-1):
                dpg.add_input_text(default_value=self._attributes.github)

    def draw_details_region(self, parent, width=200):
        with dpg.group(horizontal=True, tag=f"more_details_{self._runtime_id}", width=width*.6,
                       horizontal_spacing=15, parent=parent):
            with dpg.group(label="Description", tag=f"description_{self._runtime_id}"):
                dpg.add_text(default_value="Description", indent=10)
                dpg.add_text(default_value=self._attributes.description, wrap=width // 2 + 30)

            with dpg.group(label="Inherited Ops", width=width*.65):
                dpg.add_text(default_value="Inherited Ops", indent=10)
                dpg.add_listbox(items=self._attributes.inheritance, num_items=3)

        if self.operation.attributes.active:
            with dpg.group(horizontal=True, parent=parent, width=width*.40, height=20, indent=10):
                dpg.add_text(default_value="Status:")
                dpg.add_text(tag=f"status_{self._runtime_id}",
                    default_value=self.operation.status if hasattr(self.operation, "status") else "Not Initialized")

            with dpg.group(horizontal=True, tag=f"execution_{self._runtime_id}", parent=parent, width=width*.40,
                           height=20):
                dpg.add_button(label="Execute", callback=lambda: asyncio.run(self.execute_operation()))
                dpg.add_button(label="Stop", callback=lambda: asyncio.run(self.stop_operation()))
                dpg.add_button(label="Reset", callback=lambda: asyncio.run(self.reset_operation()))

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

                req_inputs_dict = self._attributes.input_ids
                _inputs = [f"{k} - {v}" for k, v in req_inputs_dict.items()]
                dpg.add_listbox(items=_inputs, num_items=3, tag=f"req_inputs_{self._runtime_id}")

            with dpg.group(label="Output", tag=f"output_{self._runtime_id}",
                           width=width*.65):
                dpg.add_text(default_value="Output", indent=5)
                dpg.add_listbox(items=[], num_items=3, tag=f"output_list_{self._runtime_id}")

    def draw_lower_region(self, parent, width=200):
        dpg.add_text(default_value="Action", parent=parent, indent=10)
        with dpg.group(parent=parent, tag=f"action_group_{self._runtime_id}"):
            dpg.add_input_text(default_value=get_function_body(self._attributes.action), multiline=True,
                               tab_input=True, height=100)

        if self.operation.attributes.active:
            with dpg.group(parent=parent, tag=f"state_mods_{self._runtime_id}"):
                dpg.add_button(label="View Result", callback=self.view_result)
                dpg.add_button(label="Reload Original Attributes", callback=self.reload_attributes)
                dpg.add_button(label="Save Operation Settings", callback=self.operation.save_in_workspace,
                               tag=f"save_{self._runtime_id}")

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        """Resizes the GUI."""
        self.width = new_width
        self.height = new_height
        dpg.set_item_width(self._parent_id, new_width)
        dpg.set_item_height(self._parent_id, new_height)

    def reload_attributes(self) -> None:
        """Reloads the original attributes of the operation."""
        from research_analytics_suite.operation_manager import BaseOperation

        self._attributes = copy(self.__attribute_reset)
        self.operation = BaseOperation(self._attributes)
        self.operation.add_log_entry("Reloaded original attributes.")

    async def execute_operation(self) -> None:
        """Executes the operation. If the operation has not been initialized, it will be initialized first."""
        if not hasattr(self.operation, "_initialized"):
            self.operation.add_log_entry("Detected uninitialized operation. Initializing operation.")
            self._logger.debug(f"Initializing operation {self.operation.name}.")
            await self.operation.initialize_operation()

        try:
            self.operation.is_ready = True
            self._logger.debug(f"Operation {self.operation.name} is ready for execution.")
            self.operation.add_log_entry("Marked operation for execution.")
        except Exception as e:
            self._logger.error(e, self)
            self.operation.add_log_entry(f"Error executing operation: {e}")

    async def stop_operation(self) -> None:
        """Stops the operation."""
        if not hasattr(self.operation, "_initialized") or not self.operation.initialized:
            self.operation.add_log_entry("ERROR: Cannot stop an operation that has not been initialized.")

        try:
            await self.operation.stop()
        except Exception as e:
            self._logger.error(e, self)
            self.operation.add_log_entry(f"Error stopping operation: {e}")

    async def reset_operation(self) -> None:
        """Resets the operation."""
        if not hasattr(self.operation, "_initialized"):
            self.operation.add_log_entry("ERROR: Cannot reset an operation that has not been initialized.")

        try:
            await self.operation.reset()
        except Exception as e:
            self._logger.error(e, self)
            self.operation.add_log_entry(f"Error resetting operation: {e}")

    async def view_result(self) -> None:
        """Handles the event when the user clicks the 'View Result' button."""
        if not hasattr(self.operation, "_initialized"):
            self.operation.add_log_entry(
                "ERROR: Cannot view the results of an operation that has not been initialized.")

        _output_dict = await self.operation.get_results()
        self._logger.debug(f"Viewing result: {_output_dict}")


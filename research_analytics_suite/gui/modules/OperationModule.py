"""
OperationModule

This module defines the OperationModule class, which is responsible for managing operations and their GUI representation
within the research analytics suite. It handles the initialization, execution, stopping, pausing, resuming, and
resetting of operations and updates the GUI accordingly.

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
import dearpygui.dearpygui as dpg

from research_analytics_suite.gui.GUIBase import GUIBase
from research_analytics_suite.gui.modules.CreateOperationModule import CreateOperationModule
from research_analytics_suite.gui.utils.left_aligned_button import left_aligned_button
from research_analytics_suite.gui.utils.left_aligned_input_field import left_aligned_input_field
from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation
from research_analytics_suite.operation_manager.operations.system.UpdateMonitor import UpdateMonitor


class OperationModule(GUIBase):
    """A class to manage operations and their GUI representation."""
    MIDDLE_INDENT = 20

    def __init__(self, operation: BaseOperation, width: int, height: int, parent):
        """
        Initializes the OperationModule with the given operation, control, and logger.

        Args:
            operation (BaseOperation): An instance of BaseOperation.
            width (int): The width of the module.
            height (int): The height of the module.
        """
        super().__init__(width, height, parent)
        self._operation = operation
        self._child_ops_parent = None
        self._log_container_id = None

        self._parent_id = f"parent_{self._operation_id}"
        self._is_loop_id = f"is_loop_{self._operation_id}"
        self._cpu_bound_id = f"cpu_bound_{self._operation_id}"
        self._parallel_id = f"parallel_{self._operation_id}"

        self._progress_id = f"progress_{self._operation_id}"
        self._result_id = f"result_{self._operation_id}"
        self._log_id = f"log_{self._operation_id}"

        self._left_panel_id = f"left_panel_{self._operation_id}"

    @property
    def operation(self) -> BaseOperation:
        """Returns the operation."""
        return self._operation

    async def initialize_gui(self) -> None:
        """Initializes resources and adds the update operation."""
        try:
            self._update_operation = await self._operation_control.operation_manager.create_operation(
                operation_type=UpdateMonitor, name="gui_OpModuleUpdate", action=self.update_gui)
            self._update_operation.is_ready = True
        except Exception as e:
            self._logger.error(e, self)
            self._operation.add_log_entry(f"Error creating task: {e}")

        self._operation.attach_gui_module(self)

    def draw(self) -> None:
        """Draws the GUI elements for the operation."""
        with dpg.group(parent=self._parent, tag=self._parent_id, horizontal=True,
                       height=max(int(self._height * 0.3), 120)):
            with dpg.child_window(border=False, width=int(self._width * 0.5), parent=self._parent_id,
                                  tag=f"description_{self._operation_id}"):
                left_aligned_input_field(label="Unique ID", tag=f"unique_id_{self._operation_id}",
                                         parent=f"description_{self._operation_id}",
                                         value=self._operation.unique_id, readonly=True)
                left_aligned_input_field(label="Runtime ID", tag=f"runtime_id_{self._operation_id}",
                                         parent=f"description_{self._operation_id}",
                                         value=self._operation.runtime_id, readonly=True)
                dpg.add_separator()
                left_aligned_input_field(label="Name", value=self._operation.name, tag=f"name_{self._operation_id}",
                                         parent=f"description_{self._operation_id}")

                left_aligned_input_field(label="Action", value=f"{self._operation.action}", multiline=True,
                                         tag=f"action_{self._operation_id}", parent=f"description_{self._operation_id}",
                                         readonly=False)

            with dpg.child_window(border=True, width=-1, parent=self._parent_id, tag=f"parameters_{self._operation_id}"):
                dpg.add_checkbox(label="Continuous/Loop", tag=self._is_loop_id,
                                 default_value=self._operation.is_loop,
                                 parent=f"parameters_{self._operation_id}")
                dpg.add_checkbox(label="CPU Bound", tag=self._cpu_bound_id,
                                 default_value=self._operation.is_cpu_bound,
                                 parent=f"parameters_{self._operation_id}")
                dpg.add_checkbox(label="Parallel Execution", tag=self._parallel_id,
                                 default_value=self._operation.parallel,
                                 parent=f"parameters_{self._operation_id}")

        with dpg.group(parent=self._parent, horizontal=True, tag=self._left_panel_id,
                       height=max(int(self._height * 0.6), 100)):

            with dpg.child_window(height=-1, width=int(self._width * 0.5), border=False,
                                  parent=self._left_panel_id):
                dpg.add_progress_bar(default_value=self._operation.progress[0],
                                     tag=self._progress_id, overlay=self._operation.progress[1].upper(), width=-1)

                button_width = int(((self._width * 0.4) - 45) / 3)
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Execute", callback=self.execute_operation, width=button_width)
                    dpg.add_button(label="Stop", callback=self.stop_operation, width=button_width)
                    dpg.add_button(label="Pause", callback=self.pause_operation, width=button_width)
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Resume", callback=self.resume_operation, width=button_width)
                    dpg.add_button(label="Reset", callback=self.reset_operation, width=button_width)

                dpg.add_button(label="Input & Output", callback=self.view_result, width=-1)
                dpg.add_button(label="Save as Template", callback=self._operation.save_operation_in_workspace,
                               user_data=self._operation, width=-1)

            with dpg.child_window(height=-1, width=-1, border=True):
                self._child_ops_parent = f"child_ops_{self._operation_id}"
                with dpg.group(tag=f"container_{self._operation_id}", width=-1):
                    if self._operation.parent_operation is not None:
                        left_aligned_button(label="Open Parent Operation", tag=f"open_parent_{self._operation_id}",
                                            parent=f"container_{self._operation_id}", callback=self._open_parent_operation,
                                            enabled=True, text=self._operation.parent_operation.name)
                        dpg.add_separator()

                    dpg.add_text("Child Operations")
                    with dpg.group(tag=self._child_ops_parent, parent=f"container_{self._operation_id}"):
                        if self._operation.inheritance:
                            for child_op in self._operation.inheritance:
                                with dpg.group(parent=self._child_ops_parent,
                                               tag=f"{child_op.runtime_id}_{self._operation_id}"):
                                    dpg.add_input_text(label="Child Operation Name", default_value=child_op.name,
                                                       readonly=True)
                                    dpg.add_input_text(label="Status", default_value=child_op.status, readonly=True)
                                    dpg.add_checkbox(label="Concurrent", default_value=child_op.parallel)
                                    dpg.add_button(label="Remove",
                                                   callback=lambda: self.remove_child_operation(child_op))

                    create_operation_module = CreateOperationModule(width=700,
                                                                    height=400,
                                                                    parent_operation=self._operation,
                                                                    parent=f"container_{self._operation_id}")
                    create_operation_module.draw_button(parent=f"container_{self._operation_id}",
                                                        label="Add Child Operation")

    def dict_to_listbox_items(self, dictionary) -> list[str]:
        """Converts a dictionary to a list of strings for use in a listbox."""
        return [f"{key}:\t{value}" for key, value in dictionary.items()]

    async def update_gui(self) -> None:
        """Updates the GUI with the current status and progress."""
        while True:

            if dpg.does_item_exist(self._progress_id):
                dpg.set_value(self._progress_id, self._operation.progress[0])
                dpg.configure_item(self._progress_id, overlay=self._operation.progress[1].upper())

            if dpg.does_item_exist(self._child_ops_parent):
                current_inherited_ops = len(self._operation.inheritance)
                children = dpg.get_item_children(self._child_ops_parent, slot=1)
                if len(children) != current_inherited_ops:
                    dpg.delete_item(self._child_ops_parent, children_only=True)
                    for child_op in self._operation.inheritance:
                        dpg.add_input_text(label="Child Operation Name", default_value=child_op.name, readonly=True,
                                           parent=self._child_ops_parent)
                        dpg.add_input_text(label="Status", default_value=child_op.status, readonly=True,
                                           parent=self._child_ops_parent)
                        dpg.add_checkbox(label="Parallel", default_value=child_op.parallel,
                                         parent=self._child_ops_parent)
                        dpg.add_button(label="Remove", callback=lambda: self.remove_child_operation(child_op),
                                       parent=self._child_ops_parent)
                    dpg.add_button(
                        label="Execute Inherited Operations",
                        callback=self._operation.execute_child_operations,
                        width=-1, parent=self._child_ops_parent
                    )

            if dpg.does_item_exist(self._is_loop_id):
                dpg.set_value(self._is_loop_id, self._operation.is_loop)

            if dpg.does_item_exist(self._cpu_bound_id):
                dpg.set_value(self._cpu_bound_id, self._operation.is_cpu_bound)

            await asyncio.sleep(0.005)

    async def execute_operation(self, sender: any, app_data: any, user_data: any) -> None:
        """Executes the operation."""
        try:
            self._operation.is_ready = True
        except Exception as e:
            self._logger.error(e, self)
            self._operation.status = "error"
            self._operation.add_log_entry(f"Error executing operation: {e}")

    async def stop_operation(self, sender: any, app_data: any, user_data: any) -> None:
        """Stops the operation."""
        if not self._operation.is_loop:
            try:
                await self._operation.stop()
            except Exception as e:
                self._logger.error(e, self)
                self._operation.status = "error"
                self._operation.add_log_entry(f"Error stopping operation: {e}")

    async def pause_operation(self, sender: any, app_data: any, user_data: any) -> None:
        """Pauses the operation."""
        if not self._operation.is_loop:
            try:
                await self._operation.pause()
            except Exception as e:
                self._logger.error(e, self)
                self._operation.status = "error"
                self._operation.add_log_entry(f"Error pausing operation: {e}")

    async def resume_operation(self, sender: any, app_data: any, user_data: any) -> None:
        """Resumes the operation."""
        if not self._operation.is_loop:
            try:
                await self._operation.resume()
            except Exception as e:
                self._logger.error(e, self)
                self._operation.status = "error"
                self._operation.add_log_entry(f"Error resuming operation: {e}")

    async def reset_operation(self, sender: any, app_data: any, user_data: any) -> None:
        """Resets the operation."""
        try:
            await self._operation.reset()
        except Exception as e:
            self._logger.error(e, self)
            self._operation.status = "error"
            self._operation.add_log_entry(f"Error resetting operation: {e}")

    async def view_result(self, sender: any, app_data: any, user_data: any) -> None:
        """Handles the event when the user clicks the 'View Result' button."""
        _result = await self._operation.get_results_from_memory()
        self._operation.add_log_entry(f"Result viewed: {_result}")

    async def add_child_operation(self, child_operation: BaseOperation) -> None:
        """Adds a child operation to the current operation."""
        await self._operation.add_child_operation(child_operation)

    async def remove_child_operation(self, child_operation: BaseOperation) -> None:
        """Removes a child operation from the current operation."""
        await self._operation.remove_child_operation(child_operation)

    async def _open_parent_operation(self, sender: any, app_data: any, user_data: any) -> None:
        """Opens the parent operation in the GUI."""

        def on_ok_button(_sender, _app_data, _user_data):
            dpg.delete_item(popup_id)

        parent_operation = self._operation.parent_operation
        if parent_operation:
            popup_id = dpg.generate_uuid()

            with dpg.window(label="Parent Operation", modal=True, tag=popup_id, width=self._width, height=self._height):
                parent_operation_gui = OperationModule(operation=parent_operation,
                                                       width=self._width, height=self._height, parent=popup_id)
                await parent_operation_gui.initialize_gui()
                dpg.add_button(label="Close", callback=on_ok_button)

            dpg.show_item(popup_id)
        else:
            popup_id = dpg.generate_uuid()
            with dpg.window(label="Info", modal=True, tag=popup_id, no_title_bar=True):
                dpg.add_text("No parent operation found.")
                dpg.add_button(label="OK", callback=on_ok_button)

            # Show the popup dialog
            dpg.show_item(popup_id)
            self._operation.add_log_entry("No parent operation found.")

    async def _update_async(self) -> None:
        """Performs async updates."""
        await self.update_gui()

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        """Resizes the GUI."""
        self.width = new_width
        self.height = new_height
        dpg.set_item_width(self._parent_id, new_width)
        dpg.set_item_height(self._parent_id, new_height)

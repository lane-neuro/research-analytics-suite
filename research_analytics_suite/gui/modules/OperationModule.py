"""
OperationModule

This module defines the OperationModule class, which is responsible for managing operations and their GUI representation
within the research analytics suite. It handles the initialization, starting, stopping, pausing, resuming, and
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
import uuid
from typing import Optional, Any
import dearpygui.dearpygui as dpg
from research_analytics_suite.operation_manager.operations.ABCOperation import ABCOperation
from research_analytics_suite.utils.CustomLogger import CustomLogger


class OperationModule:
    """A class to manage operations and their GUI representation."""

    def __init__(self, operation: ABCOperation, operation_control: Any, width: int, height: int):
        """
        Initializes the OperationModule with the given operation, control, and logger.

        Args:
            operation (ABCOperation): An instance of ABCOperation.
            operation_control: Control interface for operations.
            width (int): The width of the module.
            height (int): The height of the module.
        """
        self.operation = operation
        self.operation_control = operation_control
        self.width = int(width * 1.0)
        self.height = int(height * 1.0)
        self._logger = CustomLogger()
        self.update_operation = None
        self.unique_id = None
        self.log_id = None
        self.result_id = None
        self.persistent_id = None
        self.cpu_bound_id = None
        self.add_child_dialog_id = None

    async def initialize(self) -> None:
        """Initializes resources and adds the update operation."""
        self.initialize_resources()
        self.update_operation = await self.add_update_operation()

    def initialize_resources(self) -> None:
        """Initializes necessary resources and logs the event."""
        try:
            self.operation.attach_gui_module(self)
        except Exception as e:
            self._logger.error(e, self)

    async def add_update_operation(self) -> ABCOperation:
        """
        Adds an update operation to the operations manager.

        Returns:
            The created update operation or None if an error occurred.
        """
        try:
            operation = await self.operation_control.operation_manager.add_operation(
                operation_type=ABCOperation, name="gui_OperationUpdateTask", logger=self._logger,
                local_vars=self.operation_control.local_vars,
                func=self.update_gui, persistent=True)
            return operation
        except Exception as e:
            self._logger.error(e, self)
            self.operation.add_log_entry(f"Error creating task: {e}")

    async def start_operation(self, sender: Any, app_data: Any, user_data: Any) -> None:
        """Starts the operation."""
        if not self.operation.persistent:
            try:
                await self.operation.start()
            except Exception as e:
                self._logger.error(e, self)
                self.operation.status = "error"
                self.operation.add_log_entry(f"Error starting operation: {e}")

    async def stop_operation(self, sender: Any, app_data: Any, user_data: Any) -> None:
        """Stops the operation."""
        if not self.operation.persistent:
            try:
                await self.operation.stop()
            except Exception as e:
                self._logger.error(e, self)
                self.operation.status = "error"
                self.operation.add_log_entry(f"Error stopping operation: {e}")

    async def pause_operation(self, sender: Any, app_data: Any, user_data: Any) -> None:
        """Pauses the operation."""
        if not self.operation.persistent:
            try:
                await self.operation.pause()
            except Exception as e:
                self._logger.error(e, self)
                self.operation.status = "error"
                self.operation.add_log_entry(f"Error pausing operation: {e}")

    async def resume_operation(self, sender: Any, app_data: Any, user_data: Any) -> None:
        """Resumes the operation."""
        if not self.operation.persistent:
            try:
                await self.operation.resume()
            except Exception as e:
                self._logger.error(e, self)
                self.operation.status = "error"
                self.operation.add_log_entry(f"Error resuming operation: {e}")

    async def reset_operation(self, sender: Any, app_data: Any, user_data: Any) -> None:
        """Resets the operation."""
        try:
            await self.operation.reset()
        except Exception as e:
            self._logger.error(e, self)
            self.operation.status = "error"
            self.operation.add_log_entry(f"Error resetting operation: {e}")

    def draw(self, parent: int) -> None:
        """Draws the GUI elements for the operation."""
        with dpg.group(parent=parent, height=int(self.height * 0.14) - 2):
            self.unique_id = str(uuid.uuid4())
            self.log_id = f"log_{self.unique_id}"
            self.result_id = f"result_{self.unique_id}"
            self.persistent_id = f"persistent_{self.unique_id}"
            self.cpu_bound_id = f"cpu_bound_{self.unique_id}"

            # Section A: Details
            with dpg.child_window(height=-1, width=-1, border=True):
                dpg.add_text(f"Operation: {self.operation.name}")
                dpg.add_separator()

                with dpg.group(horizontal=True, width=-1, height=-1):
                    dpg.add_text(f"Status: {self.operation.status}",
                                 tag=f"status_{self.operation.name}_{self.unique_id}")
                    dpg.add_text(f"Persistent: {self.operation.persistent}", tag=self.persistent_id)
                    dpg.add_text(f"CPU Bound: {self.operation.is_cpu_bound}", tag=self.cpu_bound_id)

        with dpg.group(parent=parent, horizontal=True):

            # Section B: Interaction & Child Operations
            with dpg.child_window(height=int(self.height * 0.85) - 12, width=int(self.width * 0.4) - 15, border=True):
                dpg.add_progress_bar(
                    default_value=self.operation.progress[0] / 100,
                    tag=f"progress_{self.operation.name}_{self.unique_id}",
                    overlay="%.1f%%" % self.operation.progress[0],
                    width=-1)
                dpg.add_separator()

                # Interaction buttons
                button_width = int(((self.width * 0.4) - 45) / 3)
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Start", callback=self.start_operation, width=button_width)
                    dpg.add_button(label="Stop", callback=self.stop_operation, width=button_width)
                    dpg.add_button(label="Pause", callback=self.pause_operation, width=button_width)
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Resume", callback=self.resume_operation, width=button_width)
                    dpg.add_button(label="Reset", callback=self.reset_operation, width=button_width)
                dpg.add_separator()

                # Child Operations
                dpg.add_text("Child Operations:")
                if self.operation.child_operations:
                    for child_op in self.operation.child_operations:
                        dpg.add_text(f"Child Operation: {child_op.name} - Status: {child_op.status} - Concurrent: "
                                     f"{child_op.concurrent}")
                else:
                    dpg.add_button(label="Add Child Operation", callback=self.open_add_child_dialog, width=-1)

            # Section C: Logs & Results
            child_height = int((self.height * 0.85) * 0.5) - 18
            with dpg.child_window(height=int(self.height * 0.85) - 12, width=int(self.width * 0.6) - 10, border=True):
                logs_results_tag = f"logs_results_{self.unique_id}"
                with dpg.group(tag=logs_results_tag, width=-1, height=child_height):
                    with dpg.child_window(border=False, parent=logs_results_tag):
                        dpg.add_text("Logs")
                        dpg.add_separator()
                        log_container_id = f"log_container_{self.unique_id}"
                        with dpg.child_window(tag=log_container_id, width=-1, border=False):
                            for log in self.operation.operation_logs:
                                dpg.add_text(log, parent=log_container_id)

                    dpg.add_separator()

                    with dpg.child_window(border=False, parent=logs_results_tag):
                        # Section D: Results
                        dpg.add_text("Result")
                        dpg.add_separator()
                        dpg.add_input_text(tag=self.result_id, readonly=True, multiline=True, width=-1)
                        dpg.add_separator()
                        dpg.add_button(label="View Result", callback=self.view_result, width=-1)

    async def update_gui(self) -> None:
        """Updates the GUI with the current status and progress."""
        while True:
            if dpg.does_item_exist(f"status_{self.operation.name}_{self.unique_id}"):
                dpg.set_value(f"status_{self.operation.name}_{self.unique_id}", f"Status:  "
                                                                                f"{self.operation.status}\t\t")

            if dpg.does_item_exist(f"progress_{self.operation.name}_{self.unique_id}"):
                dpg.set_value(f"progress_{self.operation.name}_{self.unique_id}", self.operation.progress[0] / 100)
                dpg.configure_item(f"progress_{self.operation.name}_{self.unique_id}",
                                   overlay="%.1f%%" % self.operation.progress[0])

            if dpg.does_item_exist(self.log_id):
                dpg.set_value(self.log_id, list(reversed(self.operation.operation_logs)))

            if dpg.does_item_exist(self.result_id):
                result = self.operation.get_result()
                dpg.set_value(self.result_id, str(result))

            if dpg.does_item_exist(self.persistent_id):
                dpg.set_value(self.persistent_id, f"Persistent:  {self.operation.persistent}\t\t")

            if dpg.does_item_exist(self.cpu_bound_id):
                dpg.set_value(self.cpu_bound_id, f"CPU Bound:  {self.operation.is_cpu_bound}")

            await asyncio.sleep(0.05)

    def view_result(self, sender: Any, app_data: Any, user_data: Any) -> None:
        """Handles the event when the user clicks the 'View Result' button."""
        result = self.operation.get_result()
        self.operation.add_log_entry(f"Result viewed: {result}")

    def add_child_operation(self, child_operation: ABCOperation) -> None:
        """Adds a child operation to the current operation."""
        self.operation.add_child_operation(child_operation)

    def remove_child_operation(self, child_operation: ABCOperation) -> None:
        """Removes a child operation from the current operation."""
        self.operation.remove_child_operation(child_operation)

    def open_add_child_dialog(self, sender: Any, app_data: Any, user_data: Any) -> None:
        """Opens a dialog to add a child operation."""
        if self.add_child_dialog_id is None:
            self.add_child_dialog_id = dpg.generate_uuid()
            with dpg.window(label="Add Child Operation", modal=True, tag=self.add_child_dialog_id):
                dpg.add_input_text(label="Operation Name", tag="child_op_name")
                dpg.add_input_text(label="Function", tag="child_op_func")
                dpg.add_input_text(label="Local Vars", tag="child_op_local_vars", default_value="{}")
                dpg.add_checkbox(label="Persistent", tag="child_op_persistent")
                dpg.add_checkbox(label="CPU Bound", tag="child_op_cpu_bound")
                dpg.add_button(label="Add", callback=self.add_child_operation_from_dialog)
                dpg.add_button(label="Cancel", callback=lambda: dpg.hide_item(self.add_child_dialog_id))
        else:
            dpg.show_item(self.add_child_dialog_id)

    def add_child_operation_from_dialog(self, sender: Any, app_data: Any, user_data: Any) -> None:
        """Adds a child operation from the dialog inputs."""
        try:
            name = dpg.get_value("child_op_name")
            func = eval(dpg.get_value("child_op_func"))  # This assumes the input is a valid function
            local_vars = eval(dpg.get_value("child_op_local_vars"))  # This assumes the input is a valid dictionary
            persistent = dpg.get_value("child_op_persistent")
            is_cpu_bound = dpg.get_value("child_op_cpu_bound")

            new_child_op = ABCOperation(
                name=name,
                func=func,
                local_vars=local_vars,
                persistent=persistent,
                is_cpu_bound=is_cpu_bound
            )
            self.add_child_operation(new_child_op)
            dpg.hide_item(self.add_child_dialog_id)
        except Exception as e:
            self._logger.error(e, self)
            self.operation.add_log_entry(f"Error adding child operation: {e}")

"""
OperationModule

This module defines the OperationModule class, which is responsible for managing operations and their GUI representation
within the neurobehavioral analytics suite. It handles the initialization, starting, stopping, pausing, resuming, and
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
from neurobehavioral_analytics_suite.operation_manager.operations.ABCOperation import ABCOperation
from neurobehavioral_analytics_suite.utils.CustomLogger import CustomLogger


class OperationModule:
    """A class to manage operations and their GUI representation."""

    def __init__(self, operation: ABCOperation, operation_control: Any):
        """
        Initializes the OperationModule with the given operation, control, and logger.

        Args:
            operation (ABCOperation): An instance of ABCOperation.
            operation_control: Control interface for operations.
        """
        self.operation = operation
        self.operation_control = operation_control
        self._logger = CustomLogger()
        self.update_operation = None
        self.unique_id = None
        self.log_id = None
        self.result_id = None

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
        """
        Starts the operations.

        Args:
            sender: The sender of the start event.
            app_data: Additional application data.
            user_data: Additional user data.
        """
        try:
            await self.operation.start()
        except Exception as e:
            self._logger.error(e, self)
            self.operation.status = "error"
            self.operation.add_log_entry(f"Error starting operations: {e}")

    async def stop_operation(self, sender: Any, app_data: Any, user_data: Any) -> None:
        """
        Stops the operations.

        Args:
            sender: The sender of the stop event.
            app_data: Additional application data.
            user_data: Additional user data.
        """
        try:
            await self.operation.stop()
        except Exception as e:
            self._logger.error(e, self)
            self.operation.status = "error"
            self.operation.add_log_entry(f"Error stopping operations: {e}")

    async def pause_operation(self, sender: Any, app_data: Any, user_data: Any) -> None:
        """
        Pauses the operations.

        Args:
            sender: The sender of the pause event.
            app_data: Additional application data.
            user_data: Additional user data.
        """
        try:
            await self.operation.pause()
        except Exception as e:
            self._logger.error(e, self)
            self.operation.status = "error"
            self.operation.add_log_entry(f"Error pausing operations: {e}")

    async def resume_operation(self, sender: Any, app_data: Any, user_data: Any) -> None:
        """
        Resumes the operations.

        Args:
            sender: The sender of the resume event.
            app_data: Additional application data.
            user_data: Additional user data.
        """
        try:
            await self.operation.resume()
        except Exception as e:
            self._logger.error(e, self)
            self.operation.status = "error"
            self.operation.add_log_entry(f"Error resuming operations: {e}")

    async def reset_operation(self, sender: Any, app_data: Any, user_data: Any) -> None:
        """
        Resets the operations.

        Args:
            sender: The sender of the reset event.
            app_data: Additional application data.
            user_data: Additional user data.
        """
        try:
            await self.operation.reset()
        except Exception as e:
            self._logger.error(e, self)
            self.operation.status = "error"
            self.operation.add_log_entry(f"Error resetting operations: {e}")

    def draw(self, parent: int) -> None:
        """
        Draws the GUI elements for the operations.

        Args:
            parent (int): The parent GUI element to attach to.
        """
        with dpg.group(parent=parent):
            dpg.add_text(f"Operation: {self.operation.name}")
            self.unique_id = str(uuid.uuid4())
            self.log_id = f"log_{self.unique_id}"
            self.result_id = f"result_{self.unique_id}"
            dpg.add_text(f"Status: {self.operation.status}", tag=f"status_{self.operation.name}_{self.unique_id}")
            dpg.add_progress_bar(
                default_value=self.operation.progress[0] / 100,
                tag=f"progress_{self.operation.name}_{self.unique_id}",
                overlay="%.1f%%" % self.operation.progress[0],
                width=dpg.get_item_width(parent) - 20)
            with dpg.group(horizontal=True):
                dpg.add_button(label="Start", callback=self.start_operation)
                dpg.add_button(label="Stop", callback=self.stop_operation)
                dpg.add_button(label="Pause", callback=self.pause_operation)
                dpg.add_button(label="Resume", callback=self.resume_operation)
                dpg.add_button(label="Reset", callback=self.reset_operation)
            dpg.add_text("Logs:")
            dpg.add_listbox(items=self.operation.operation_logs, num_items=5, tag=self.log_id,
                            width=dpg.get_item_width(parent) - 25)
            dpg.add_text("Child Operations:")
            for child_op in self.operation.child_operations:
                dpg.add_text(f"Child Operation: {child_op.name} - Status: {child_op.status}")
            dpg.add_text("Result:")
            dpg.add_input_text(tag=self.result_id, readonly=True, multiline=True, width=dpg.get_item_width(parent) - 25)
            dpg.add_button(label="View Result", callback=self.view_result)

    async def update_gui(self) -> None:
        """Updates the GUI with the current status and progress."""
        while True:
            if dpg.does_item_exist(f"status_{self.operation.name}_{self.unique_id}"):
                dpg.set_value(f"status_{self.operation.name}_{self.unique_id}", f"Status: {self.operation.status}")
            if dpg.does_item_exist(f"progress_{self.operation.name}_{self.unique_id}"):
                dpg.set_value(f"progress_{self.operation.name}_{self.unique_id}", self.operation.progress[0] / 100)
                # dpg.set_item_overlay(f"progress_{self.operation.name}_{self.unique_id}", "%.1f%%" %
                # self.operation.progress[0])
            if dpg.does_item_exist(self.log_id):
                dpg.set_value(self.log_id, self.operation.operation_logs.__reversed__())
            if dpg.does_item_exist(self.result_id):
                result = self.operation.get_result()
                dpg.set_value(self.result_id, str(result))
            await asyncio.sleep(0.05)

    def add_child_operation(self, child_operation: ABCOperation) -> None:
        """
        Adds a child operation to the current operation.

        Args:
            child_operation (ABCOperation): The child operation to add.
        """
        self.operation.add_child_operation(child_operation)

    def remove_child_operation(self, child_operation: ABCOperation) -> None:
        """
        Removes a child operation from the current operation.

        Args:
            child_operation (ABCOperation): The child operation to remove.
        """
        self.operation.remove_child_operation(child_operation)

    def view_result(self, sender: Any, app_data: Any, user_data: Any) -> None:
        """
        Handles the event when the user clicks the "View Result" button.

        Args:
            sender: The sender of the event.
            app_data: Additional application data.
            user_data: Additional user data.
        """
        result = self.operation.get_result()
        self.operation.add_log_entry(f"Result viewed: {result}")
        # Additional actions to handle the result can be implemented here.

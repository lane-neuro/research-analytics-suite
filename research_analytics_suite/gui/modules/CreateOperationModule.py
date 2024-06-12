import uuid

import dearpygui.dearpygui as dpg
from typing import Any

from research_analytics_suite.operation_manager.operations.ABCOperation import ABCOperation
from research_analytics_suite.utils.CustomLogger import CustomLogger


class CreateOperationModule:
    """A class to create custom instances of ABCOperation with user-defined parameters."""

    def __init__(self, operation_control, width: int, height: int, parent_operation=None):
        self._logger = CustomLogger()
        self.operation_control = operation_control
        self._parent_operation = parent_operation
        self.width = width
        self.height = height
        self.create_operation_dialog_id = f"{uuid.uuid4()}"

        self._new_op_name = f"new_op_name_{self.create_operation_dialog_id}"
        self._new_op_func = f"new_op_func_{self.create_operation_dialog_id}"
        self._new_op_local_vars = f"new_op_local_vars_{self.create_operation_dialog_id}"
        self._new_op_persistent = f"new_op_persistent_{self.create_operation_dialog_id}"
        self._new_op_cpu_bound = f"new_op_cpu_bound_{self.create_operation_dialog_id}"
        self._new_op_concurrent = f"new_op_concurrent_{self.create_operation_dialog_id}"

    def draw_button(self, parent, label: str) -> None:
        """Draws the GUI elements for creating a new operation."""
        if dpg.does_item_exist(parent):
            dpg.add_button(label=label, callback=self.open_create_operation_dialog, parent=parent)

    def open_create_operation_dialog(self, sender: Any, app_data: Any) -> None:
        """Opens a dialog to create a new operation."""
        with dpg.window(label="Create New Operation", modal=True, tag=f"new_{self.create_operation_dialog_id}"):
            dpg.add_input_text(label="Operation Name", tag=self._new_op_name)
            dpg.add_input_text(label="Function Code", tag=self._new_op_func, multiline=True)
            dpg.add_input_text(label="Local Variables", tag=self._new_op_local_vars, default_value="{}")
            dpg.add_checkbox(label="Persistent", tag=self._new_op_persistent)
            dpg.add_checkbox(label="CPU Bound", tag=self._new_op_cpu_bound)
            dpg.add_checkbox(label="Concurrent", tag=self._new_op_concurrent)
            dpg.add_button(label="Create", callback=self.create_operation_from_dialog)
            dpg.add_button(label="Cancel", callback=lambda: dpg.hide_item(f"new_{self.create_operation_dialog_id}"))

    async def create_operation_from_dialog(self, sender: Any, app_data: Any, user_data: Any) -> None:
        """Creates a new operation from the dialog inputs."""
        try:
            name = dpg.get_value(self._new_op_name)
            func = dpg.get_value(self._new_op_func)
            local_vars = eval(dpg.get_value(self._new_op_local_vars))  # Assumes the input is a valid dictionary
            persistent = dpg.get_value(self._new_op_persistent)
            is_cpu_bound = dpg.get_value(self._new_op_cpu_bound)
            concurrent = dpg.get_value(self._new_op_concurrent)

            await self.operation_control.operation_manager.add_operation(
                operation_type=ABCOperation, name=name, func=func,
                local_vars=local_vars, persistent=persistent,
                is_cpu_bound=is_cpu_bound, concurrent=concurrent,
                parent_operation=self._parent_operation
            )
            dpg.hide_item(f"new_{self.create_operation_dialog_id}")
        except Exception as e:
            self._logger.error(e, self)
            self.operation_control.add_log_entry(f"Error creating new operation: {e}")

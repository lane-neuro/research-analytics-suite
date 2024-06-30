import dearpygui.dearpygui as dpg
from typing import Any

from research_analytics_suite.gui.GUIBase import GUIBase
from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation


class CreateOperationModule(GUIBase):
    """A class to create custom instances of BaseOperation with user-defined parameters."""

    def __init__(self, width: int, height: int, parent, parent_operation=None):
        super().__init__(width, height, parent)

        self._parent_operation = parent_operation

        self._new_op_name = f"new_op_name_{self._operation_id}"
        self._new_op_action = f"new_op_action_{self._operation_id}"
        self._new_op_persistent = f"new_op_persistent_{self._operation_id}"
        self._new_op_cpu_bound = f"new_op_cpu_bound_{self._operation_id}"
        self._new_op_concurrent = f"new_op_concurrent_{self._operation_id}"

    async def initialize_gui(self) -> None:
        pass

    async def _update_async(self) -> None:
        pass

    def draw(self) -> None:
        """Opens a dialog to create a new operation."""
        if dpg.does_item_exist(f"new_{self._operation_id}"):
            dpg.delete_item(f"new_{self._operation_id}")

        with dpg.window(label="Create New Operation", modal=True, tag=f"new_{self._operation_id}",
                        width=self.width, height=self.height):
            dpg.add_input_text(label="Operation Name", tag=self._new_op_name)
            dpg.add_input_text(label="Action", tag=self._new_op_action, multiline=True)
            dpg.add_checkbox(label="Persistent", tag=self._new_op_persistent)
            dpg.add_checkbox(label="CPU Bound", tag=self._new_op_cpu_bound)
            dpg.add_checkbox(label="Concurrent", tag=self._new_op_concurrent)
            dpg.add_button(label="Create", callback=self.create_operation_from_dialog)
            dpg.add_button(label="Cancel", callback=lambda: dpg.hide_item(f"new_{self._operation_id}"))

    def draw_button(self, parent, label: str, width=-1) -> None:
        """Draws the GUI elements for creating a new operation."""
        if dpg.does_item_exist(parent):
            dpg.add_button(label=label, callback=self.draw, parent=parent, width=width)

    async def create_operation_from_dialog(self, sender: Any, app_data: Any, user_data: Any) -> None:
        """Creates a new operation from the dialog inputs."""
        try:
            name = dpg.get_value(self._new_op_name)
            action = dpg.get_value(self._new_op_action)
            persistent = dpg.get_value(self._new_op_persistent)
            is_cpu_bound = dpg.get_value(self._new_op_cpu_bound)
            concurrent = dpg.get_value(self._new_op_concurrent)

            await self._operation_control.operation_manager.add_operation_with_parameters(
                operation_type=BaseOperation, name=name, action=action, persistent=persistent,
                is_cpu_bound=is_cpu_bound, concurrent=concurrent, parent_operation=self._parent_operation
            )
            dpg.hide_item(f"new_{self._operation_id}")
            dpg.delete_item(f"new_{self._operation_id}")
        except Exception as e:
            self._logger.error(e, self)

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        pass

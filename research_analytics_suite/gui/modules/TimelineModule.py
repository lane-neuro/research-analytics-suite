"""
TimelineModule

This module defines the TimelineModule class, which is responsible for managing a multi-layered timeline interface
where different OperationModule instances can be reordered via drag-and-drop within the Research Analytics Suite.

Author: Lane
"""
import asyncio
from typing import Optional, Any

import dearpygui.dearpygui as dpg
from uuid import uuid4
from research_analytics_suite.operation_manager.operations.ABCOperation import ABCOperation
from research_analytics_suite.utils.CustomLogger import CustomLogger


class TimelineModule:
    """A class to manage a multi-layered timeline interface for reordering OperationModule instances."""

    def __init__(self, operation_control, operation_queue, width: int, height: int):
        self.window = dpg.add_group(label="Timeline", parent="bottom_pane", tag="timeline_manager", horizontal=False)
        self._logger = CustomLogger()
        self.update_operation = None
        self.operation_control = operation_control
        self.width = width
        self.height = height
        self.operation_queue = operation_queue
        self.unique_id = str(uuid4())
        self.dragging_operation = None
        self.operation_elements = {}

    async def initialize_dialog(self) -> None:
        self.update_operation = await self.add_update_operation()

    async def add_update_operation(self) -> Optional[Any]:
        try:
            operation = await self.operation_control.operation_manager.add_operation(
                operation_type=ABCOperation, name="gui_TimelineUpdateTask",
                local_vars=self.operation_control.local_vars,
                func=self.draw_timeline, persistent=True, concurrent=True)
            return operation
        except Exception as e:
            self._logger.error(e, self)
        return None

    async def draw_timeline(self) -> None:
        if not dpg.does_item_exist(self.unique_id):
            dpg.add_child_window(tag=self.unique_id, width=self.width, height=self.height, border=True,
                                 parent="timeline_manager")

        while True:
            for layer_index, operation_chain in enumerate(self.operation_queue.queue):
                for idx, node in enumerate(operation_chain):
                    if not node.operation.name.startswith("gui_") and not node.operation.name.startswith("sys_"):
                        self.update_operation_element(node.operation, layer_index, idx)
            await asyncio.sleep(0.1)

    def update_operation_element(self, operation: ABCOperation, layer_index: int, idx: int) -> None:
        operation_id = f"operation_{operation.name}_{idx}_{layer_index}"

        if operation_id in self.operation_elements:
            dpg.set_value(self.operation_elements[operation_id]['text'], f"Operation {idx + 1}: {operation.name}")
        else:
            with dpg.group(horizontal=True, parent=self.unique_id):
                text_tag = dpg.add_text(f"Operation {idx + 1}: {operation.name}", tag=operation_id)
                dpg.add_button(label="Drag", callback=lambda: self.set_dragging_operation(operation, operation_id))
                dpg.add_button(label="Drop Here", callback=lambda: self.reorder_operations(layer_index, operation, idx))
                self.operation_elements[operation_id] = {'text': text_tag}

    def set_dragging_operation(self, operation: ABCOperation, operation_id: str) -> None:
        self.dragging_operation = (operation, operation_id)

    def reorder_operations(self, layer_index: int, operation: ABCOperation, new_index: int) -> None:
        if self.dragging_operation:
            dragged_operation, _ = self.dragging_operation
            operation_chain = self.operation_queue.queue[layer_index]
            if operation_chain.contains(dragged_operation):
                self.operation_queue.move_operation(dragged_operation, new_index)
            self.dragging_operation = None
            # Update UI after reordering
            self.update_all_elements()

    def update_all_elements(self) -> None:
        for layer_index, operation_chain in enumerate(self.operation_queue.queue):
            for idx, node in enumerate(operation_chain):
                if not node.operation.name.startswith("gui_"):
                    self.update_operation_element(node.operation, layer_index, idx)

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

from research_analytics_suite.gui.GUIBase import GUIBase
from research_analytics_suite.operation_manager.control.OperationControl import OperationControl
from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation
from research_analytics_suite.utils.CustomLogger import CustomLogger


class TimelineModule(GUIBase):
    """A class to manage a multi-layered timeline interface for reordering OperationModule instances."""

    def __init__(self, operation_sequencer, width: int, height: int, parent):
        super().__init__(width, height, parent)
        self._operation_sequencer = operation_sequencer
        self._dragging_operation = None
        self._operation_elements = {}

    async def initialize_gui(self) -> None:
        dpg.add_child_window(tag="sequencer_module", border=True, width=self.width, parent=self._parent)

        self._update_operation = await self._operation_control.operation_manager.add_operation_with_parameters(
                operation_type=BaseOperation, name="gui_TimelineUpdateTask",
                action=self._update_async, is_loop=True, parallel=True)
        self._update_operation.is_ready = True

    async def _update_async(self) -> None:
        while not dpg.does_item_exist(f"print_sequencer_module"):
            await asyncio.sleep(0.001)

        while True:
            await self.update_all_elements()
            await asyncio.sleep(0.001)

    def draw(self) -> None:
        dpg.add_button(label="Print Sequencer", callback=self._operation_sequencer.print_sequencer,
                       parent="sequencer_module", tag=f"print_sequencer_module")

    async def update_operation_element(self, operation: BaseOperation, layer_index: int, idx: int) -> None:
        operation_id = f"operation_{operation.name}_{idx}_{layer_index}"

        if operation_id in self._operation_elements:
            dpg.set_value(self._operation_elements[operation_id]['text'], f"Operation {idx + 1}: {operation.name}")
        else:
            with dpg.group(horizontal=True, parent=self._operation_id):
                text_tag = dpg.add_text(f"Operation {idx + 1}: {operation.name}", tag=operation_id)
                #dpg.add_button(label="Drag", callback=lambda: self.set_dragging_operation(operation, operation_id))
                #dpg.add_button(label="Drop Here", callback=lambda: self.reorder_operations(layer_index, operation, idx))
                self._operation_elements[operation_id] = {'text': text_tag}

    def set_dragging_operation(self, operation: BaseOperation, operation_id: str) -> None:
        self._dragging_operation = (operation, operation_id)

    def reorder_operations(self, layer_index: int, operation: BaseOperation, new_index: int) -> None:
        if self._dragging_operation:
            dragged_operation, _ = self._dragging_operation
            operation_chain = self._operation_sequencer.sequencer[layer_index]
            if operation_chain.contains(dragged_operation):
                self._operation_sequencer.move_operation(dragged_operation, new_index)
            self._dragging_operation = None

    async def update_all_elements(self) -> None:
        for layer_index, operation_chain in enumerate(self._operation_sequencer.sequencer):
            for idx, node in enumerate(operation_chain):
                if not node.operation.name.startswith("gui_") and not node.operation.name.startswith("sys_"):
                    await self.update_operation_element(node.operation, layer_index, idx)

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        pass

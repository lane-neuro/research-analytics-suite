"""
OperationManagerLayout Module

This module provides the main layout container that combines OperationTreeView and OperationDetailPanel
to create a comprehensive operation management interface.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import asyncio
from typing import Optional

import dearpygui.dearpygui as dpg

from research_analytics_suite.gui.GUIBase import GUIBase
from research_analytics_suite.gui.modules.OperationTreeView import OperationTreeView
from research_analytics_suite.gui.modules.OperationDetailPanel import OperationDetailPanel
from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation
from research_analytics_suite.operation_manager.operations.core.OperationAttributes import OperationAttributes


class OperationManagerLayout(GUIBase):
    """
    Main operation management layout combining tree view and detail panel.

    Provides a split-pane interface with operation tree on the left and
    detailed operation information on the right.
    """

    def __init__(self, width: int, height: int, parent: str):
        """
        Initialize the OperationManagerLayout.

        Args:
            width (int): Total width of the layout
            height (int): Total height of the layout
            parent (str): Parent container ID
        """
        super().__init__(width, height, parent)
        self._layout_id = f"op_manager_layout_{self._runtime_id}"
        self._splitter_id = f"splitter_{self._runtime_id}"

        # Layout proportions
        self._tree_width_ratio = 0.4
        self._min_tree_width = 350

        # Child components
        self._tree_view: Optional[OperationTreeView] = None
        self._detail_panel: Optional[OperationDetailPanel] = None

        # Current state
        self._selected_operation: Optional[BaseOperation] = None
        self._last_rendered_operation: Optional[BaseOperation] = None

    async def initialize_gui(self) -> None:
        """Initialize the layout and child components."""
        self._logger.debug("Initializing OperationManagerLayout")

        # Create tree view
        tree_container_id = f"tree_container_{self._runtime_id}"
        self._tree_view = OperationTreeView(
            width=-1,
            height=self.height,
            parent=tree_container_id,
            selection_callback=self._on_operation_selected
        )

        # Create detail panel
        detail_container_id = f"detail_container_{self._runtime_id}"
        self._detail_panel = OperationDetailPanel(
            width=self.width,
            height=self.height,
            parent=detail_container_id
        )

        # Initialize components
        await self._tree_view.initialize_gui()
        await self._detail_panel.initialize_gui()

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        """Resize the layout and child components."""
        self.width = new_width
        self.height = new_height

        if dpg.does_item_exist(self._layout_id):
            dpg.set_item_width(self._layout_id, new_width)
            dpg.set_item_height(self._layout_id, new_height)

        # Recalculate child component sizes
        if self._tree_view and self._detail_panel:
            actual_width = new_width if new_width > 0 else dpg.get_item_width(self._layout_id)
            tree_width = max(self._min_tree_width, int(actual_width * self._tree_width_ratio))
            detail_width = actual_width - tree_width

            await self._tree_view.resize_gui(tree_width, new_height)
            await self._detail_panel.resize_gui(detail_width, new_height)

    async def _update_async(self) -> None:
        """Required abstract method implementation - delegates to child components."""
        pass

    def draw(self) -> None:
        """Draw the operation manager layout."""
        with dpg.group(tag=self._layout_id, parent=self._parent, horizontal=True):
            actual_width = self.width
            tree_width = max(self._min_tree_width, int(actual_width * self._tree_width_ratio))
            detail_width = -1

            # Tree view container
            with dpg.child_window(tag=f"tree_container_{self._runtime_id}",
                                 width=tree_width,
                                 height=self.height,
                                 border=False):
                if self._tree_view:
                    self._tree_view.draw()

            # Detail panel container
            with dpg.child_window(tag=f"detail_container_{self._runtime_id}",
                                 width=detail_width,
                                 height=self.height,
                                 border=False):
                if self._detail_panel:
                    self._detail_panel.draw()

    def _on_operation_selected(self, operation: BaseOperation) -> None:
        """Handle operation selection from tree view."""
        self._selected_operation = operation

        # Only update detail panel if selection actually changed
        if self._selected_operation != self._last_rendered_operation:
            if self._detail_panel:
                self._detail_panel.set_operation(operation)
            self._last_rendered_operation = operation

        self._logger.debug(f"Selected operation: {operation.name if operation else 'None'}")

    async def add_operation(self, operation_attributes: OperationAttributes) -> None:
        """Add a new operation to the manager (triggers tree refresh)."""
        if self._tree_view:
            await self._tree_view.add_operation_to_tree(operation_attributes)

    def get_selected_operation(self) -> Optional[BaseOperation]:
        """Get the currently selected operation."""
        return self._selected_operation

    def clear_selection(self) -> None:
        """Clear the current operation selection."""
        self._selected_operation = None
        self._last_rendered_operation = None  # Force re-render on next selection
        if self._tree_view:
            self._tree_view.clear_selection()
        if self._detail_panel:
            self._detail_panel.clear_operation()

    async def refresh_operations(self) -> None:
        """Refresh the operation tree display."""
        if self._tree_view:
            await self._tree_view._refresh_tree()

    def get_tree_view(self) -> Optional[OperationTreeView]:
        """Get the tree view component."""
        return self._tree_view

    def get_detail_panel(self) -> Optional[OperationDetailPanel]:
        """Get the detail panel component."""
        return self._detail_panel

    async def cleanup(self) -> None:
        """Cleanup resources when layout is destroyed."""
        if self._tree_view and hasattr(self._tree_view, '_update_operation'):
            if self._tree_view._update_operation:
                await self._tree_view._update_operation.stop()

        if self._detail_panel and hasattr(self._detail_panel, '_update_operation'):
            if self._detail_panel._update_operation:
                await self._detail_panel._update_operation.stop()

        self._logger.debug("OperationManagerLayout cleanup completed")

    async def execute_selected_operation(self) -> bool:
        """Execute the currently selected operation."""
        if self._selected_operation:
            try:
                self._selected_operation.is_ready = True
                self._logger.info(f"Executing selected operation: {self._selected_operation.name}")
                return True
            except Exception as e:
                self._logger.error(f"Error executing selected operation: {e}")
        return False

    async def stop_selected_operation(self) -> bool:
        """Stop the currently selected operation."""
        if self._selected_operation:
            try:
                await self._selected_operation.stop()
                self._logger.info(f"Stopped selected operation: {self._selected_operation.name}")
                return True
            except Exception as e:
                self._logger.error(f"Error stopping selected operation: {e}")
        return False

    async def reset_selected_operation(self) -> bool:
        """Reset the currently selected operation."""
        if self._selected_operation:
            try:
                await self._selected_operation.reset()
                self._logger.info(f"Reset selected operation: {self._selected_operation.name}")
                return True
            except Exception as e:
                self._logger.error(f"Error resetting selected operation: {e}")
        return False

    def get_operation_count(self) -> int:
        """Get the total number of operations in the manager."""
        if not self._operation_control or not self._operation_control.operation_manager:
            return 0

        sequencer = self._operation_control.operation_manager.operation_sequencer
        if not sequencer:
            return 0

        count = 0
        for chain in sequencer.sequencer:
            current_node = chain.head
            while current_node:
                if current_node.operation:
                    count += 1
                current_node = current_node.next_node

        return count

    def get_operations_by_status(self, status: str) -> list:
        """Get all operations with a specific status."""
        if not self._operation_control or not self._operation_control.operation_manager:
            return []

        operations = []
        sequencer = self._operation_control.operation_manager.operation_sequencer
        if not sequencer:
            return operations

        for chain in sequencer.sequencer:
            current_node = chain.head
            while current_node:
                if current_node.operation and current_node.operation.status.lower() == status.lower():
                    operations.append(current_node.operation)
                current_node = current_node.next_node

        return operations
"""
OperationTreeView Module

This module provides a hierarchical tree view for managing operations. Displays operation chains from
OperationSequencer in a structured, expandable tree format with status indicators.

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
from typing import Dict, List, Optional, Callable

import dearpygui.dearpygui as dpg

from research_analytics_suite.gui.GUIBase import GUIBase
from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation
from research_analytics_suite.operation_manager.operations.core.OperationAttributes import OperationAttributes
from research_analytics_suite.operation_manager.operations.system.UpdateMonitor import UpdateMonitor


class OperationTreeView(GUIBase):
    """
    Hierarchical tree view for operation management.

    Provides expandable tree structure showing operation chains, status indicators,
    and quick action buttons. Integrates with OperationSequencer for chain management.
    """

    def __init__(self, width: int, height: int, parent: str, selection_callback: Optional[Callable] = None):
        """
        Initialize the OperationTreeView.

        Args:
            width (int): Width of the tree view
            height (int): Height of the tree view
            parent (str): Parent container ID
            selection_callback (Callable): Callback when operation is selected
        """
        super().__init__(width, height, parent)
        self._tree_id = f"operation_tree_{self._runtime_id}"
        self._search_id = f"search_{self._runtime_id}"
        self._filter_id = f"filter_{self._runtime_id}"
        self._selection_callback = selection_callback

        # Tree state management
        self._tree_nodes: Dict[str, str] = {}
        self._expanded_nodes: set = set()
        self._selected_operation: Optional[BaseOperation] = None
        self._selected_operation_runtime_id: Optional[str] = None

        self._update_operation: Optional[BaseOperation] = None

    async def initialize_gui(self) -> None:
        """Initialize GUI components and start update monitoring."""
        self._logger.debug("Initializing OperationTreeView")

        # Create update monitor for tree refreshing
        self._update_operation = await self._operation_control.operation_manager.create_operation(
            operation_type=UpdateMonitor,
            name=f"tree_update_{self._runtime_id}",
            action=self._update_async
        )
        self._update_operation.is_ready = True

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        """Resize the tree view."""
        self.width = new_width
        self.height = new_height
        if dpg.does_item_exist(self._tree_id):
            dpg.set_item_width(self._tree_id, new_width)
            dpg.set_item_height(self._tree_id, new_height - 60)  # Account for search bar

    def draw(self) -> None:
        """Draw the tree view interface."""
        with dpg.child_window(tag=f"tree_container_{self._runtime_id}",
                             parent=self._parent,
                             width=self.width,
                             height=self.height,
                             border=False):

            # Search and filter controls
            with dpg.group(horizontal=True, horizontal_spacing=10):
                dpg.add_input_text(
                    tag=self._search_id,
                    hint="Search operations...",
                    width=self.width - 120,
                    callback=self._on_search_change
                )
                dpg.add_button(
                    label="Refresh",
                    width=100,
                    callback=lambda: asyncio.create_task(self._refresh_tree())
                )

            dpg.add_separator()

            # Status filter checkboxes
            with dpg.group(horizontal=True, horizontal_spacing=15, width=-1):
                dpg.add_checkbox(label="Ready", default_value=True, tag=f"filter_ready_{self._runtime_id}")
                dpg.add_checkbox(label="Running", default_value=True, tag=f"filter_running_{self._runtime_id}")
                dpg.add_checkbox(label="Complete", default_value=True, tag=f"filter_complete_{self._runtime_id}")
                dpg.add_checkbox(label="Error", default_value=True, tag=f"filter_error_{self._runtime_id}")

            dpg.add_separator()

            with dpg.child_window(tag=self._tree_id,
                                 width=-1,
                                 height=-1,
                                 border=True):
                # Tree content will be populated by _refresh_tree
                pass

    async def _update_async(self) -> None:
        """Asynchronous update loop for tree refreshing."""
        while self._update_operation.is_ready:
            if dpg.does_item_exist(self._tree_id):
                await self._refresh_tree()
            await asyncio.sleep(1.0)

    async def _refresh_tree(self) -> None:
        """Refresh the entire tree structure."""
        if not dpg.does_item_exist(self._tree_id):
            return

        # Clear existing tree content
        dpg.delete_item(self._tree_id, children_only=True)
        self._tree_nodes.clear()

        # Get operation sequencer
        sequencer = self._operation_control.operation_manager.sequencer
        if not sequencer or sequencer.is_empty():
            dpg.add_text("No operations available", parent=self._tree_id, color=(128, 128, 128))
            return

        # Build tree from operation chains
        for chain_idx, chain in enumerate(sequencer.sequencer):
            if chain.head.operation.category_id == 0:
                continue  # Skip system chains

            chain_node_id = f"chain_{chain_idx}_{self._runtime_id}"

            with dpg.tree_node(tag=chain_node_id,
                              parent=self._tree_id,
                              label=f"Chain {chain_idx + 1}",
                              default_open=True):
                current_node = chain.head
                operation_idx = 0

                while current_node and current_node.operation:
                    operation = current_node.operation
                    await self._add_operation_node(operation, chain_node_id, operation_idx)
                    current_node = current_node.next_node
                    operation_idx += 1

    async def _add_operation_node(self, operation: BaseOperation, parent_id: str, index: int) -> None:
        """Add a single operation node to the tree."""
        if not self._should_show_operation(operation):
            return

        node_id = f"op_{operation.runtime_id}_{self._runtime_id}"
        self._tree_nodes[operation.runtime_id] = node_id

        # Create operation display label with status indicators
        label = self._create_operation_label(operation)

        with dpg.tree_node(tag=node_id,
                          parent=parent_id,
                          label=label,
                          leaf=True):

            # Operation details row
            with dpg.group(horizontal=True, horizontal_spacing=10):
                # Status indicator
                status_color = self._get_status_color(operation.status)
                dpg.add_text(f"Status: {operation.status}", color=status_color)

                # Execution flags
                if hasattr(operation, 'attributes'):
                    attrs = operation.attributes
                    if attrs.is_loop:
                        dpg.add_text("LOOP", color=(100, 200, 255))
                    if attrs.is_gpu_bound:
                        dpg.add_text("GPU", color=(255, 100, 100))
                    if attrs.parallel:
                        dpg.add_text("PARALLEL", color=(255, 200, 100))

            # Quick action buttons
            with dpg.group(horizontal=True, horizontal_spacing=5):
                if operation.status in ["ready", "waiting", "idle", "started"]:
                    dpg.add_button(
                        label="Execute",
                        width=60,
                        height=20,
                        callback=lambda: asyncio.create_task(self._execute_operation(operation))
                    )
                elif operation.status == "running":
                    dpg.add_button(
                        label="Stop",
                        width=60,
                        height=20,
                        callback=lambda: asyncio.create_task(self._stop_operation(operation))
                    )

                dpg.add_button(
                    label="Reset",
                    width=60,
                    height=20,
                    callback=lambda: asyncio.create_task(self._reset_operation(operation))
                )

                dpg.add_button(
                    label="Details",
                    width=60,
                    height=20,
                    callback=lambda: self._select_operation(operation)
                )

    def _create_operation_label(self, operation: BaseOperation) -> str:
        """Create display label for operation."""
        name = operation.name if hasattr(operation, 'name') else "Unknown"
        version = ""
        if hasattr(operation, 'attributes') and hasattr(operation.attributes, 'version'):
            version = f" v{operation.attributes.version}"
        return f"{name}{version}"

    def _get_status_color(self, status: str) -> tuple:
        """Get color for operation status."""
        status_colors = {
            "ready": (100, 255, 100),      # Green
            "running": (100, 150, 255),    # Blue
            "waiting": (255, 255, 100),    # Yellow
            "completed": (150, 150, 150),  # Gray
            "error": (255, 100, 100),      # Red
            "paused": (255, 150, 100),     # Orange
        }
        return status_colors.get(status.lower(), (200, 200, 200))

    def _should_show_operation(self, operation: BaseOperation) -> bool:
        """Check if operation should be shown based on filters."""
        # Search filter
        search_text = dpg.get_value(self._search_id) if dpg.does_item_exist(self._search_id) else ""
        if search_text and search_text.lower() not in operation.name.lower():
            return False

        # Status filter
        status = operation.status.lower()
        filter_checks = {
            "ready": f"filter_ready_{self._runtime_id}",
            "running": f"filter_running_{self._runtime_id}",
            "completed": f"filter_complete_{self._runtime_id}",
            "error": f"filter_error_{self._runtime_id}"
        }

        filter_tag = filter_checks.get(status)
        if filter_tag and dpg.does_item_exist(filter_tag):
            return dpg.get_value(filter_tag)

        return True

    def _on_search_change(self, sender, app_data, user_data):
        """Handle search text changes."""
        asyncio.create_task(self._refresh_tree())

    def _select_operation(self, operation: BaseOperation) -> None:
        """Select an operation with exclusive selection behavior."""
        current_runtime_id = operation.runtime_id

        # Unselect previously selected operation (visual state)
        prev_runtime_id = self._selected_operation_runtime_id
        if prev_runtime_id and prev_runtime_id != current_runtime_id:
            # Add visual deselection
            pass

        # Update selection state
        self._selected_operation = operation
        self._selected_operation_runtime_id = current_runtime_id

        # Trigger callback for detail panel update
        if self._selection_callback:
            self._selection_callback(operation)

        self._logger.debug(f"Selected operation: {operation.name} [{current_runtime_id}]")

    async def _execute_operation(self, operation: BaseOperation) -> None:
        """Execute the selected operation."""
        try:
            operation.is_ready = True
            self._logger.info(f"Starting execution of operation: {operation.name}")
        except Exception as e:
            self._logger.error(f"Error executing operation {operation.name}: {e}")

    async def _stop_operation(self, operation: BaseOperation) -> None:
        """Stop the selected operation."""
        try:
            await operation.stop()
            self._logger.info(f"Stopped operation: {operation.name}")
        except Exception as e:
            self._logger.error(f"Error stopping operation {operation.name}: {e}")

    async def _reset_operation(self, operation: BaseOperation) -> None:
        """Reset the selected operation."""
        try:
            await operation.reset()
            self._logger.info(f"Reset operation: {operation.name}")
        except Exception as e:
            self._logger.error(f"Error resetting operation {operation.name}: {e}")

    def get_selected_operation(self) -> Optional[BaseOperation]:
        """Get the currently selected operation."""
        return self._selected_operation

    async def add_operation_to_tree(self, operation_attributes: OperationAttributes) -> None:
        """Add a new operation to the tree."""
        # This will be handled by the next tree refresh
        await self._refresh_tree()

    def clear_selection(self) -> None:
        """Clear the current selection."""
        self._selected_operation = None
        self._selected_operation_runtime_id = None
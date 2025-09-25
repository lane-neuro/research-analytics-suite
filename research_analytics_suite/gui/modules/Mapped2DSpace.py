"""
Mapped2DSpace Module

This module now serves as a wrapper around the new OperationManagerLayout,
maintaining backward compatibility while providing the improved hierarchical interface.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype - Refactored to use OperationManagerLayout
"""
import asyncio

import dearpygui.dearpygui as dpg
from research_analytics_suite.gui.GUIBase import GUIBase
from research_analytics_suite.gui.modules.OperationManagerLayout import OperationManagerLayout
from research_analytics_suite.operation_manager.operations.core.OperationAttributes import OperationAttributes


class Mapped2DSpace(GUIBase):
    """
    Mapped2DSpace class now uses the new OperationManagerLayout for improved operation management.

    This class maintains backward compatibility with existing code while providing
    the new hierarchical tree-based interface internally.
    """
    _lock = asyncio.Lock()

    def __init__(self, width: int, height: int, parent):
        """
        Initialize the Mapped2DSpace class with new OperationManagerLayout.

        Args:
            width (int): The width of the space.
            height (int): The height of the space.
            parent (Any): The parent object.
        """
        super().__init__(width, height, parent)

        # New operation manager layout
        self._operation_manager_layout = None

    async def initialize_gui(self) -> None:
        """
        Initialize the GUI using the new OperationManagerLayout.
        """
        # Create and initialize the new operation manager layout
        container_id = f"mapped_space_container_{self._runtime_id}"
        self._operation_manager_layout = OperationManagerLayout(
            width=self.width,
            height=self.height,
            parent=container_id
        )

        await self._operation_manager_layout.initialize_gui()

    async def _update_async(self) -> None:
        pass

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        """Resize the GUI components."""
        self.width = new_width
        self.height = new_height

        if self._operation_manager_layout:
            await self._operation_manager_layout.resize_gui(new_width, new_height)

    def add_node(self, operation_attributes: OperationAttributes) -> None:
        """
        Add an operation to the hierarchical manager.

        Creates an actual BaseOperation from the attributes and adds it to the operation manager,
        then adds it to the hierarchical display.

        Args:
            operation_attributes (OperationAttributes): The operation attributes
        """
        asyncio.create_task(self._create_and_add_operation(operation_attributes))

    async def _create_and_add_operation(self, operation_attributes: OperationAttributes) -> None:
        """Create and register a new operation from attributes."""
        try:
            # Set attributes as active for proper initialization
            operation_attributes.active = True

            # Create BaseOperation from attributes
            from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation
            operation = BaseOperation(operation_attributes)

            # Initialize the operation
            await operation.initialize_operation()

            # Add to operation manager (this handles sequencer registration)
            operation = await self._operation_control.operation_manager.add_initialized_operation(operation)

            # Refresh the tree display to show the new operation
            if self._operation_manager_layout:
                await self._operation_manager_layout.refresh_operations()

            self._logger.info(f"Created and added operation: {operation.name}")

        except Exception as e:
            self._logger.error(f"Error creating operation from attributes: {e}")

    def draw(self) -> None:
        """
        Draw the new operation manager layout.
        """
        with dpg.child_window(tag=f"mapped_space_container_{self._runtime_id}",
                             parent=self._parent,
                             width=self.width,
                             height=self.height,
                             border=False):
            if self._operation_manager_layout:
                self._operation_manager_layout.draw()

    def clear_elements(self):
        """
        Clear all elements from the operation manager.
        """
        if self._operation_manager_layout:
            self._operation_manager_layout.clear_selection()

    def get_operation_manager_layout(self) -> OperationManagerLayout:
        """Get the underlying OperationManagerLayout instance."""
        return self._operation_manager_layout

    def get_selected_operation(self):
        """Get the currently selected operation."""
        if self._operation_manager_layout:
            return self._operation_manager_layout.get_selected_operation()
        return None

    async def refresh_operations(self):
        """Refresh the operation display."""
        if self._operation_manager_layout:
            await self._operation_manager_layout.refresh_operations()

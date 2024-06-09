"""
OperationManagerDialog Module.

This module defines the OperationManagerDialog class, which is responsible for managing the dialog for displaying and
controlling operations within the neurobehavioral analytics suite. It initializes the operation manager dialog, adds new
operation tiles, and handles the resizing of the GUI.

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
from typing import Optional, Any
import dearpygui.dearpygui as dpg
from neurobehavioral_analytics_suite.gui.modules.OperationModule import OperationModule
from neurobehavioral_analytics_suite.operation_manager.OperationControl import OperationControl
from neurobehavioral_analytics_suite.operation_manager.operations.ABCOperation import ABCOperation
from neurobehavioral_analytics_suite.utils.CustomLogger import CustomLogger


class OperationManagerDialog:
    """A class to manage the dialog for displaying and controlling operations."""

    SLEEP_DURATION = 0.05
    TILE_WIDTH = 530  # Fixed width for each operation tile
    TILE_HEIGHT = 470  # Fixed height for each operation tile
    TILE_PADDING = 20  # Padding between tiles

    def __init__(self, operation_control: OperationControl, container_width: int = 1700):
        """
        Initializes the OperationManagerDialog with the given operation control, logger, and container width.

        Args:
            operation_control (OperationControl): Control interface for operations.
            container_width (int): Initial width of the container.
        """
        self.window = dpg.add_group(label="Operation Manager", parent="operation_pane", tag="operation_gallery",
                                    horizontal=False)
        self.operation_control = operation_control
        self._logger = CustomLogger()
        self.operation_items = {}  # Store operation GUI items
        self.update_operation = None
        self.container_width = container_width
        self.tiles_per_row = self.calculate_tiles_per_row(container_width)
        self.current_row_group = None

    def calculate_tiles_per_row(self, width: int) -> int:
        """
        Calculates the number of tiles per row based on the container width.

        Args:
            width (int): Width of the container.

        Returns:
            int: Number of tiles that fit in the given width.
        """
        return max(1, width // (self.TILE_WIDTH + self.TILE_PADDING))

    async def initialize_dialog(self) -> None:
        """Initializes the operation manager dialog by adding the update operation."""
        self.update_operation = await self.add_update_operation()
        dpg.set_viewport_resize_callback(self.on_resize)

    async def add_update_operation(self) -> Optional[Any]:
        """
        Adds an update operations to the operations manager.

        Returns:
            Operation: The created update operations or None if an error occurred.
        """
        try:
            operation = await self.operation_control.operation_manager.add_operation(
                operation_type=ABCOperation, name="gui_OperationManagerUpdateTask",
                local_vars=self.operation_control.local_vars,
                func=self.display_operations, persistent=True, concurrent=True)
            return operation
        except Exception as e:
            self._logger.error(e, self)
        return None

    async def display_operations(self) -> None:
        """Continuously checks for new operations and displays them in the GUI."""
        while True:
            queue_copy = set(self.operation_control.queue.queue)
            for operation_chain in queue_copy:
                for node in operation_chain:
                    if node.operation not in self.operation_items and node.operation.name != "gui_OperationUpdateTask":
                        self.operation_items[node.operation] = OperationModule(node.operation, self.operation_control,
                                                                               self.TILE_WIDTH, self.TILE_HEIGHT)
                        await self.operation_items[node.operation].initialize()
                        self.add_operation_tile(node.operation)
            await asyncio.sleep(self.SLEEP_DURATION)

    def add_operation_tile(self, operation: ABCOperation) -> None:
        """
        Adds a new operations tile to the GUI.

        Args:
            operation (CustomOperation): The operations to add as a tile.
        """
        if (self.current_row_group is None
                or len(dpg.get_item_children(self.current_row_group)[1]) >= self.tiles_per_row):
            self.current_row_group = dpg.add_group(horizontal=True, parent=self.window)
            self._logger.debug(f"Created new row group: {self.current_row_group}")
        child_window = dpg.add_child_window(width=self.TILE_WIDTH, height=self.TILE_HEIGHT,
                                            parent=self.current_row_group)
        self._logger.debug(f"Created child window: {child_window} in row group: {self.current_row_group}")
        self.operation_items[operation].draw(parent=child_window)

    def on_resize(self, sender: str, data: dict) -> None:
        """
        Handles the resize event and adjusts the number of tiles per row.

        Args:
            sender (str): The sender of the event.
            data (dict): The data associated with the event.
        """
        new_width = dpg.get_viewport_client_width() - 220
        new_tiles_per_row = self.calculate_tiles_per_row(new_width)
        if new_tiles_per_row != self.tiles_per_row:
            self.tiles_per_row = new_tiles_per_row
            self.refresh_display()

    def refresh_display(self) -> None:
        """Refreshes the display to adjust the tiles per row."""
        dpg.delete_item(self.window, children_only=True)
        self.current_row_group = None
        for operation in self.operation_items.values():
            self.add_operation_tile(operation.operation)

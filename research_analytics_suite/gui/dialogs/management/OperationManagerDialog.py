"""
OperationManagerDialog Module.

This module defines the OperationManagerDialog class, which is responsible for managing the dialog for displaying and
controlling operations within the research analytics suite. It initializes the operation manager dialog, adds new
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

from research_analytics_suite.data_engine.Config import Config
from research_analytics_suite.gui.modules.CreateOperationModule import CreateOperationModule
from research_analytics_suite.gui.modules.OperationModule import OperationModule
from research_analytics_suite.operation_manager.control.OperationControl import OperationControl
from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation
from research_analytics_suite.utils.CustomLogger import CustomLogger


class OperationManagerDialog:
    """A class to manage the dialog for displaying and controlling operations."""

    SLEEP_DURATION = 0.05
    TILE_WIDTH = 450  # Fixed width for each operation tile
    TILE_HEIGHT = 450  # Fixed height for each operation tile
    TILE_PADDING = 20  # Padding between tiles

    def __init__(self, container_width: int = 1700):
        """
        Initializes the OperationManagerDialog with the given operation control, logger, and container width.

        Args:
            container_width (int): Initial width of the container.
        """
        self.window = None
        self.create_operation_module = CreateOperationModule(height=400, width=800,
                                                             parent_operation=None)
        self._config = Config()
        self.operation_control = OperationControl()
        self._logger = CustomLogger()
        self.operation_items = dict[BaseOperation.runtime_id, OperationModule]()
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
        dpg.add_text("Operation Manager", parent="right_pane")
        self.create_operation_module.draw_button(label="Create New Operation", width=200, parent="right_pane")
        dpg.add_button(label="Load Operation from File", width=200, parent="right_pane",
                       callback=self.load_operation)
        self.window = dpg.add_group(parent="right_pane", tag="operation_gallery",
                                    horizontal=False)
        dpg.set_viewport_resize_callback(self.on_resize)

    async def add_update_operation(self) -> Optional[Any]:
        """
        Adds an update operations to the operations manager.

        Returns:
            Operation: The created update operations or None if an error occurred.
        """
        try:
            self._logger.debug("Adding update operation...")
            operation = await self.operation_control.operation_manager.add_operation_with_parameters(
                operation_type=BaseOperation, name="gui_OperationManagerUpdateTask",
                action=self.display_operations, persistent=True, concurrent=True)
            operation.is_ready = True
            self._logger.debug(f"Update operation added: {operation}")
            return operation
        except Exception as e:
            self._logger.error(e, self)
        return None

    async def display_operations(self) -> None:
        """Continuously checks for new operations and displays them in the GUI."""
        while True:
            sequencer_copy = set(self.operation_control.sequencer.sequencer)
            self._logger.debug(f"Current operations in sequencer: {len(sequencer_copy)} chains")

            for operation_chain in sequencer_copy:
                for node in operation_chain:
                    self._logger.debug(f"Checking operation: {node.operation.name} with runtime_id: {node.operation.runtime_id}")

                    # Debugging conditions
                    if node.operation.runtime_id in self.operation_items.keys():
                        self._logger.debug(f"Operation {node.operation.name} with runtime_id: {node.operation.runtime_id} is already in operation_items.")
                    if node.operation.name == "gui_OperationManagerUpdateTask":
                        self._logger.debug(f"Operation {node.operation.name} with runtime_id: {node.operation.runtime_id} is gui_OperationManagerUpdateTask.")
                    if node.operation.name.startswith("gui_") or node.operation.name.startswith("sys_"):
                        self._logger.debug(f"Operation {node.operation.name} with runtime_id: {node.operation.runtime_id} starts with gui_ or sys_.")

                    # Condition to add operations
                    if (node.operation.runtime_id not in self.operation_items.keys()
                            and node.operation.name != "gui_OperationManagerUpdateTask"
                            and not node.operation.name.startswith("gui_")
                            and not node.operation.name.startswith("sys_")):
                        self._logger.info(f"Adding operation to display: {node.operation.name} with runtime_id: {node.operation.runtime_id}")
                        self._logger.debug(f"Adding operation to display: {node.operation.name} with runtime_id: {node.operation.runtime_id}")
                        self.operation_items[node.operation.runtime_id] = OperationModule(operation=node.operation,
                                                                                          width=self.TILE_WIDTH,
                                                                                          height=self.TILE_HEIGHT)
                        await self.operation_items[node.operation.runtime_id].initialize()
                        await self.add_operation_tile(node.operation)
            await asyncio.sleep(self.SLEEP_DURATION)
            self._logger.debug("Display operations loop sleeping...")

    async def add_operation_tile(self, operation: 'BaseOperation') -> None:
        """
        Adds a new operations tile to the GUI.

        Args:
            operation (BaseOperation): The operations to add as a tile.
        """
        if (self.current_row_group is None
                or len(dpg.get_item_children(self.current_row_group)[1]) >= self.tiles_per_row):
            self.current_row_group = dpg.add_group(horizontal=True, parent=self.window)
            self._logger.debug(f"Created new row group: {self.current_row_group}")
            self._logger.debug(f"Created new row group: {self.current_row_group}")

        tag = f"{operation.runtime_id}_tile"
        self._logger.debug(f"Creating child window for operation: {operation.name} with tag: {tag}")
        self._logger.debug(f"Creating child window for operation: {operation.name} with tag: {tag}")
        child_window = dpg.add_child_window(width=self.TILE_WIDTH, height=self.TILE_HEIGHT,
                                            parent=self.current_row_group, tag=tag)
        self._logger.debug(f"Created child window: {child_window} in row group: {self.current_row_group}")
        self._logger.debug(f"Created child window: {child_window} in row group: {self.current_row_group}")
        await self.operation_items[operation.runtime_id].draw(parent=tag)

    def load_operation(self, sender: str, data: dict) -> None:
        """Loads operations from a file."""
        if dpg.does_item_exist("selected_file"):
            dpg.delete_item("selected_file")

        with dpg.file_dialog(show=True,
                             default_path=f"{self._config.BASE_DIR}/{self._config.WORKSPACE_NAME}/"
                                          f"{self._config.WORKSPACE_OPERATIONS_DIR}",
                             callback=self.load_operation_callback, tag="selected_file",
                             width=500, height=500, modal=True):
            dpg.add_file_extension(".json", color=(255, 255, 255, 255))

    def load_operation_callback(self, sender: str, data: dict) -> None:
        """
        Callback function for loading operations from a file.

        Args:
            sender (str): The sender of the event.
            data (dict): The data associated with the event.
        """
        asyncio.run(self._load_operation(data))

    async def _load_operation(self, data: dict) -> None:
        """
        Loads the operation from the selected file asynchronously.

        Args:
            data (dict): The data associated with the event.
        """
        _file_path = data["file_path_name"]
        if not _file_path:
            self._logger.error(Exception("No file selected."), self)
            return

        self._logger.info(f"Loading operation from file: {_file_path}")
        self._logger.debug(f"Loading operation from file: {_file_path}")

        loaded_operations = dict[BaseOperation.runtime_id, 'BaseOperation']()
        try:
            await BaseOperation.load_operation_group(_file_path, loaded_operations)
            self._logger.debug(f"Loaded operations: {loaded_operations}")
        except Exception as e:
            self._logger.error(e, self)
            self._logger.debug(f"Error loading operations from file: {e}")
            return

        # Uncomment and adjust if needed
        # try:
        #     for operation in loaded_operations.values():
        #         await self.operation_control.operation_manager.add_initialized_operation(operation)
        # except Exception as e:
        #     self._logger.error(e, self)
        #     return

        await self.refresh_display()
        self._logger.debug("Display refreshed after loading operations.")

    async def on_resize(self, sender: str, data: dict) -> None:
        """
        Handles the resize event and adjusts the number of tiles per row.

        Args:
            sender (str): The sender of the event.
            data (dict): The data associated with the event.
        """
        new_width = 1  # dpg.get_viewport_width()
        new_tiles_per_row = self.calculate_tiles_per_row(new_width)
        if new_tiles_per_row != self.tiles_per_row:
            self.tiles_per_row = new_tiles_per_row
            await self.refresh_display()

    async def refresh_display(self) -> None:
        """Refreshes the display to adjust the tiles per row."""
        self._logger.debug("Refreshing display...")
        dpg.delete_item(self.window, children_only=True)
        self.current_row_group = None
        for operation_module in self.operation_items.values():
            await self.add_operation_tile(operation_module.operation)
        self._logger.debug("Display refreshed.")

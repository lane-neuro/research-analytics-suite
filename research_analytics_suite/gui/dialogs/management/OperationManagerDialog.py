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
import dearpygui.dearpygui as dpg

from research_analytics_suite.gui.GUIBase import GUIBase
from research_analytics_suite.gui.modules.OperationModule import OperationModule
from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation


class OperationManagerDialog(GUIBase):
    """A class to manage the dialog for displaying and controlling operations."""

    SLEEP_DURATION = 0.05
    TILE_WIDTH = 450  # Fixed width for each operation tile
    TILE_HEIGHT = 450  # Fixed height for each operation tile
    TILE_PADDING = 20  # Padding between tiles

    def __init__(self, width: int, height: int, parent):
        """
        Initializes the OperationManagerDialog with the given operation control, logger, and container width.

        Args:
            width (int): Initial width of the container.
            height (int): Initial height of the container.
            parent: Parent container
        """
        super().__init__(width, height, parent)
        self.operation_items = {}
        self.tiles_per_row = self.calculate_tiles_per_row(width)
        self.current_row_group = None
        self.window = None
        self._create_operation_module = None

    def calculate_tiles_per_row(self, width: int) -> int:
        """
        Calculates the number of tiles per row based on the container width.

        Args:
            width (int): Width of the container.

        Returns:
            int: Number of tiles that fit in the given width.
        """
        return max(1, width // (self.TILE_WIDTH + self.TILE_PADDING))

    async def initialize_gui(self) -> None:
        """Initializes the operation manager dialog by adding the update operation."""
        self._update_operation = await self._operation_control.operation_manager.add_operation_with_parameters(
                operation_type=BaseOperation, name="gui_OperationManagerUpdateTask",
                action=self._update_async, persistent=True, concurrent=True)
        self._update_operation.is_ready = True
        # dpg.set_viewport_resize_callback(lambda: asyncio.create_task(self.on_resize()))

    def draw(self) -> None:
        """Draws the GUI elements for the operation manager dialog."""
        dpg.add_text("Operation Manager", parent=self._parent)

        from research_analytics_suite.gui import CreateOperationModule
        self._create_operation_module = CreateOperationModule(height=400, width=800,
                                                              parent_operation=None, parent=self._parent)
        self._create_operation_module.draw_button(label="Create New Operation", width=200, parent=self._parent)

        dpg.add_button(label="Load Operation from File", width=200, parent=self.parent, callback=self.load_operation)
        self.window = dpg.add_group(parent=self.parent, tag="operation_gallery", horizontal=False)

    async def _update_async(self) -> None:
        """Continuously checks for new operations and displays them in the GUI."""
        while True:
            sequencer_copy = set(self._operation_control.sequencer.sequencer)
            self._logger.debug(f"Current operations in sequencer: {len(sequencer_copy)} chains")

            for operation_chain in sequencer_copy:
                for node in operation_chain:
                    self._logger.debug(f"Checking operation: {node.operation.name} with runtime_id: "
                                       f"{node.operation.runtime_id}")

                    # Debugging conditions
                    if node.operation.runtime_id in self.operation_items.keys():
                        self._logger.debug(f"Operation {node.operation.name} with runtime_id: "
                                           f"{node.operation.runtime_id} is already in operation_items.")
                    if node.operation.name == "gui_OperationManagerUpdateTask":
                        self._logger.debug(f"Operation {node.operation.name} with runtime_id: "
                                           f"{node.operation.runtime_id} is gui_OperationManagerUpdateTask.")
                    if node.operation.name.startswith("gui_") or node.operation.name.startswith("sys_"):
                        self._logger.debug(f"Operation {node.operation.name} with runtime_id: "
                                           f"{node.operation.runtime_id} starts with gui_ or sys_.")

                    # Condition to add operations
                    if (node.operation.runtime_id not in self.operation_items.keys()
                            and node.operation.name != "gui_OperationManagerUpdateTask"
                            and not node.operation.name.startswith("gui_")
                            and not node.operation.name.startswith("sys_")):
                        self._logger.debug(f"Adding operation to display: {node.operation.name} with runtime_id: "
                                           f"{node.operation.runtime_id}")
                        await self.add_operation_tile(node.operation)
            await asyncio.sleep(self.SLEEP_DURATION)
            self._logger.debug("Display operations loop sleeping...")

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        """Handles the resize event and adjusts the number of tiles per row."""
        self.width = new_width
        self.height = new_height
        new_tiles_per_row = self.calculate_tiles_per_row(new_width)
        if new_tiles_per_row != self.tiles_per_row:
            self.tiles_per_row = new_tiles_per_row
            await self.refresh_display()

    async def add_operation_tile(self, operation: 'BaseOperation') -> None:
        """
        Adds a new operations tile to the GUI.

        Args:
            operation (BaseOperation): The operations to add as a tile.
        """
        if (self.current_row_group is None
                or len(dpg.get_item_children(self.current_row_group)[1]) >= self.tiles_per_row):
            self.current_row_group = dpg.add_group(horizontal=True, parent=self._parent)
            self._logger.debug(f"Created new row group: {self.current_row_group}")

        tag = f"{operation.runtime_id}_tile"
        self._logger.debug(f"Creating child window for operation: {operation.name} with tag: {tag}")
        child_window = dpg.add_child_window(width=self.TILE_WIDTH, height=self.TILE_HEIGHT,
                                            parent=self.current_row_group, tag=tag)
        self._logger.debug(f"Created child window: {child_window} in row group: {self.current_row_group}")

        self.operation_items[operation.runtime_id] = OperationModule(
            operation=operation, width=self.TILE_WIDTH, height=self.TILE_HEIGHT, parent=tag)
        await self.operation_items[operation.runtime_id].initialize_gui()

        self.operation_items[operation.runtime_id].draw()

    async def operation_preview_tile(self, file_name: str):
        """
        Creates a preview tile for the operation.

        Args:
            file_name (str): The name of the file.
        """
        self._logger.debug(f"Creating operation preview tile for file: {file_name}")

        from research_analytics_suite.operation_manager.operations.core.workspace import load_from_disk
        operation_dict = await load_from_disk(file_path=file_name, operation_group=None, with_instance=False)

        from research_analytics_suite.gui.modules.UpdatedOperationModule import UpdatedOperationModule
        preview_tile = UpdatedOperationModule(operation_dict=operation_dict, width=self.TILE_WIDTH,
                                              height=self.TILE_HEIGHT, parent=self._parent)
        await preview_tile.initialize_gui()
        preview_tile.draw()

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

        self._logger.debug(f"Loading operation from file: {_file_path}")
        await self.operation_preview_tile(_file_path)

        loaded_operations = {}
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

        # await self.refresh_display()
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

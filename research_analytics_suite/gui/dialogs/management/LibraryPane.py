"""
LibraryPane Module

The LibraryPane class module is used to display the operations of a category in the library pane.

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
from research_analytics_suite.operation_manager import BaseOperation


class LibraryPane(GUIBase):
    """A class to manage the dialog for displaying and controlling operations."""
    _lock = asyncio.Lock()

    SLEEP_DURATION = 0.05
    TILE_WIDTH = 300  # Fixed width for each preview tile
    TILE_HEIGHT = 40  # Fixed height for each preview tile

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        ...

    def __init__(self, width: int, height: int, parent):
        """
        Initializes the LibraryPane with the given operation control, logger, and container width.

        Args:
            width (int): Initial width of the container.
            height (int): Initial height of the container.
            parent: Parent container
        """
        super().__init__(width, height, parent)

        from research_analytics_suite.library_manifest import LibraryManifest
        self._library_manifest = LibraryManifest()

        from research_analytics_suite.utils import CustomLogger
        self._logger = CustomLogger()

        from research_analytics_suite.operation_manager.control.OperationControl import OperationControl
        self._operation_control = OperationControl()

        self._child_window_id = None
        self._category_id = None
        self._cell_ids = []

    async def initialize_gui(self) -> None:
        """Initializes the GUI elements for the operation library dialog."""
        self._logger.debug("Initializing the operation library dialog.")

        self._update_operation = await self._operation_control.operation_manager.add_operation_with_parameters(
            operation_type=BaseOperation, name="gui_LibraryUpdateTask", action=self._update_async,
            persistent=True, concurrent=True)
        self._update_operation.is_ready = True

        self._logger.debug("Operation library dialog initialized.")

    async def _update_async(self) -> None:
        """Asynchronously updates the cells within the child window."""
        while True:
            await asyncio.sleep(self.SLEEP_DURATION)

            async with self._lock:
                if self._library_manifest:
                    for _id, _category in self._library_manifest.get_categories():
                        # TODO: TOMORROW START HERE, DEBUG RIGHT HERE
                        if _category.operations is not []:
                            for operation in _category.operations:
                                if operation not in self._cell_ids:
                                    await self.operation_preview_tile(category=_category, operation_info=operation)
                                    self._cell_ids.append(operation)

    def draw(self) -> None:
        """Sets up the container for the operation manager dialog."""
        with dpg.child_window(label="Operation Library", width=self._width, height=self._height) as child_window:
            self._child_window_id = child_window

    async def operation_preview_tile(self, category, operation_info: dict) -> None:
        """
        Creates a preview tile for the operation.

        Args:
            category: The category of the operation.
            operation_info (dict): Information about the operation.
        """
        self._logger.debug(f"Creating operation preview tile for: {operation_info['name']}")

        from research_analytics_suite.gui.modules.OperationSlotPreview import OperationSlotPreview
        preview_tile = OperationSlotPreview(operation_dict=operation_info, width=self.TILE_WIDTH,
                                            height=self.TILE_HEIGHT, parent=self._child_window_id)
        await preview_tile.initialize_gui()
        preview_tile.draw()

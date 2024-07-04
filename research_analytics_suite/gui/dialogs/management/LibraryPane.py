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
    TILE_WIDTH = 250
    TILE_HEIGHT = 30

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        ...

    def __init__(self, width: int, height: int, parent):
        super().__init__(width, height, parent)

        from research_analytics_suite.library_manifest import LibraryManifest
        self._library_manifest = LibraryManifest()

        from research_analytics_suite.utils import CustomLogger
        self._logger = CustomLogger()

        from research_analytics_suite.operation_manager.control.OperationControl import OperationControl
        self._operation_control = OperationControl()

        self._child_window_id = None
        self._categories = {}
        self._cell_ids = set()

    async def initialize_gui(self) -> None:
        self._logger.debug("Initializing the operation library dialog.")
        self._update_operation = await self._operation_control.operation_manager.add_operation_with_parameters(
            operation_type=BaseOperation, name="gui_LibraryUpdateTask", action=self._update_async,
            is_loop=True, parallel=True)
        self._update_operation.is_ready = True
        self._logger.debug("Operation library dialog initialized.")

    async def _update_async(self) -> None:
        while True:
            await asyncio.sleep(self.SLEEP_DURATION)
            async with self._lock:
                if self._library_manifest:
                    for _id, _category in self._library_manifest.get_categories():
                        if _id not in self._categories:
                            self._categories[_id] = _category
                            await self._create_category_node(_category, self._child_window_id)

    async def _create_category_node(self, category, parent):
        """Recursively creates category tree nodes."""
        unique_tag = f"{category.name}_{category.category_id}"
        if unique_tag not in self._categories:
            self._categories[unique_tag] = category
            with dpg.tree_node(label=category.name, parent=parent, tag=unique_tag, default_open=False):
                for subcategory in category.subcategories.values():
                    await self._create_category_node(subcategory, unique_tag)
                for operation in category.operations:
                    await self._create_operation_tile(operation, unique_tag)
            if not category.subcategories:
                dpg.add_separator(parent=parent)

    def draw(self) -> None:
        with dpg.child_window(label="Operation Library",
                              width=self._width, height=self._height, border=False) as child_window:
            with dpg.child_window(parent=child_window, border=False, width=-1, height=30):
                with dpg.group(horizontal=True, horizontal_spacing=10):
                    dpg.add_button(label="New Category", callback=self._add_category, width=100)
                    dpg.add_button(label="New Operation", callback=self._new_operation, width=-1)

                from research_analytics_suite.gui import left_aligned_input_field
                left_aligned_input_field(label="Search", tag="operation_search", width=-1,
                                         callback=self._search_operations, parent=child_window, value="")
                dpg.add_spacer(width=5, parent=child_window)

            with dpg.child_window(parent=child_window, border=True, width=-1, height=-1, tag="library_view",
                                  horizontal_scrollbar=True):
                self._child_window_id = "library_view"

    async def _create_operation_tile(self, operation_info, parent):
        """Creates a preview tile for the operation."""
        u_id = None
        from research_analytics_suite.operation_manager.operations.core.memory.OperationAttributes import OperationAttributes
        if isinstance(operation_info, OperationAttributes):
            u_id = operation_info.unique_id
            operation_info = operation_info.export_attributes()
        elif isinstance(operation_info, dict):
            u_id = operation_info['unique_id']

        if u_id not in self._cell_ids:
            self._cell_ids.add(u_id)
            from research_analytics_suite.gui.modules.OperationSlotPreview import OperationSlotPreview
            preview_tile = OperationSlotPreview(operation_dict=operation_info, width=self.TILE_WIDTH,
                                                height=self.TILE_HEIGHT, parent=parent)
            await preview_tile.initialize_gui()
            preview_tile.draw()

    def _add_category(self) -> None:
        self._library_manifest.add_category(category_id=10, category_name="New Category")

    def _new_operation(self) -> None:
        from research_analytics_suite.operation_manager.operations.core.memory.OperationAttributes import OperationAttributes
        op_attributes = OperationAttributes()
        # self._library_manifest.add_operation_from_attributes(op_attributes)

    def _search_operations(self) -> None:
        pass

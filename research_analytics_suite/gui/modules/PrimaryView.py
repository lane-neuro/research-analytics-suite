"""
PrimaryView Module

This module defines the PrimaryView class, which is responsible for managing the main GUI window and its components.
"""
import asyncio
from typing import Optional, Any

import dearpygui.dearpygui as dpg
from research_analytics_suite.data_engine.memory.MemorySlotCollection import MemorySlotCollection
from research_analytics_suite.operation_manager import BaseOperation
from research_analytics_suite.utils import CustomLogger


class PrimaryView:
    """A class to manage the main GUI window and its components."""

    def __init__(self, parent=None):
        """Initializes the PrimaryView."""

        from research_analytics_suite.operation_manager import OperationControl
        self.operation_control = OperationControl()

        self._logger = CustomLogger()

        from research_analytics_suite.data_engine import MemoryManager
        self._memory_manager = MemoryManager()

        self.collections = []
        self.search_bar = None
        self.notification_area = None
        self.collection_summary = None
        self.advanced_slot_view = None
        self.update_operation = None
        self.parent = parent

    async def initialize_dialog(self) -> None:
        """Initializes the user interface."""
        with dpg.window(label="Primary Window", tag="primary_view", parent=self.parent, width=-1, height=-1):
            self.search_bar = dpg.add_input_text(label="Search", callback=self.search)
            self.notification_area = dpg.add_text("Notifications will appear here.")

            from research_analytics_suite.gui.modules.CollectionSummaryView import CollectionSummaryView
            self.collection_summary = CollectionSummaryView(parent="primary_view", collection_list=self.collections)
            self.collection_summary.draw()

            self.advanced_slot_view = None

        self.update_operation = await self.add_update_operation()

    async def add_update_operation(self) -> Optional[Any]:
        try:
            operation = await self.operation_control.operation_manager.add_operation_with_parameters(
                operation_type=BaseOperation, name="gui_DataCollectionUpdateTask",
                action=self.update_collections, persistent=True, concurrent=True)
            operation.is_ready = True
            return operation
        except Exception as e:
            self._logger.error(e, self)
        return None

    def search(self, sender, data):
        """Callback function for search bar."""
        search_query = dpg.get_value(self.search_bar)
        # Logic for searching collections and slots based on the query

    def add_collection(self, collection: MemorySlotCollection):
        """Adds a new collection to the primary view."""
        self.collections.append(collection)
        self.collection_summary.add_collection(collection)

    def remove_collection(self, collection_id: str):
        """Removes a collection from the primary view."""
        self.collections = [c for c in self.collections if c.collection_id != collection_id]
        self.collection_summary.remove_collection(collection_id)

    def show_advanced_slot_view(self, slot):
        """Displays the advanced slot view for a given slot."""
        if dpg.does_item_exist("advanced_slot_window"):
            dpg.delete_item("advanced_slot_window")
        with dpg.window(label="Advanced Slot View", tag="advanced_slot_window", width=500, height=500):
            from research_analytics_suite.gui import AdvancedSlotView
            self.advanced_slot_view = AdvancedSlotView(parent="advanced_slot_group", slot=slot)

    async def update_collections(self):
        """Updates the primary view with the given collections."""
        self.collections = await self._memory_manager.list_collections()
        self.collection_summary.update(self.collections)
        await asyncio.sleep(0.1)

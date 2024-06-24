"""
CollectionSummaryView Module

This module defines the CollectionSummaryView class, which is responsible for managing the GUI representation of collections and their slots.
"""
import dearpygui.dearpygui as dpg
from research_analytics_suite.data_engine.memory.MemorySlotCollection import MemorySlotCollection


class CollectionSummaryView:
    """A class to manage the GUI representation of collections and their slots."""

    def __init__(self, parent, collection_list: list[MemorySlotCollection]):
        """
        Initializes the CollectionSummaryView with the given collections.

        Args:
            parent (str): The parent GUI element ID.
            collection_list (list[MemorySlotCollection]): The list of memory slot collections to represent.
        """
        self.parent = parent
        self.collection_list = collection_list
        self.collection_groups = {}
        self.draw()

    def draw(self):
        """Draws the collection summary view elements."""
        for collection in self.collection_list:
            collection_tag = f"collection_group_{collection.collection_id}"
            self.collection_groups[collection.collection_id] = collection_tag

            with dpg.group(tag=collection_tag, parent=self.parent, horizontal=True):
                dpg.add_text(f"Collection: {collection.name}", parent=collection_tag)
                for slot in collection.slots:
                    from research_analytics_suite.gui import SlotPreview
                    slot_preview = SlotPreview(parent=collection_tag, slot=slot, width=200, height=100)
                    slot_preview.draw()

    def update(self, collections: list[MemorySlotCollection]):
        """Updates the collection summary view elements."""
        self.collection_list = collections
        for collection_tag in self.collection_groups.values():
            if dpg.does_item_exist(collection_tag):
                dpg.delete_item(collection_tag)
        self.draw()

    def add_collection(self, collection: MemorySlotCollection):
        """Adds a new collection to the view."""
        self.collection_list.append(collection)
        self.update(self.collection_list)

    def remove_collection(self, collection_id: str):
        """Removes a collection from the view."""
        self.collection_list = [c for c in self.collection_list if c.collection_id != collection_id]
        self.update(self.collection_list)

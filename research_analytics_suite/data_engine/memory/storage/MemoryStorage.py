"""
MemoryStorage Module

This module defines the in-memory storage backend for memory slot collections.

Author: Lane
"""
from typing import Tuple

from research_analytics_suite.data_engine.memory.storage.BaseStorage import BaseStorage
from research_analytics_suite.data_engine.memory.MemorySlotCollection import MemorySlotCollection


class MemoryStorage(BaseStorage):
    """
    In-memory storage implementation for memory slot collections.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collections = {}  # Store MemorySlotCollections
        self._logger.debug(f"[MemoryStorage] initialized. Backup path: {self.db_path}")

    async def setup(self):
        # No setup required for in-memory storage
        pass

    async def add_collection(self, collection: MemorySlotCollection):
        """
        Adds a new MemorySlotCollection to the in-memory storage.

        Args:
            collection (MemorySlotCollection): The collection to add.
        """
        self.collections[collection.collection_id] = collection
        self._logger.debug(f"[MemoryStorage] Added collection: {collection.display_name}")

    async def get_collection(self, collection_id: str) -> MemorySlotCollection:
        """
        Retrieves a MemorySlotCollection by its ID from the in-memory storage.

        Args:
            collection_id (str): The ID of the collection to retrieve.

        Returns:
            MemorySlotCollection: The retrieved collection.
        """
        return self.collections.get(collection_id)

    async def remove_collection(self, collection_id: str):
        """
        Removes a MemorySlotCollection by its ID from the in-memory storage.

        Args:
            collection_id (str): The ID of the collection to remove.
        """
        if collection_id in self.collections:
            del self.collections[collection_id]
            self._logger.debug(f"[MemoryStorage] Removed collection with ID: {collection_id}")

    async def list_collections(self) -> dict:
        """
        Lists all MemorySlotCollections from the in-memory storage.

        Returns:
            dict: A dictionary of MemorySlotCollections.
        """
        return {cid: col for cid, col in self.collections.items()}

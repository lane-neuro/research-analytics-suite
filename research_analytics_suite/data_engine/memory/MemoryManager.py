"""
MemoryManager Module

This module defines the MemoryManager class, which manages memory slot collections
using a specified storage backend.

Author: Lane
"""
import asyncio

from research_analytics_suite.data_engine.memory.MemorySlotCollection import MemorySlotCollection


class MemoryManager:
    """
    A class to manage memory slot collections within the workspace using a specified storage backend.
    """
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initializes the MemoryManager instance.
        """
        if not hasattr(self, "_initialized"):
            from research_analytics_suite.utils.CustomLogger import CustomLogger
            self._logger = CustomLogger()

            from research_analytics_suite.data_engine.memory import DataCache
            self._data_cache = DataCache()

            self.memory_slot_collections = {}  # Holds multiple MemorySlotCollections
            self.default_collection = None
            self._initialized = False

    async def initialize(self):
        """
        Initializes the MemoryManager.
        """
        if not self._initialized:
            async with MemoryManager._lock:
                if not self._initialized:
                    await self._data_cache.initialize()
                    self.memory_slot_collections = {}
                    await self.initialize_default_collection()
                    self._logger.info("MemoryManager initialized.")
                    self._initialized = True

    async def initialize_default_collection(self):
        if not self.memory_slot_collections:
            if not self.default_collection:
                self.default_collection = MemorySlotCollection("Primary")
            else:
                self.add_collection(self.default_collection)
        else:
            self.default_collection = next(iter(self.memory_slot_collections.values()))

    async def get_default_collection_id(self) -> str:
        return self.default_collection.collection_id

    def add_collection(self, collection: MemorySlotCollection):
        """
        Adds a new MemorySlotCollection.

        Args:
            collection (MemorySlotCollection): The collection to add.
        """
        if collection.name == "Primary":
            if self.default_collection:
                self.default_collection.add_slots(collection.slots)
                self._logger.info(f"Merged new collection with default collection: {collection.display_name}")
                return
            else:
                self.default_collection = collection
                self.memory_slot_collections[collection.collection_id] = collection
                self._logger.info(f"Set new collection as default collection: {collection.display_name}")
        else:
            if collection.collection_id not in self.memory_slot_collections:
                self.memory_slot_collections[collection.collection_id] = collection
                self._logger.info(f"Added MemorySlotCollection: {collection.display_name}")
            else:
                self._logger.info(f"Collection with ID {collection.collection_id} already exists, "
                                  f"importing existing memory slots as new slots.")
                self.memory_slot_collections[collection.collection_id].add_slots(collection.slots)

    async def get_collection(self, collection_id: str) -> MemorySlotCollection:
        """
        Retrieves a MemorySlotCollection by its ID.

        Args:
            collection_id (str): The ID of the collection to retrieve.

        Returns:
            MemorySlotCollection: The retrieved collection.
        """
        cached_collection = self._data_cache.get(collection_id)
        if cached_collection:
            self._logger.info(f"Cache hit for collection ID: {collection_id}")
            self._data_cache.set(collection_id, cached_collection)  # Update cache to keep it fresh
            return cached_collection

        self._logger.info(f"Cache miss for collection ID: {collection_id}")
        collection = self.memory_slot_collections.get(collection_id)
        if collection:
            self._data_cache.set(collection_id, collection)
        return collection

    def get_collection_by_display_name(self, collection_name: str) -> MemorySlotCollection:
        """
        Retrieves a MemorySlotCollection by its display name.

        Args:
            collection_name (str): The display name of the collection to retrieve.

        Returns:
            MemorySlotCollection: The retrieved collection.
        """
        for collection in self.memory_slot_collections.values():
            if collection.display_name == collection_name:
                self._logger.info(f"Cache hit for collection display name: {collection_name}")
                self._data_cache.set(collection.collection_id, collection)  # Update cache to keep it fresh
                return collection
        self._logger.info(f"Cache miss for collection display name: {collection_name}")

    async def remove_collection(self, collection_id: str):
        """
        Removes a MemorySlotCollection by its ID.

        Args:
            collection_id (str): The ID of the collection to remove.
        """
        if collection_id == self.default_collection.collection_id:
            self.default_collection = None
            self._logger.info(f"Removed default collection with ID: {collection_id}")
            await self.initialize_default_collection()
        elif collection_id in self.memory_slot_collections:
            del self.memory_slot_collections[collection_id]
            self._data_cache.set(collection_id, None)  # Remove from cache
            self._logger.info(f"Removed MemorySlotCollection with ID: {collection_id}")
        else:
            self._logger.info(f"No collection found with ID: {collection_id}")

    async def list_collections(self) -> dict:
        """
        Lists all MemorySlotCollections.

        Returns:
            dict: A dictionary of MemorySlotCollections.
        """
        return {cid: col for cid, col in self.memory_slot_collections.items()}

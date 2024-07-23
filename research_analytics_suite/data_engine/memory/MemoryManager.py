"""
MemoryManager Module

This module defines the MemoryManager class, which manages memory slot collections
using a specified storage backend.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from __future__ import annotations
import asyncio
from research_analytics_suite.data_engine.memory.MemorySlot import MemorySlot
from research_analytics_suite.data_engine.memory.SQLiteStorage import SQLiteStorage
from research_analytics_suite.data_engine.memory.DataCache import DataCache


class MemoryManager:
    """
    A class to manage memory slot collections within the workspace using a specified storage backend.

    Attributes:
        _instance (MemoryManager): Singleton instance of MemoryManager.
        _lock (asyncio.Lock): Lock to ensure thread-safe operations.
        _logger (CustomLogger): Logger instance for logging events.
        _data_cache (DataCache): Instance of DataCache for managing cached data.
        _sqlite_storage (SQLiteStorage): Instance of SQLiteStorage for managing persistent data.
        _initialized (bool): Flag indicating whether the manager has been initialized.
    """
    _instance: MemoryManager = None
    _lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        """
        Singleton implementation for MemoryManager.

        Returns:
            MemoryManager: The MemoryManager instance.
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_path: str = "memory_manager.db"):
        """
        Initializes the MemoryManager instance.

        Args:
            db_path (str): The path to the SQLite database file.
        """
        if not hasattr(self, "_initialized"):
            from research_analytics_suite.utils.CustomLogger import CustomLogger
            self._logger = CustomLogger()

            self._data_cache = DataCache()
            self._sqlite_storage = SQLiteStorage(db_path=db_path)

            self._initialized = False

    async def initialize(self):
        """
        Initializes the MemoryManager.
        """
        if not self._initialized:
            async with MemoryManager._lock:
                if not self._initialized:
                    await self._data_cache.initialize()
                    await self._sqlite_storage.setup()
                    self._logger.debug("MemoryManager initialized.")
                    self._initialized = True

    async def create_memory_slot(self, memory_id: str, name: str, data: any, file_path: str = None):
        """
        Creates a new memory slot and stores it in both cache and SQLite storage.

        Args:
            memory_id (str): The unique identifier for the memory slot.
            name (str): The name of the memory slot.
            data (any): The data to store in the memory slot.
            file_path (str): The file path for memory-mapped storage.

        Returns:
            MemorySlot: The created memory slot.
        """
        memory_slot = MemorySlot(memory_id, name, data, file_path)
        await self._sqlite_storage.add_variable(memory_id, memory_slot)
        self._data_cache.set(memory_id, memory_slot)
        return memory_slot

    async def get_memory_slot(self, memory_id: str) -> MemorySlot or None:
        """
        Retrieves a memory slot from the cache or SQLite storage.

        Args:
            memory_id (str): The unique identifier for the memory slot.

        Returns:
            MemorySlot or None: The retrieved memory slot or None if not found.
        """
        memory_slot = self._data_cache.get(memory_id)
        if memory_slot:
            return memory_slot

        data = await self._sqlite_storage.get_variable(memory_id)
        if data:
            memory_slot = MemorySlot(**data)
            self._data_cache.set(memory_id, memory_slot)
        return memory_slot

    async def update_memory_slot(self, memory_id: str, data: any):
        """
        Updates the data in an existing memory slot.

        Args:
            memory_id (str): The unique identifier for the memory slot.
            data (any): The new data to store in the memory slot.

        Returns:
            MemorySlot: The updated memory slot.
        """
        memory_slot = await self.get_memory_slot(memory_id)
        if memory_slot:
            memory_slot.set_data(data)
            await self._sqlite_storage.update_variable(memory_id, memory_slot)
            self._data_cache.set(memory_id, memory_slot)
        return memory_slot

    async def delete_memory_slot(self, memory_id: str):
        """
        Deletes a memory slot from both cache and SQLite storage.

        Args:
            memory_id (str): The unique identifier for the memory slot.
        """
        await self._sqlite_storage.delete_variable(memory_id)
        self._data_cache._cache.pop(memory_id, None)

    async def list_memory_slots(self) -> dict:
        """
        Lists all memory slots stored in the SQLite storage.

        Returns:
            dict: A dictionary of memory slots.
        """
        return await self._sqlite_storage.list_variables()

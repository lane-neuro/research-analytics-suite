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
import os
import uuid
from research_analytics_suite.data_engine.memory.MemorySlot import MemorySlot
from research_analytics_suite.data_engine.memory.DataCache import DataCache
from research_analytics_suite.utils import CustomLogger
from research_analytics_suite.utils import Config


class MemoryManager:
    """
    A class to manage memory slot collections within the workspace using a specified storage backend.

    Attributes:
        _instance (MemoryManager): Singleton instance of MemoryManager.
        _lock (asyncio.Lock): Lock to ensure thread-safe operations.
        _logger (CustomLogger): Logger instance for logging events.
        _data_cache (DataCache): Instance of DataCache for managing cached data.
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

    def __init__(self, db_path: str = "memory_manager.db", cache_backend: str = 'cachetools',
                 cache_directory: str = 'cache_directory'):
        """
        Initializes the MemoryManager instance.

        Args:
            db_path (str): The path to the SQLite database file.
            cache_backend (str): The caching backend to use ('cachetools' or 'diskcache').
            cache_directory (str): The directory to store diskcache files.
        """
        if not hasattr(self, "_initialized"):
            self._logger = None
            self._config = None

            self._db_path = db_path
            self._cache_backend = cache_backend
            self._cache_directory = cache_directory

            self._data_cache = None

            self._initialized = False

    async def initialize(self):
        """
        Initializes the MemoryManager.
        """
        if self._initialized:
            return

        async with MemoryManager._lock:
            if self._initialized:
                return
            self._logger = CustomLogger()
            self._config = Config()

            try:
                self._db_path = os.path.normpath(self._db_path)
            except Exception as e:
                self._db_path = os.path.normpath(os.path.join(
                    self._config.BASE_DIR, self._config.WORKSPACE_NAME,
                    self._config.DATA_DIR, "memory_manager.db"))

            try:
                self._cache_directory = os.path.normpath(self._cache_directory)
            except Exception as e:
                self._cache_directory = os.path.normpath(
                    os.path.join(self._config.BASE_DIR, self._config.WORKSPACE_NAME,
                                 self._config.DATA_DIR, self._config.CACHE_DIR))

            self._data_cache = DataCache(backend=self._cache_backend, directory=self._cache_directory)
            await self._data_cache.initialize()
            self._logger.debug("MemoryManager initialized.")
            self._initialized = True

    async def create_slot(self, name: str, data: any, db_path: str = None, file_path: str = None) -> str:
        """
        Creates a new memory slot and stores it in both cache and SQLite storage.

        Args:
            name (str): The name of the memory slot.
            data (any): The data to store in the memory slot.
            db_path (str): The path to the SQLite database file.
            file_path (str): The file path for memory-mapped storage.

        Returns:
            str: The unique identifier for the created memory slot.
        """
        if file_path:
            try:
                file_path = os.path.normpath(file_path)
            except Exception as e:
                self._logger.warning(f"Invalid file path: {e} \nMemory slot will not be memory-mapped.")
                file_path = None

        _id = uuid.uuid4().hex[:8]
        memory_slot = MemorySlot(memory_id=_id, name=name, data=data, db_path=db_path, file_path=file_path)
        await memory_slot.setup()
        self._data_cache.set(key=memory_slot._memory_id, data=memory_slot)
        return memory_slot._memory_id

    async def update_slot(self, memory_id: str, data: any) -> str:
        """
        Updates the data in an existing memory slot.

        Args:
            memory_id (str): The unique identifier for the memory slot.
            data (any): The new data to store in the memory slot.

        Returns:
            str: The memory slot identifier.
        """
        memory_slot = self._data_cache.get_key(key=memory_id)
        if memory_slot:
            await memory_slot.set_data(data)
        else:
            memory_slot = MemorySlot(memory_id=memory_id, name="", data=data, db_path=self._db_path)
            await memory_slot.setup()
            await memory_slot.set_data(data)
            self._data_cache.set(key=memory_id, data=memory_slot)
        return memory_id

    async def delete_slot(self, memory_id: str) -> None:
        """
        Deletes a memory slot from both cache and SQLite storage.

        Args:
            memory_id (str): The unique identifier for the memory slot.
        """
        memory_slot = self._data_cache.get_key(key=memory_id)
        if memory_slot:
            memory_slot.close()
            os.remove(memory_slot._file_path)  # Remove memory-mapped file if it exists
        self._data_cache.delete(key=memory_id)

    async def list_slots(self) -> dict:
        """
        Lists all memory slots stored in the SQLite storage.

        Returns:
            dict: A dictionary of memory slots.
        """
        return await self._data_cache.list_keys()

    async def slot_data(self, memory_id: str) -> any:
        """
        Retrieves the data stored in a memory slot.

        Args:
            memory_id (str): The unique identifier for the memory slot.

        Returns:
            any: The data stored in the memory slot.
        """
        memory_slot = self._data_cache.get_key(key=memory_id)
        if memory_slot is not None:
            return await memory_slot.data

        memory_slot = MemorySlot(memory_id=memory_id, name="", data=None, db_path=self._db_path)
        await memory_slot.setup()
        data = await memory_slot.data
        if data:
            self._data_cache.set(key=memory_id, data=memory_slot)
        return data

    async def slot_name(self, memory_id: str) -> str:
        """
        Retrieves the name of a memory slot.

        Args:
            memory_id (str): The unique identifier for the memory slot.

        Returns:
            str: The name of the memory slot.
        """
        memory_slot = self._data_cache.get_key(key=memory_id)
        if memory_slot:
            return memory_slot.name

        memory_slot = MemorySlot(memory_id=memory_id, name="", data=None, db_path=self._db_path)
        await memory_slot.setup()
        name = memory_slot.name
        if name:
            self._data_cache.set(key=memory_id, data=memory_slot)
        return name

    async def validate_slots(self, memory_ids: list, require_values: bool = True) -> (list, list):
        """
        Validates a list of memory slot identifiers and returns the valid and invalid slots.

        Args:
            memory_ids (list): A list of memory slot identifiers.
            require_values (bool): Flag indicating whether to require values in the slots. Defaults to True.

        Returns:
            tuple: A tuple containing the valid and invalid memory slot identifiers.
        """
        valid_slots = []
        for memory_id in memory_ids:
            data = await self.slot_data(memory_id=memory_id)
            if data:
                if require_values and not data:
                    continue
                valid_slots.append(memory_id)
        return valid_slots, list(set(memory_ids) - set(valid_slots))

    async def cleanup(self):
        """
        Cleans up resources used by MemoryManager.
        """
        if self._data_cache:
            await self._data_cache.close()

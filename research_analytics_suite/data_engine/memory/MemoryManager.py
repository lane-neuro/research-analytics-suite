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
from typing import Type

from research_analytics_suite.commands import link_class_commands, command
from research_analytics_suite.data_engine.memory.MemorySlot import MemorySlot
from research_analytics_suite.data_engine.memory.DataCache import DataCache
from research_analytics_suite.utils import CustomLogger
from research_analytics_suite.utils import Config


@link_class_commands
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
            self._slot_collection = {}

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

            # await self._initialize_data_cache()

            self._logger.debug("MemoryManager initialized.")
            self._initialized = True

    async def _initialize_data_cache(self):
        """
        Initializes the data cache for the MemoryManager.
        """
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

    @command
    async def create_slot(self, name: str, d_type: type = any, data: any = None, db_path: str = None, file_path: str = None) \
            -> [str, str, any]:
        """
        Creates a new memory slot and stores it in both cache and SQLite storage.

        Args:
            name (str): The name of the memory slot.
            d_type (Type): The data type of the memory slot.
            data (any): The data to store in the memory slot.
            db_path (str): The path to the SQLite database file.
            file_path (str): The file path for memory-mapped storage.

        Returns:
            str: The unique identifier for the created memory slot.
            str: The name of the memory slot.
            any: The data stored in the memory slot.
        """
        if file_path:
            try:
                file_path = os.path.normpath(file_path)
            except Exception as e:
                self._logger.warning(f"Invalid file path: {e} \nMemory slot will not be memory-mapped.")
                file_path = None

        _id = uuid.uuid4().hex[:8]
        memory_slot = MemorySlot(
            memory_id=_id, name=name, d_type=d_type, data=data, db_path=db_path, file_path=file_path)
        self._slot_collection[memory_slot.memory_id] = memory_slot
        await memory_slot.setup()

        return memory_slot.memory_id, memory_slot.name, memory_slot.data

    @command
    async def update_slot(self, memory_id: str, data: any) -> [str, any]:
        """
        Updates the data in an existing memory slot.

        Args:
            memory_id (str): The unique identifier for the memory slot.
            data (any): The new data to store in the memory slot.

        Returns:
            str: The memory slot identifier.
            any: The updated data.
        """
        memory_slot = self._slot_collection.get(memory_id)
        if memory_slot:
            await memory_slot.set_data(data)
        else:
            d_type = type(data)
            memory_slot = MemorySlot(memory_id=memory_id, name="", d_type=d_type, data=data, db_path=self._db_path)
            await memory_slot.setup()
            await memory_slot.set_data(data)
        return memory_id, memory_slot.data

    @command
    async def delete_slot(self, memory_id: str) -> None:
        """
        Deletes a memory slot from both SQLite storage.

        Args:
            memory_id (str): The unique identifier for the memory slot.
        """
        try:
            memory_slot = self._slot_collection.pop(memory_id)
            if memory_slot:
                memory_slot.close()
                if memory_slot.file_path is not None:
                    os.remove(memory_slot.file_path)  # Remove memory-mapped file if it exists
        except KeyError or FileNotFoundError:
            self._logger.warning(f"Memory slot with ID: {memory_id} does not exist.")

    @command
    def list_slots(self) -> list:
        """
        Lists all memory slots stored in the SQLite storage.

        Returns:
            list: A dictionary of memory slots.
        """
        _slots = []
        for memory_id in self._slot_collection:
            _slots.append(self._slot_collection[memory_id])
        return _slots

    @command
    def slot_data(self, memory_id: str) -> any:
        """
        Retrieves the data stored in a memory slot.

        Args:
            memory_id (str): The unique identifier for the memory slot.

        Returns:
            any: The data stored in the memory slot.
        """
        return self._slot_collection[memory_id].data

    @command
    def slot_name(self, memory_id: str) -> str:
        """
        Retrieves the name of a memory slot.

        Args:
            memory_id (str): The unique identifier for the memory slot.

        Returns:
            str: The name of the memory slot.
        """
        return self._slot_collection[memory_id].name

    @command
    def slot_type(self, memory_id: str) -> Type:
        """
        Retrieves the data type of a memory slot.

        Args:
            memory_id (str): The unique identifier for the memory slot.

        Returns:
            Type: The data type of the memory slot.
        """
        return self._slot_collection[memory_id].data_type

    @command
    def get_slot(self, memory_id: str) -> MemorySlot:
        """
        Retrieves a MemorySlot instance from the cache.

        Args:
            memory_id (str): The unique identifier for the memory slot.

        Returns:
            MemorySlot: The MemorySlot instance.
        """
        return self._slot_collection[memory_id]

    @command
    def get_slot_subset(self, memory_ids: list) -> list:
        """
        Retrieves a list of MemorySlot instances from the cache.

        Args:
            memory_ids (list): A list of memory slot identifiers.

        Returns:
            list: A list of MemorySlot instances.
        """
        return [self.get_slot(memory_id) for memory_id in memory_ids]

    @command
    def get_all_slots(self) -> dict:
        """
        Retrieves all MemorySlot instances from the cache.

        Returns:
            list: A list of MemorySlot instances.
        """
        temp_output = {}
        for memory_id, slot in self._slot_collection.items():
            temp_output[memory_id] = slot
        return temp_output

    def validate_slots(self, memory_ids: list, require_values: bool = True) -> (list, list):
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
            data = self.slot_data(memory_id=memory_id)
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

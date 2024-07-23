"""
DataCache Module

This module defines the DataCache class for caching data to optimize access to datasets.

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
import sys
from cachetools import LRUCache
from research_analytics_suite.utils import CustomLogger


class DataCache:
    """
    A class to manage caching of data for optimizing access to datasets.

    Attributes:
        _logger (CustomLogger): Logger instance for logging events.
        _instance (DataCache): Singleton instance of DataCache.
        _lock (asyncio.Lock): Lock to ensure thread-safe operations.
        _size (int): The size of the cache in bytes.
        _workspace (Workspace): Workspace instance for managing the workspace.
        _cache (LRUCache): An instance of LRUCache to store cached data.
        _initialized (bool): Flag indicating whether the cache has been initialized.
    """
    _logger: CustomLogger = None
    _instance: DataCache = None
    _lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        """
        Singleton implementation for DataCache.

        Returns:
            DataCache: The DataCache instance.
        """
        if not cls._instance:
            cls._instance = super(DataCache, cls).__new__(cls)
        return cls._instance

    def __init__(self, size=2e9):
        """
        Initializes the DataCache instance.

        Args:
            size (int): The size of the cache in bytes. Default is 2GB.
        """
        if not hasattr(self, '_initialized'):
            self._size = size
            self._workspace = None
            self._cache = None
            self._initialized = False

    async def initialize(self):
        """
        Initializes the DataCache instance.
        """
        if not self._initialized:
            async with DataCache._lock:
                if not self._initialized:
                    self._logger = CustomLogger()
                    from research_analytics_suite.data_engine import Workspace
                    self._workspace = Workspace()
                    self._cache = LRUCache(maxsize=int(self._size))
                    self._initialized = True

    def get(self, key):
        """
        Retrieves data from the cache.

        Args:
            key (str): The key for the cached data.

        Returns:
            The cached data or None if the key is not found.
        """
        return self._cache.get(key)

    def set(self, key, data):
        """
        Stores data in the cache.

        Args:
            key (str): The key for the data.
            data: The data to cache.
        """
        cost = sys.getsizeof(data)
        self._cache[key] = data

    def clear(self):
        """
        Clears all data from the cache.
        """
        self._cache.clear()

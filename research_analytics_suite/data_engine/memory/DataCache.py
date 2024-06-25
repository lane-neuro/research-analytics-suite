"""
DataCache Module

Defines the DataCache class for caching data to optimize access to datasets.

Author: Lane
"""
import asyncio
import sys

from cachey import Cache


class DataCache:
    """
    A class to manage caching of data for optimizing access to datasets.

    Attributes:
        _cache (Cache): An instance of Cachey to store cached data.
    """
    _logger = None
    _instance = None
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

            self._logger = None
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

                    from research_analytics_suite.utils import CustomLogger
                    self._logger = CustomLogger()

                    from research_analytics_suite.data_engine import Workspace
                    self._workspace = Workspace()

                    self._cache = Cache(self._size)

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
        self._cache.put(key=key, value=data, cost=cost)

    def clear(self):
        """
        Clears all data from the cache.
        """
        self._cache.clear()

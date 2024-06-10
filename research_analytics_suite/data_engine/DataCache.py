"""
DataCache Module

Defines the DataCache class for caching data to optimize access to datasets.

Author: Lane
"""

from dask.cache import Cache


class DataCache(Cache):
    """
    A class to manage caching of data for optimizing access to datasets.

    Attributes:
        cache (dict): A dictionary to store cached data.
    """

    def __init__(self, size=2e9):
        """
        Initializes the DataCache instance.

        Args:
            size (int): The size of the cache. Default is 2GB.
        """
        super().__init__(size)
        self.cache = {}

    def get(self, key):
        """
        Retrieves data from the cache.

        Args:
            key (str): The key for the cached data.

        Returns:
            The cached data or None if the key is not found.
        """
        return self.cache.get(key)

    def set(self, key, data):
        """
        Stores data in the cache.

        Args:
            key (str): The key for the data.
            data: The data to cache.
        """
        self.cache[key] = data

    def remove(self, key):
        """
        Removes data from the cache.

        Args:
            key (str): The key for the data to remove.
        """
        if key in self.cache:
            del self.cache[key]

    def clear(self):
        """
        Clears all data from the cache.
        """
        self.cache.clear()

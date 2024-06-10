"""
DataEngineOptimized Module

This module defines the DataEngineOptimized class, which extends the UnifiedDataEngine to include optimizations for
performance and scalability. It handles larger datasets efficiently using distributed computing and includes advanced
caching mechanisms and memory management techniques.

Author: Lane
"""
import psutil

from research_analytics_suite.data_engine.Config import Config
from research_analytics_suite.data_engine.DataCache import DataCache
from research_analytics_suite.data_engine.UnifiedDataEngine import UnifiedDataEngine
from research_analytics_suite.utils.CustomLogger import CustomLogger


class DataEngineOptimized(UnifiedDataEngine):
    """
    A class to handle larger datasets efficiently using distributed computing and advanced caching mechanisms.

    Attributes:
        cache (DataCache): Data cache for storing intermediate results.
        memory_limit (float): Memory limit for caching, in bytes.
        workspace (Workspace): Workspace instance for managing saving and loading workspaces.
    """
    def __init__(self, workspace, data=None):
        """
        Initializes the DataEngineOptimized instance.

        Args:
            data: The initial data for the data engine.
            workspace (Workspace): Workspace instance for managing saving and loading workspaces.
        """
        super().__init__(data=data)
        self._logger = CustomLogger()
        self._config = Config()

        self.cache = DataCache(self._config.CACHE_SIZE)
        self.cache.register()
        self.memory_limit = self._config.MEMORY_LIMIT
        self.workspace = workspace

    def perform_operation(self, operation_name):
        """
        Performs the specified operation on the data and caches the result.

        Args:
            operation_name (str): The name of the operation to perform.
        """
        self._logger.info(f"Performing operation: {operation_name}")
        result = self.data.map_partitions(self._apply_operation, operation_name)
        self.cache.set(operation_name, result)
        self._logger.info("Operation performed and result cached")
        return result

    def _apply_operation(self, df, operation_name):
        """
        Applies the specified operation to a partition of the data.

        Args:
            df: A partition of the data.
            operation_name (str): The name of the operation to perform.

        Returns:
            The result of the operation.
        """
        # Placeholder for actual operation logic
        if operation_name == "double":
            return df * 2
        return df

    def update_live_data(self, new_data):
        """
        Updates the data engine with new live data and caches the updated data.

        Args:
            new_data: The new live data.
        """
        self._logger.info("Updating live data")
        self.data = self.data.append(new_data)
        self.cache.set('live_data', self.data)
        self._logger.info("Live data updated and cached")

    def monitor_memory_usage(self):
        """
        Monitors the memory usage and clears the cache if the memory limit is exceeded.
        """
        memory_used = psutil.virtual_memory().used
        if memory_used > self.memory_limit:
            self._logger.warning("Memory limit exceeded, clearing cache")
            self.cache.clear()
            self._logger.info("Cache cleared to free up memory")

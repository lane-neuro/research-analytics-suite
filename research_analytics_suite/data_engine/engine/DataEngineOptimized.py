"""
DataEngineOptimized Module

This module defines the DataEngineOptimized class, which extends the UnifiedDataEngine to include optimizations for
performance and scalability. It handles larger datasets efficiently using distributed computing and includes advanced
caching mechanisms and memory management techniques.

Author: Lane
"""
import psutil

from research_analytics_suite.commands import register_commands, command
from research_analytics_suite.utils.Config import Config
from research_analytics_suite.data_engine.memory.DataCache import DataCache
from research_analytics_suite.data_engine.engine.UnifiedDataEngine import UnifiedDataEngine
from research_analytics_suite.data_engine.data_streams.LiveDataHandler import LiveDataHandler
from research_analytics_suite.utils.CustomLogger import CustomLogger


@register_commands
class DataEngineOptimized(UnifiedDataEngine):
    """
    A class to handle larger datasets efficiently using distributed computing and advanced caching mechanisms.
    """
    def __init__(self, data=None):
        """
        Initializes the DataEngineOptimized instance.

        Args:
            data: The initial data for the data engine.
        """
        super().__init__(data=data)
        self._logger = CustomLogger()

        from research_analytics_suite.data_engine.Workspace import Workspace
        self._workspace = Workspace()

        self._config = Config()

        self._cache = DataCache()
        self._memory_limit = self._config.MEMORY_LIMIT

        self.live_data_handler = LiveDataHandler(data_engine=self)

    @command
    def perform_operation(self, operation_name):
        """
        Performs the specified operation on the data and caches the result.

        Args:
            operation_name (str): The name of the operation to perform.
        """
        self._logger.debug(f"Performing operation: {operation_name}")
        result = self.data.map_partitions(self._apply_operation, operation_name)
        self._cache.set(operation_name, result)
        self._logger.debug("Operation performed and result cached")
        return result

    @command
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
        self._logger.debug("Updating live data")
        self.data = self.data.append(new_data)
        self._cache.set('live_data', self.data)
        self._logger.debug("Live data updated and cached")

    def monitor_memory_usage(self):
        """
        Monitors the memory usage and clears the cache if the memory limit is exceeded.
        """
        memory_used = psutil.virtual_memory().used
        if memory_used > self._memory_limit:
            self._logger.warning("Memory limit exceeded, clearing cache")
            self._cache.clear()
            self._logger.debug("Cache cleared to free up memory")

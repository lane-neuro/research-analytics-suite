"""
Base Storage Module

This module defines the abstract base class for storage backends for user variables.

Author: Lane
"""

from abc import ABC, abstractmethod

from research_analytics_suite.data_engine.Config import Config
from research_analytics_suite.utils.CustomLogger import CustomLogger


class BaseStorage(ABC):
    """
    Abstract base class for storage backends.
    """

    def __init__(self, *args, **kwargs):
        self._logger = CustomLogger()
        self._config = Config()

        self.db_path = kwargs.get('db_path', None)

    @abstractmethod
    async def setup(self):
        """
        Sets up the storage backend.
        """
        pass

    @abstractmethod
    async def add_variable(self, name, value):
        """
        Adds a new variable to the storage.

        Args:
            name (str): The name of the variable.
            value: The value of the variable.
        """
        pass

    @abstractmethod
    async def get_variable_value(self, name):
        """
        Retrieves the value of a variable by name from the storage.

        Args:
            name (str): The name of the variable.

        Returns:
            The value of the variable.
        """
        pass

    @abstractmethod
    async def remove_variable(self, name):
        """
        Removes a variable by name from the storage.

        Args:
            name (str): The name of the variable to remove.
        """
        pass

    @abstractmethod
    async def list_variables(self):
        """
        Lists all variables from the storage.

        Returns:
            dict: A dictionary of all variables.
        """
        pass

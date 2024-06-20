"""
Base Storage Module

This module defines the abstract base class for storage backends for user variables.

Author: Lane
"""
import uuid
from abc import ABC, abstractmethod
from typing import Tuple

from research_analytics_suite.data_engine.utils.Config import Config
from research_analytics_suite.utils.CustomLogger import CustomLogger


class BaseStorage(ABC):
    """
    Abstract base class for storage backends.
    """
    _GENERAL_MEMORY_ID = None

    def __init__(self, *args, **kwargs):
        self._GENERAL_MEMORY_ID = f"{uuid.uuid4()}"
        self._logger = CustomLogger()
        self._config = Config()

        from research_analytics_suite.data_engine.Workspace import Workspace
        self._workspace = Workspace()

        self.db_path = kwargs.get('db_path', None)

    @abstractmethod
    async def setup(self):
        """
        Sets up the storage backend.
        """
        pass

    @abstractmethod
    async def add_variable(self, name, value, memory_id=None) -> Tuple[str, dict]:
        """
        Adds a new variable to the storage, optionally filtered by memory ID.

        Args:
            name (str): The name of the variable.
            value: The value of the variable.
            memory_id (str, optional): The ID of the memory to which the variable belongs.

        Returns:
            str: The memory_id location of the stored variable.
            dict[name, value]:
                name (str): The name of the variable. (aka: the key)
                value: The value of the stored variable in the associated memory_id location.
        """
        pass

    @abstractmethod
    async def get_variable_value(self, name, memory_id=None) -> Tuple[str, dict]:
        """
        Retrieves the value of a variable by name from storage.

        Args:
            name (str): The name of the variable.
            memory_id (str, optional): The ID of the memory to which the variable belongs.

        Returns:
            str: The memory_id location of the stored variable.
            dict[name, value]:
                name (str): The name of the variable. (aka: the key)
                value: The value of the stored variable in the associated memory_id location.
        """
        pass

    @abstractmethod
    async def remove_variable(self, name, memory_id=None):
        """
        Removes a variable by name from the storage, optionally filtered by memory ID.

        Args:
            name (str): The name of the variable to remove.
            memory_id (str, optional): The ID of the memory to which the variable belongs.
        """
        pass

    @abstractmethod
    async def list_variables(self, memory_id=None) -> dict:
        """
        Lists all variables from the storage, optionally filtered by memory ID.

        Args:
            memory_id (str, optional): The ID of the memory to which the variables

        Returns:
            dict: A dictionary of variables.
        """
        pass

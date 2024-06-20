"""
UserVariablesManager Module

This module defines the UserVariablesManager class, which manages user-defined variables
using a specified storage backend.

Author: Lane
"""

import asyncio
from typing import Mapping, Any, Tuple

from research_analytics_suite.data_engine.variable_storage.storage.BaseStorage import BaseStorage
from research_analytics_suite.utils.CustomLogger import CustomLogger


class UserVariablesManager:
    """
    A class to manage user-defined variables within the workspace using a specified storage backend.
    """

    def __init__(self, storage: BaseStorage):
        """
        Initializes the UserVariablesManager instance.

        Args:
            storage (BaseStorage): The storage backend to use.
        """
        self.storage = storage
        self._logger = CustomLogger()
        asyncio.run(self.storage.setup())

    async def add_variable_to_manager(self, name, value, memory_id=None) -> Tuple[str, dict]:
        """
        Adds a new variable to the storage.

        Args:
            name (str): The name of the variable.
            value: The value of the variable.
            memory_id (str, optional): The ID of the memory to which the variable belongs.

        Returns:
            str: The memory_id location of the stored variable in the user_variables database.
            dict[name, value]:
                name (str): The name of the variable. (aka: the key)
                value: The value of the stored variable in the associated memory_id location.
        """
        try:
            return await self.storage.add_variable(name=name, value=value, memory_id=memory_id)
        except Exception as e:
            self._logger.error(Exception(f"Error adding variable '{name}': {e}"), self)

    async def get_variable(self, name, memory_id=None) -> Tuple[str, dict]:
        """
        Retrieves the value of a variable by name from the storage.

        Args:
            name (str): The name of the variable.
            memory_id (str, optional): The ID of the memory to which the variable belongs.

        Returns:
            str: The memory_id location of the stored variable in the user_variables database.
            dict[name, value]:
                name (str): The name of the variable. (aka: the key)
                value: The value of the stored variable in the associated memory_id location.
        """
        try:
            return await self.storage.get_variable_value(name=name, memory_id=memory_id)
        except Exception as e:
            self._logger.error(Exception(f"Error retrieving variable '{name}': {e}"), self)

    async def remove_variable(self, name, memory_id=None):
        """
        Removes a variable by name from the storage.

        Args:
            name (str): The name of the variable to remove.
            memory_id (str, optional): The ID of the memory to which the variable belongs.
        """
        try:
            await self.storage.remove_variable(name=name, memory_id=memory_id)
        except Exception as e:
            self._logger.error(Exception(f"Error removing variable '{name}': {e}"), self)

    async def list_variables(self, memory_id=None) -> dict:
        """
        Lists all variables in the storage, optionally filtered by memory ID.

        Args:
            memory_id (str, optional): The ID of the memory to which the variables belong.

        Returns:
            dict: A dictionary of variables.
        """
        try:
            return await self.storage.list_variables(memory_id=memory_id)
        except Exception as e:
            self._logger.error(Exception(f"Error listing variables: {e}"), self)

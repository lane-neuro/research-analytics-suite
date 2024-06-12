"""
UserVariablesManager Module

This module defines the UserVariablesManager class, which manages user-defined variables
using a specified storage backend.

Author: Lane
"""

import asyncio
from research_analytics_suite.data_engine.variable_management.storage.BaseStorage import BaseStorage
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

    async def add_variable(self, name, value):
        """
        Adds a new variable to the storage.

        Args:
            name (str): The name of the variable.
            value: The value of the variable.
        """
        try:
            await self.storage.add_variable(name, value)
        except Exception as e:
            self._logger.error(Exception(f"Error adding variable '{name}': {e}"), self)

    async def get_variable(self, name):
        """
        Retrieves the value of a variable by name from the storage.

        Args:
            name (str): The name of the variable.

        Returns:
            The value of the variable.
        """
        try:
            return await self.storage.get_variable_value(name)
        except Exception as e:
            self._logger.error(Exception(f"Error retrieving variable '{name}': {e}"), self)

    async def remove_variable(self, name):
        """
        Removes a variable by name from the storage.

        Args:
            name (str): The name of the variable to remove.
        """
        try:
            await self.storage.remove_variable(name)
        except Exception as e:
            self._logger.error(Exception(f"Error removing variable '{name}': {e}"), self)

    async def list_variables(self) -> dict:
        """
        Lists all variables from the storage.

        Returns:
            dict: A dictionary of all variables.
        """
        try:
            return await self.storage.list_variables()
        except Exception as e:
            self._logger.error(Exception(f"Error listing variables: {e}"), self)

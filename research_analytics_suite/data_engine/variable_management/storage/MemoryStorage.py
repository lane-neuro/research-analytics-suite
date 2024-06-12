"""
Memory Storage Module

This module defines the in-memory storage backend for user variables.

Author: Lane
"""
from typing import Any

from research_analytics_suite.data_engine.variable_management.storage.BaseStorage import BaseStorage


class MemoryStorage(BaseStorage):
    """
    In-memory storage implementation for user variables.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._variables = {}
        self._logger.info(f"[Memory] Class initialized. Backup path: {self.db_path}")

    async def setup(self):
        # No setup required for in-memory storage
        pass

    async def add_variable(self, name, value):
        """
        Adds a new variable to the in-memory storage.

        Args:
            name (str): The name of the variable.
            value: The value of the variable.
        """
        try:
            self._variables[name] = value
        except Exception as e:
            self._logger.error(Exception(f"Error adding variable '{name}': {e}"), self)

    async def get_variable_value(self, name):
        """
        Retrieves the value of a variable by name from the in-memory storage.

        Args:
            name (str): The name of the variable.

        Returns:
            The value of the variable.
        """
        try:
            return self._variables[name]
        except Exception as e:
            self._logger.error(Exception(f"Error retrieving variable '{name}': {e}"), self)

    async def remove_variable(self, name):
        """
        Removes a variable by name from the in-memory storage.

        Args:
            name (str): The name of the variable to remove.
        """
        try:
            if name in self._variables:
                del self._variables[name]
        except Exception as e:
            self._logger.error(Exception(f"Error removing variable '{name}': {e}"), self)

    async def list_variables(self) -> dict:
        """
        Lists all variables from the in-memory storage.

        Returns:
            dict: A dictionary of all variables.
        """
        try:
            return self._variables
        except Exception as e:
            self._logger.error(Exception(f"Error listing variables: {e}"), self)

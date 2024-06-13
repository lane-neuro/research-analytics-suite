"""
MemoryStorage Module

This module defines the in-memory storage backend for user variables.

Author: Lane
"""
from research_analytics_suite.data_engine.variable_management.storage.BaseStorage import BaseStorage


class MemoryStorage(BaseStorage):
    """
    In-memory storage implementation for user variables.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._variables = {}
        self._logger.info(f"[MemoryStorage] initialized. Backup path: {self.db_path}")

    async def setup(self):
        # No setup required for in-memory storage
        pass

    async def add_variable(self, name, value, memory_id=None) -> dict:
        """
        Adds a new variable to the in-memory storage.

        Args:
            name (str): The name of the variable.
            value: The value of the variable.
            memory_id (str, optional): The ID of the memory to which the variable belongs.
        """
        try:
            if memory_id is None:
                self._variables[name] = value
            else:
                if memory_id not in self._variables:
                    self._variables[memory_id] = {}
                self._variables[memory_id][name] = value
            return await self.get_variable_value(name, memory_id)
        except Exception as e:
            self._logger.error(Exception(f"Error adding variable '{name}' with memory_id '{memory_id}': {e}"), self)

    async def get_variable_value(self, name, memory_id=None):
        """
        Retrieves the value of a variable by name from the in-memory storage.

        Args:
            name (str): The name of the variable.
            memory_id (str, optional): The ID of the memory to which the variable belongs.

        Returns:
            The value of the variable.
        """
        try:
            if memory_id is None:
                return self._variables[name]
            else:
                return self._variables[memory_id][name]
        except Exception as e:
            self._logger.error(Exception(f"Error retrieving variable '{name}' with memory_id '{memory_id}': {e}"), self)

    async def remove_variable(self, name, memory_id=None):
        """
        Removes a variable by name from the in-memory storage.

        Args:
            name (str): The name of the variable to remove.
            memory_id (str, optional): The ID of the memory to which the variable belongs.
        """
        try:
            if memory_id is None:
                if name in self._variables:
                    del self._variables[name]
            else:
                if memory_id in self._variables and name in self._variables[memory_id]:
                    del self._variables[memory_id][name]
        except Exception as e:
            self._logger.error(Exception(f"Error removing variable '{name}' with memory_id '{memory_id}': {e}"), self)

    async def list_variables(self, memory_id=None) -> dict:
        """
        Lists all variables from the in-memory storage.

        Args:
            memory_id (str, optional): The ID of the memory to list variables from.

        Returns:
            dict: A dictionary of all variables.
        """
        try:
            if memory_id is None:
                return self._variables
            else:
                return self._variables.get(memory_id)
        except Exception as e:
            self._logger.error(Exception(f"Error listing variables with memory_id '{memory_id}': {e}"), self)

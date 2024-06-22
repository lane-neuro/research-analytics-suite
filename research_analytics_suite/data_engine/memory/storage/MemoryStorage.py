"""
MemoryStorage Module

This module defines the in-memory storage backend for user variables.

Author: Lane
"""
from typing import Tuple

from research_analytics_suite.data_engine.memory.storage.BaseStorage import BaseStorage


class MemoryStorage(BaseStorage):
    """
    In-memory storage implementation for user variables.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._variables = dict[str, dict[str, any]]()
        self._logger.info(f"[MemoryStorage] initialized. Backup path: {self.db_path}")

    async def setup(self):
        # No setup required for in-memory storage
        pass

    async def add_variable(self, name, value, memory_id=None) -> Tuple[str, dict]:
        """
        Adds a new variable to the in-memory storage.

        Args:
            name (str): The name of the variable.
            value: The value of the variable.
            memory_id (str, optional): The ID of the memory to which the variable belongs.

        Returns:
            str: The memory_id location of the stored variable in the in-memory storage.
            dict[name, value]:
                name (str): The name of the variable. (aka: the key)
                value: The value of the stored variable in the associated memory_id location.
        """
        if memory_id is None:
            memory_id = self._GENERAL_MEMORY_ID

        try:
            if memory_id not in self._variables:
                self._variables[memory_id] = dict()
            self._variables[memory_id][name] = value

            return await self.get_variable_value(name, memory_id)
        except Exception as e:
            self._logger.error(Exception(f"Error adding variable '{name}' with memory_id '{memory_id}': {e}"), self)

    async def get_variable_value(self, name, memory_id=None) -> Tuple[str, dict]:
        """
        Retrieves the value of a variable by name from the in-memory storage.

        Args:
            name (str): The name of the variable.
            memory_id (str, optional): The ID of the memory to which the variable belongs.

        Returns:
            str: The memory_id location of the stored variable in the user_variables database.
            dict[name, value]:
                name (str): The name of the variable. (aka: the key)
                value: The value of the stored variable in the associated memory_id location.
        """
        _memory_id = memory_id
        if _memory_id is None:
            _memory_id = self._GENERAL_MEMORY_ID

        _name = name
        _value = None

        try:
            if _memory_id not in self._variables.keys():
                raise KeyError(f"Memory ID '{_memory_id}' not found in memory storage")

            if _name not in self._variables[_memory_id].keys():
                raise KeyError(f"Variable '{_name}' not found in memory storage with memory ID '{_memory_id}'")

            _value = self._variables[_memory_id][_name]
            return _memory_id, {_name: _value}

        except Exception as e:
            self._logger.error(
                Exception(f"Error retrieving variable '{_name}' with memory_id '{_memory_id}': {e}"), self)

    async def remove_variable(self, name, memory_id=None):
        """
        Removes a variable by name from the in-memory storage.

        Args:
            name (str): The name of the variable to remove.
            memory_id (str, optional): The ID of the memory to which the variable belongs.
        """
        try:
            if memory_id is None:
                if name in self._variables[self._GENERAL_MEMORY_ID]:
                    del self._variables[self._GENERAL_MEMORY_ID][name]
                    return

                else:
                    raise KeyError(f"Variable '{name}' not found in general memory slot '{self._GENERAL_MEMORY_ID}'")

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
            dict: A dictionary of variables.
        """
        try:
            if memory_id is None:
                return self._variables
            return self._variables[memory_id]
        except Exception as e:
            self._logger.error(Exception(f"Error listing variables with memory_id '{memory_id}': {e}"), self)

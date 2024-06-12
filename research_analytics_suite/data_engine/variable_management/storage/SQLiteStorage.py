"""
SQLite Storage Module

This module defines the SQLite storage backend for user variables.

Author: Lane
"""

import json
import aiosqlite
from research_analytics_suite.data_engine.variable_management.storage.BaseStorage import BaseStorage
from research_analytics_suite.utils.CustomLogger import CustomLogger


class SQLiteStorage(BaseStorage):
    """
    SQLite storage implementation for user variables.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger.info(f"[SQLite] Class initialized. Path: {self.db_path}")

    async def setup(self):
        """
        Sets up the SQLite database and creates the variables table if it does not exist.
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS variables (
                        name TEXT PRIMARY KEY,
                        value BLOB
                    )
                """)
                await conn.commit()
            self._logger.info(f"[SQLite] Database setup complete. Path: {self.db_path}")
        except Exception as e:
            self._logger.error(Exception(f"Error setting up SQLite database: {e}"), self)

    async def add_variable(self, name, value):
        """
        Adds a new variable to the SQLite database.

        Args:
            name (str): The name of the variable.
            value: The value of the variable.
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("REPLACE INTO variables (name, value) VALUES (?, ?)", (name, json.dumps(value)))
                await conn.commit()
        except Exception as e:
            self._logger.error(Exception(f"Error adding variable '{name}': {e}"), self)

    async def get_variable(self, name):
        """
        Retrieves the value of a variable by name from the SQLite database.

        Args:
            name (str): The name of the variable.

        Returns:
            The value of the variable.
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                async with conn.execute("SELECT value FROM variables WHERE name = ?", (name,)) as cursor:
                    row = await cursor.fetchone()
                    return json.loads(row[0]) if row else None
        except Exception as e:
            self._logger.error(Exception(f"Error retrieving variable '{name}': {e}"), self)

    async def remove_variable(self, name):
        """
        Removes a variable by name from the SQLite database.

        Args:
            name (str): The name of the variable to remove.
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("DELETE FROM variables WHERE name = ?", (name,))
                await conn.commit()
        except Exception as e:
            self._logger.error(Exception(f"Error removing variable '{name}': {e}"), self)

    async def list_variables(self):
        """
        Lists all variables from the SQLite database.

        Returns:
            dict: A dictionary of all variables.
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                async with conn.execute("SELECT name, value FROM variables") as cursor:
                    rows = await cursor.fetchall()
                    return {name: json.loads(value) for name, value in rows}
        except Exception as e:
            self._logger.error(Exception(f"Error listing variables: {e}"), self)

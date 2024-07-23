"""
SQLiteStorage Module

This module defines the SQLiteStorage class for storing data in an SQLite database.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import aiosqlite
import pickle
from research_analytics_suite.utils import CustomLogger


class SQLiteStorage:
    """
    A class to manage storage of data in an SQLite database.

    Attributes:
        db_path (str): The path to the SQLite database file.
        _logger (CustomLogger): Logger instance for logging events.
    """

    def __init__(self, db_path='database.db'):
        """
        Initializes the SQLiteStorage instance.

        Args:
            db_path (str): The path to the SQLite database file.
        """
        self.db_path = db_path
        self._logger = CustomLogger()

    async def setup(self):
        """
        Sets up the SQLite database and creates the variables table if it does not exist.
        """
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS variables (
                    name TEXT PRIMARY KEY,
                    value BLOB
                )
            """)
            await conn.commit()

    async def add_variable(self, name: str, value: any):
        """
        Adds a variable to the SQLite database.

        Args:
            name (str): The name of the variable.
            value (any): The value of the variable.
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("REPLACE INTO variables (name, value) VALUES (?, ?)",
                                   (name, pickle.dumps(value)))
                await conn.commit()
        except Exception as e:
            self._logger.error(Exception(f"[SQLite] Add variable error: {e}"), self.__class__.__name__)

    async def get_variable(self, name: str) -> any:
        """
        Retrieves a variable from the SQLite database.

        Args:
            name (str): The name of the variable.

        Returns:
            any: The value of the variable or None if not found.
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                async with conn.execute("SELECT value FROM variables WHERE name = ?", (name,)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return pickle.loads(row[0])
                    return None
        except Exception as e:
            self._logger.error(Exception(f"[SQLite] Get variable error: {e}"), self.__class__.__name__)

    async def update_variable(self, name: str, value: any):
        """
        Updates a variable in the SQLite database.

        Args:
            name (str): The name of the variable.
            value (any): The new value of the variable.
        """
        await self.add_variable(name, value)

    async def delete_variable(self, name: str):
        """
        Deletes a variable from the SQLite database.

        Args:
            name (str): The name of the variable.
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("DELETE FROM variables WHERE name = ?", (name,))
                await conn.commit()
        except Exception as e:
            self._logger.error(Exception(f"[SQLite] Delete variable error: {e}"), self.__class__.__name__)

    async def list_variables(self) -> dict:
        """
        Lists all variables in the SQLite database.

        Returns:
            dict: A dictionary of variable names and values.
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                async with conn.execute("SELECT name, value FROM variables") as cursor:
                    rows = await cursor.fetchall()
                    return {row[0]: pickle.loads(row[1]) for row in rows}
        except Exception as e:
            self._logger.error(Exception(f"[SQLite] List variables error: {e}"), self.__class__.__name__)
            return {}

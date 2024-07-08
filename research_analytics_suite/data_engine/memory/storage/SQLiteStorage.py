import json
import aiosqlite
from research_analytics_suite.data_engine.memory.storage.BaseStorage import BaseStorage


class SQLiteStorage(BaseStorage):
    """
    SQLite storage implementation for user variables.
    """

    async def add_collection(self, collection) -> str:  # pragma: no cover
        pass

    async def get_collection(self, collection_id: str): # pragma: no cover
        pass

    async def remove_collection(self, collection_id: str):  # pragma: no cover
        pass

    async def list_collections(self) -> dict:   # pragma: no cover
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_path = kwargs.get('db_path', 'database.db')

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
            self._logger.error(f"[SQLite] Setup error: {e}", self.__class__.__name__)

    async def add_variable(self, name: str, value: dict, memory_id=None):
        try:
            self._logger.info(f"[SQLite] Adding variable: {name} with value: {value}")
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("REPLACE INTO variables (name, value) VALUES (?, ?)", (name, json.dumps(value)))
                await conn.commit()
            self._logger.info(f"[SQLite] Variable '{name}' added/updated successfully.")
        except json.JSONDecodeError as e:
            self._logger.error(f"[SQLite] JSON encoding error: {e}", self.__class__.__name__)
        except aiosqlite.Error as e:
            self._logger.error(f"[SQLite] Database error: {e}", self.__class__.__name__)
        except Exception as e:
            self._logger.error(f"[SQLite] Add variable error: {e}", self.__class__.__name__)

    async def get_variable_value(self, name: str, memory_id=None):
        """
        Retrieves the value of a variable by name from the SQLite database.
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                async with conn.execute("SELECT value FROM variables WHERE name = ?", (name,)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return json.loads(row[0])
                    return None
        except json.JSONDecodeError as e:
            self._logger.error(f"[SQLite] JSON decoding error: {e}", self.__class__.__name__)
        except aiosqlite.Error as e:
            self._logger.error(f"[SQLite] Database error: {e}", self.__class__.__name__)
        except Exception as e:
            self._logger.error(f"[SQLite] Get variable value error: {e}", self.__class__.__name__)
            return None

    async def remove_variable(self, name: str, memory_id=None):
        """
        Removes a variable by name from the SQLite database.
        """
        try:
            self._logger.info(f"[SQLite] Removing variable: {name}")
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("DELETE FROM variables WHERE name = ?", (name,))
                await conn.commit()
            self._logger.info(f"[SQLite] Variable '{name}' removed successfully.")
        except aiosqlite.Error as e:
            self._logger.error(f"[SQLite] Database error: {e}", self.__class__.__name__)
        except Exception as e:
            self._logger.error(f"[SQLite] Remove variable error: {e}", self.__class__.__name__)

    async def list_variables(self, memory_id=None) -> dict:
        """
        Lists all variables from the SQLite database.
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                async with conn.execute("SELECT name, value FROM variables") as cursor:
                    rows = await cursor.fetchall()
                    return {name: json.loads(value) for name, value in rows}
        except json.JSONDecodeError as e:
            self._logger.error(f"[SQLite] JSON decoding error: {e}", self.__class__.__name__)
        except aiosqlite.Error as e:
            self._logger.error(f"[SQLite] Database error: {e}", self.__class__.__name__)
        except Exception as e:
            self._logger.error(f"[SQLite] List variables error: {e}", self.__class__.__name__)
            return {}

    async def update_variable(self, name: str, value: dict, memory_id=None):
        """
        Updates the value of an existing variable in the SQLite database.
        """
        await self.add_variable(name, value, memory_id)

    async def variable_exists(self, name: str, memory_id=None) -> bool:
        """
        Checks if a variable exists in the SQLite database.
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                async with conn.execute("SELECT 1 FROM variables WHERE name = ?", (name,)) as cursor:
                    return await cursor.fetchone() is not None
        except aiosqlite.Error as e:
            self._logger.error(f"[SQLite] Database error: {e}", self.__class__.__name__)
            return False
        except Exception as e:
            self._logger.error(f"[SQLite] Variable exists check error: {e}", self.__class__.__name__)
            return False

    async def get_variable_names(self, memory_id=None) -> list:
        """
        Retrieves all variable names from the SQLite database.
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                async with conn.execute("SELECT name FROM variables") as cursor:
                    rows = await cursor.fetchall()
                    return [row[0] for row in rows]
        except aiosqlite.Error as e:
            self._logger.error(f"[SQLite] Database error: {e}", self.__class__.__name__)
            return []
        except Exception as e:
            self._logger.error(f"[SQLite] Get variable names error: {e}", self.__class__.__name__)
            return []

    async def clear_variables(self, memory_id=None):
        """
        Clears all variables from the SQLite database.
        """
        try:
            self._logger.info("[SQLite] Clearing all variables.")
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("DELETE FROM variables")
                await conn.commit()
            self._logger.info("[SQLite] All variables cleared successfully.")
        except aiosqlite.Error as e:
            self._logger.error(f"[SQLite] Database error: {e}", self.__class__.__name__)
        except Exception as e:
            self._logger.error(f"[SQLite] Clear variables error: {e}", self.__class__.__name__)

"""
TestSQLiteStorage Module

This module contains tests for the SQLiteStorage class.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import pytest
import aiosqlite
import tempfile
import os
from research_analytics_suite.data_engine.memory.SQLiteStorage import SQLiteStorage


@pytest.fixture(scope='class')
async def sqlite_storage():
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = f"{temp_dir}/test.db"
        storage = SQLiteStorage(db_path=db_path)
        await storage.setup()
        yield storage


@pytest.mark.asyncio
class TestSQLiteStorage:
    """
    A test class for SQLiteStorage.
    """

    @pytest.fixture(autouse=True)
    async def setup_class(self, sqlite_storage):
        """
        Sets up the class-level fixture for SQLiteStorage.

        Args:
            sqlite_storage (SQLiteStorage): The SQLiteStorage instance.
        """
        self.storage = sqlite_storage

    async def test_sqlite_storage_setup(self):
        """
        Tests if the SQLiteStorage is set up properly.
        """
        assert os.path.exists(self.storage.db_path)

    async def test_sqlite_add_get_variable(self):
        """
        Tests adding and getting a variable in SQLiteStorage.
        """
        await self.storage.add_variable("test_var", {"key": "value"})
        value = await self.storage.get_variable("test_var")
        assert value == {"key": "value"}

    async def test_sqlite_update_variable(self):
        """
        Tests updating a variable in SQLiteStorage.
        """
        await self.storage.add_variable("test_var", {"key": "value"})
        await self.storage.update_variable("test_var", {"new_key": "new_value"})
        value = await self.storage.get_variable("test_var")
        assert value == {"new_key": "new_value"}

    async def test_sqlite_delete_variable(self):
        """
        Tests deleting a variable in SQLiteStorage.
        """
        await self.storage.add_variable("test_var", {"key": "value"})
        await self.storage.delete_variable("test_var")
        value = await self.storage.get_variable("test_var")
        assert value is None

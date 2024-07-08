import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import pytest_asyncio

from research_analytics_suite.data_engine.memory.storage.SQLiteStorage import SQLiteStorage


class TestSQLiteStorage:
    @pytest.fixture(autouse=True)
    def setup_logger(self):
        self.mock_logger = MagicMock()
        self.mock_logger.debug = MagicMock()
        self.mock_logger.error = MagicMock()
        self.mock_logger.info = MagicMock()

    @pytest_asyncio.fixture
    async def storage(self):
        with patch('research_analytics_suite.utils.CustomLogger', return_value=self.mock_logger):
            storage = SQLiteStorage(db_path="example.db")
            await storage.setup()
            await storage.clear_variables()  # Clear variables before each test
            return storage

    @pytest.mark.asyncio
    async def test_setup(self, storage):
        assert storage.db_path == "example.db"
        assert storage._logger.info.called
        assert storage._logger.error.called is False

    @pytest.mark.asyncio
    async def test_add_variable(self, storage):
        await storage.add_variable("test_var", {"key": "value"})
        result = await storage.get_variable_value("test_var")
        assert result == {"key": "value"}

    @pytest.mark.asyncio
    async def test_get_variable_value(self, storage):
        await storage.add_variable("test_var", {"key": "value"})
        result = await storage.get_variable_value("test_var")
        assert result == {"key": "value"}
        non_existent = await storage.get_variable_value("non_existent_var")
        assert non_existent is None

    @pytest.mark.asyncio
    async def test_remove_variable(self, storage):
        await storage.add_variable("test_var", {"key": "value"})
        await storage.remove_variable("test_var")
        result = await storage.get_variable_value("test_var")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_variables(self, storage):
        await storage.add_variable("test_var1", {"key": "value1"})
        await storage.add_variable("test_var2", {"key": "value2"})
        result = await storage.list_variables()
        assert result == {"test_var1": {"key": "value1"}, "test_var2": {"key": "value2"}}

    @pytest.mark.asyncio
    async def test_update_variable(self, storage):
        await storage.add_variable("test_var", {"key": "value"})
        await storage.update_variable("test_var", {"key": "new_value"})
        result = await storage.get_variable_value("test_var")
        assert result == {"key": "new_value"}

    @pytest.mark.asyncio
    async def test_variable_exists(self, storage):
        await storage.add_variable("test_var", {"key": "value"})
        exists = await storage.variable_exists("test_var")
        assert exists is True
        not_exists = await storage.variable_exists("non_existent_var")
        assert not_exists is False

    @pytest.mark.asyncio
    async def test_get_variable_names(self, storage):
        await storage.add_variable("test_var1", {"key": "value1"})
        await storage.add_variable("test_var2", {"key": "value2"})
        result = await storage.get_variable_names()
        assert set(result) == {"test_var1", "test_var2"}

    @pytest.mark.asyncio
    async def test_clear_variables(self, storage):
        await storage.add_variable("test_var1", {"key": "value1"})
        await storage.add_variable("test_var2", {"key": "value2"})
        await storage.clear_variables()
        result = await storage.list_variables()
        assert result == {}

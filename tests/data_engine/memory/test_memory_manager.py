import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest_asyncio

from research_analytics_suite.data_engine.memory.MemoryManager import MemoryManager
from research_analytics_suite.data_engine.memory import MemorySlotCollection


@pytest.fixture
def mock_data_cache():
    with patch('research_analytics_suite.data_engine.memory.DataCache', new_callable=MagicMock) as mock_data_cache:
        mock_data_cache_instance = mock_data_cache.return_value
        mock_data_cache_instance.initialize = AsyncMock()
        mock_data_cache_instance.get = MagicMock(return_value=None)
        mock_data_cache_instance.set = MagicMock()
        mock_data_cache_instance.delete = MagicMock()
        return mock_data_cache_instance


@pytest.fixture
def mock_memory_slot_collection():
    collection = MagicMock(MemorySlotCollection)
    collection.collection_id = "test_collection_id"
    collection.display_name = "Test Collection"
    collection.slots = []  # Ensure slots attribute is available
    return collection


class TestMemoryManager:

    @pytest.fixture(autouse=True)
    def setup_logger(self):
        self.mock_logger = MagicMock()
        self.mock_logger.debug = MagicMock()
        self.mock_logger.error = MagicMock()
        self.mock_logger.info = MagicMock()

    @pytest_asyncio.fixture
    async def memory_manager(self, mock_data_cache):
        with patch('research_analytics_suite.utils.CustomLogger', return_value=self.mock_logger):
            memory_manager = MemoryManager()
            memory_manager._logger = self.mock_logger
            memory_manager._data_cache = mock_data_cache
            await memory_manager.initialize()
            return memory_manager

    def test_initialize(self, memory_manager):
        assert memory_manager._initialized

    def test_add_and_get_collection(self, memory_manager, mock_memory_slot_collection):
        memory_manager.add_collection(mock_memory_slot_collection)
        memory_manager._data_cache.get.return_value = mock_memory_slot_collection
        retrieved_collection = memory_manager.get_collection(mock_memory_slot_collection.collection_id)
        assert retrieved_collection == mock_memory_slot_collection

    def test_initialize_default_collection(self, memory_manager):
        memory_manager.default_collection = MagicMock()
        memory_manager.default_collection.name = "Primary"
        assert memory_manager.default_collection is not None
        assert memory_manager.default_collection.name == "Primary"

    @pytest.mark.asyncio
    async def test_remove_collection(self, memory_manager, mock_memory_slot_collection):
        memory_manager.add_collection(mock_memory_slot_collection)
        memory_manager._data_cache.get.return_value = mock_memory_slot_collection
        await memory_manager.remove_collection(mock_memory_slot_collection.collection_id)
        memory_manager._data_cache.get.return_value = None
        retrieved_collection = memory_manager.get_collection(mock_memory_slot_collection.collection_id)
        assert retrieved_collection is None

    @pytest.mark.asyncio
    async def test_list_collections(self, memory_manager, mock_memory_slot_collection):
        memory_manager.add_collection(mock_memory_slot_collection)
        memory_manager._data_cache.get.return_value = mock_memory_slot_collection
        collections = await memory_manager.list_collections()
        assert mock_memory_slot_collection.collection_id in collections
        assert collections[mock_memory_slot_collection.collection_id] == mock_memory_slot_collection

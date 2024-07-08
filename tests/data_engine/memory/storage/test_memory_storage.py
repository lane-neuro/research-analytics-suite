# test_memory_storage.py

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from research_analytics_suite.data_engine.memory.storage.MemoryStorage import MemoryStorage
from research_analytics_suite.data_engine.memory.MemorySlotCollection import MemorySlotCollection


class TestMemoryStorage:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_logger = MagicMock()
        self.mock_logger.debug = MagicMock()
        self.mock_logger.error = MagicMock()
        self.mock_logger.info = MagicMock()

    @pytest.fixture
    def storage(self):
        with patch('research_analytics_suite.data_engine.memory.storage.BaseStorage.CustomLogger', return_value=self.mock_logger):
            return MemoryStorage(db_path=":memory:")

    @pytest.fixture
    def collection(self):
        collection = MemorySlotCollection(name="Test Collection")
        return collection

    @pytest.mark.asyncio
    async def test_add_collection(self, storage, collection):
        await storage.add_collection(collection)
        assert storage.collections[collection.collection_id] == collection

    @pytest.mark.asyncio
    async def test_get_collection(self, storage, collection):
        await storage.add_collection(collection)
        retrieved_collection = await storage.get_collection(collection.collection_id)
        assert retrieved_collection == collection

    @pytest.mark.asyncio
    async def test_remove_collection(self, storage, collection):
        await storage.add_collection(collection)
        await storage.remove_collection(collection.collection_id)
        assert collection.collection_id not in storage.collections

    @pytest.mark.asyncio
    async def test_list_collections(self, storage, collection):
        await storage.add_collection(collection)
        collections = await storage.list_collections()
        assert len(collections) == 1
        assert collections[collection.collection_id] == collection

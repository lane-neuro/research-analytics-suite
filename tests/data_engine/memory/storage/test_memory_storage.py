# test_memory_storage.py

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
from research_analytics_suite.data_engine.memory.storage.MemoryStorage import MemoryStorage
from research_analytics_suite.data_engine.memory.MemorySlotCollection import MemorySlotCollection
from research_analytics_suite.data_engine.memory.MemorySlot import MemorySlot


class TestMemoryStorage:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_logger = MagicMock()
        self.mock_logger.debug = MagicMock()
        self.mock_logger.error = MagicMock()
        self.mock_logger.info = MagicMock()

    @pytest.fixture
    def storage(self):
        with patch('research_analytics_suite.utils.CustomLogger', return_value=self.mock_logger):
            return MemoryStorage(db_path=":memory:")

    @pytest.fixture
    def collection(self):
        collection = MemorySlotCollection(name="Test Collection")
        return collection

    @pytest.fixture
    def slot(self):
        return MemorySlot(memory_id=str(uuid.uuid4()), data={"key": (str, "value")}, operation_required=False, name="Test Slot")

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

    @pytest.mark.asyncio
    async def test_add_multiple_collections(self, storage):
        collection1 = MemorySlotCollection(name="Collection 1")
        collection2 = MemorySlotCollection(name="Collection 2")
        await storage.add_collection(collection1)
        await storage.add_collection(collection2)
        collections = await storage.list_collections()
        assert len(collections) == 2
        assert collections[collection1.collection_id] == collection1
        assert collections[collection2.collection_id] == collection2

    @pytest.mark.asyncio
    async def test_remove_non_existent_collection(self, storage):
        non_existent_id = "non_existent_id"
        await storage.remove_collection(non_existent_id)  # Should not raise an error
        assert non_existent_id not in storage.collections

    @pytest.mark.asyncio
    async def test_get_non_existent_collection(self, storage):
        non_existent_id = "non_existent_id"
        collection = await storage.get_collection(non_existent_id)
        assert collection is None

    @pytest.mark.asyncio
    async def test_add_and_remove_slots_in_collection(self, storage, collection, slot):
        await storage.add_collection(collection)
        collection.add_slot(slot)
        assert slot in collection.slots

        await collection.remove_slot(slot.memory_id)
        assert slot not in collection.slots

    @pytest.mark.asyncio
    async def test_clear_slots_in_collection(self, storage, collection, slot):
        await storage.add_collection(collection)
        collection.add_slot(slot)
        await collection.clear_slots()
        assert len(collection.slots) == 0

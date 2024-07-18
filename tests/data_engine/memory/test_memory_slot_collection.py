import json

import pytest
from unittest.mock import AsyncMock, MagicMock

from research_analytics_suite.data_engine import MemorySlotCollection
from research_analytics_suite.data_engine.memory import MemorySlot


class TestMemorySlotCollection:

    def test_initialization(self):
        collection = MemorySlotCollection(name="Test Collection")
        assert collection.name == "Test Collection"
        assert len(collection.collection_id) == 32

    def test_initialization_without_name(self):
        collection = MemorySlotCollection()
        assert collection.name.startswith("Collection - ")
        assert len(collection.collection_id) == 32

    def test_set_name_with_valid_string(self):
        collection = MemorySlotCollection(name="Initial Name")
        new_name = "Updated Name"
        collection.name = new_name
        assert collection.name == new_name

    def test_set_name_with_invalid_type(self):
        collection = MemorySlotCollection(name="Initial Name")
        with pytest.raises(ValueError, match="name must be a string"):
            collection.name = 123  # Trying to set name with a non-string type

    def test_set_name_and_retrieve(self):
        collection = MemorySlotCollection(name="Initial Name")
        new_name = "Updated Name"
        collection.name = new_name
        retrieved_name = collection.name
        assert retrieved_name == new_name

    def test_set_name_with_empty_string(self):
        collection = MemorySlotCollection(name="Initial Name")
        new_name = ""
        collection.name = new_name
        assert collection.name == new_name

    def test_display_name(self):
        collection = MemorySlotCollection(name="Test Collection")
        assert collection.display_name.startswith("Test Collection [")

    def test_add_and_list_slots(self):
        collection = MemorySlotCollection()
        slot = MagicMock(spec=MemorySlot)
        collection.add_slot(slot)
        assert collection.list_slots == [slot]

    def test_new_slot_with_data(self):
        collection = MemorySlotCollection()
        data = {"key": (str, "value")}
        slot = collection.new_slot_with_data(data)
        assert slot.data == data
        assert slot in collection.list_slots

    @pytest.mark.asyncio
    async def test_remove_slot(self):
        collection = MemorySlotCollection()
        slot = MagicMock(spec=MemorySlot)
        slot.memory_id = "test_id"
        collection.add_slot(slot)
        await collection.remove_slot("test_id")
        assert collection.list_slots == []

    def test_get_slot(self):
        collection = MemorySlotCollection()
        slot = MagicMock(spec=MemorySlot)
        slot.memory_id = "test_id"
        collection.add_slot(slot)
        assert collection.get_slot("test_id") == slot

    def test_get_slot_data(self):
        collection = MemorySlotCollection()
        slot = MagicMock(spec=MemorySlot)
        slot.memory_id = "test_id"
        slot.data = {"key": "value"}
        collection.add_slot(slot)
        assert collection.get_slot_data("test_id") == {"key": "value"}

    @pytest.mark.asyncio
    async def test_clear_slots(self):
        collection = MemorySlotCollection()
        slot = MagicMock(spec=MemorySlot)
        collection.add_slot(slot)
        await collection.clear_slots()
        assert collection.list_slots == []

    @pytest.mark.asyncio
    async def test_update_slot(self):
        collection = MemorySlotCollection()
        slot = MagicMock(spec=MemorySlot)
        slot.memory_id = "test_id"
        collection.add_slot(slot)
        updated_slot = MagicMock(spec=MemorySlot)
        updated_slot.memory_id = "test_id"
        await collection.update_slot(updated_slot)
        assert collection.get_slot("test_id") == updated_slot

    @pytest.mark.asyncio
    async def test_slot_exists(self):
        collection = MemorySlotCollection()
        slot = MagicMock(spec=MemorySlot)
        slot.memory_id = "test_id"
        collection.add_slot(slot)
        assert await collection.slot_exists("test_id") is True
        assert await collection.slot_exists("non_existent_id") is False

    @pytest.mark.asyncio
    async def test_to_dict(self):
        collection = MemorySlotCollection(name="Test Collection")
        slot = MagicMock(spec=MemorySlot)
        slot.to_dict = AsyncMock(return_value={"memory_id": "test_id"})
        collection.add_slot(slot)
        result = await collection.to_dict()
        assert result == {
            'collection_id': collection.collection_id,
            'name': "Test Collection",
            'slots': [{"memory_id": "test_id"}]
        }

    @pytest.mark.asyncio
    async def test_from_dict(self):
        data = {
            'collection_id': "test_collection_id",
            'name': "Test Collection",
            'slots': [{"memory_id": "test_id"}]
        }
        slot_mock = AsyncMock(spec=MemorySlot)
        slot_mock.load_from_disk = AsyncMock(return_value=slot_mock)
        collection = await MemorySlotCollection.from_dict(data)
        assert collection.collection_id == "test_collection_id"
        assert collection.name == "Test Collection"
        assert len(collection.list_slots) == 1

    @pytest.mark.asyncio
    async def test_from_json(self):
        json_data = json.dumps({
            'collection_id': "test_collection_id",
            'name': "Test Collection",
            'slots': [{"memory_id": "test_id"}]
        })
        slot_mock = AsyncMock(spec=MemorySlot)
        slot_mock.load_from_disk = AsyncMock(return_value=slot_mock)
        collection = await MemorySlotCollection.from_json(json_data)
        assert collection.collection_id == "test_collection_id"
        assert collection.name == "Test Collection"
        assert len(collection.list_slots) == 1

    def test_filter_slots(self):
        collection = MemorySlotCollection()
        slot1 = MagicMock(spec=MemorySlot, operation_required=True)
        slot2 = MagicMock(spec=MemorySlot, operation_required=False)
        collection.add_slot(slot1)
        collection.add_slot(slot2)
        filtered_slots = collection.filter_slots(operation_required=True)
        assert filtered_slots == [slot1]

    def test_find_slots_by_name(self):
        collection = MemorySlotCollection()
        slot1 = MagicMock(spec=MemorySlot)
        slot1.name = "slot1"
        slot2 = MagicMock(spec=MemorySlot)
        slot2.name = "slot2"
        collection.add_slot(slot1)
        collection.add_slot(slot2)
        found_slots = collection.find_slots_by_name("slot1")
        assert found_slots == [slot1]

    def test_add_slots(self):
        collection = MemorySlotCollection()
        slot1 = MagicMock(spec=MemorySlot)
        slot2 = MagicMock(spec=MemorySlot)
        collection.add_slots([slot1, slot2])
        assert collection.list_slots == [slot1, slot2]

    def test_remove_slots(self):
        collection = MemorySlotCollection()
        slot1 = MagicMock(spec=MemorySlot)
        slot1.memory_id = "id1"
        slot2 = MagicMock(spec=MemorySlot)
        slot2.memory_id = "id2"
        collection.add_slot(slot1)
        collection.add_slot(slot2)
        collection.remove_slots(["id1", "id2"])
        assert collection.list_slots == []

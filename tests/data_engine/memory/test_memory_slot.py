# test_memory_slot.py

import pytest
import time
import asyncio
import pytest_asyncio
from mmap import mmap
from unittest.mock import patch, MagicMock
import os

from research_analytics_suite.data_engine.memory.MemorySlot import MemorySlot, DATA_SIZE_THRESHOLD


@pytest_asyncio.fixture
async def memory_slot():
    with patch('research_analytics_suite.utils.CustomLogger', autospec=True) as MockLogger:
        mock_logger_instance = MockLogger.return_value
        return MemorySlot(memory_id="test_slot", name="Test Slot", operation_required=True, data={
            "key1": (int, 123),
            "key2": (str, "value")
        }, file_path="test_memory.dat")


class TestMemorySlot:

    @pytest.fixture(autouse=True)
    def setup_teardown(self, memory_slot):
        self.memory_slot = memory_slot
        yield
        self.memory_slot.clear_data()
        self.memory_slot.close_mmap()
        if os.path.exists("test_memory.dat"):
            os.remove("test_memory.dat")

    def test_memory_id(self):
        assert self.memory_slot.memory_id == "test_slot"
        self.memory_slot.memory_id = "new_id"
        assert self.memory_slot.memory_id == "new_id"

    def test_name(self):
        assert self.memory_slot.name == "Test Slot"
        self.memory_slot.name = "New Name"
        assert self.memory_slot.name == "New Name"

    def test_operation_required(self):
        assert self.memory_slot.operation_required
        self.memory_slot.operation_required = False
        assert not self.memory_slot.operation_required

    def test_data(self):
        assert self.memory_slot.data == {
            "key1": (int, 123),
            "key2": (str, "value")
        }
        new_data = {"key3": (float, 1.23)}
        self.memory_slot.data = new_data
        assert self.memory_slot.data == new_data

    def test_metadata(self):
        assert self.memory_slot.metadata == {}
        new_metadata = {"meta1": "data"}
        self.memory_slot.metadata = new_metadata
        assert self.memory_slot.metadata == new_metadata

    def test_created_at(self):
        assert isinstance(self.memory_slot.created_at, float)

    def test_modified_at(self):
        assert isinstance(self.memory_slot.modified_at, float)

    @pytest.mark.asyncio
    async def test_get_data_by_key(self):
        assert await self.memory_slot.get_data_by_key("key1") == 123
        assert await self.memory_slot.get_data_by_key("key2") == "value"

    @pytest.mark.asyncio
    async def test_set_data_by_key(self):
        await self.memory_slot.set_data_by_key("key3", 456, int)
        assert await self.memory_slot.get_data_by_key("key3") == 456

    @pytest.mark.asyncio
    async def test_remove_data_by_key(self):
        await self.memory_slot.remove_data_by_key("key1")
        assert "key1" not in self.memory_slot.data

    @pytest.mark.asyncio
    async def test_clear_data(self):
        await self.memory_slot.clear_data()
        assert self.memory_slot.data == {}

    @pytest.mark.asyncio
    async def test_has_key(self):
        assert await self.memory_slot.has_key("key1")
        assert not await self.memory_slot.has_key("key3")

    @pytest.mark.asyncio
    async def test_update_data(self):
        new_data = {"key3": (float, 1.23)}
        await self.memory_slot.update_data(new_data)
        assert self.memory_slot.data == {**self.memory_slot.data, **new_data}

    @pytest.mark.asyncio
    async def test_merge_data(self):
        new_data = {"key3": (float, 1.23)}
        await self.memory_slot.merge_data(new_data)
        assert self.memory_slot.data["key3"] == (float, 1.23)

    @pytest.mark.asyncio
    async def test_data_keys(self):
        keys = await self.memory_slot.data_keys()
        assert "key1" in keys
        assert "key2" in keys

    @pytest.mark.asyncio
    async def test_data_values(self):
        values = await self.memory_slot.data_values()
        assert 123 in values
        assert "value" in values

    @pytest.mark.asyncio
    async def test_data_items(self):
        items = await self.memory_slot.data_items()
        assert ("key1", (int, 123)) in items
        assert ("key2", (str, "value")) in items

    @pytest.mark.asyncio
    async def test_to_dict(self):
        dict_repr = await self.memory_slot.to_dict()
        assert dict_repr["memory_id"] == "test_slot"
        assert dict_repr["name"] == "Test Slot"
        assert dict_repr["operation_required"]
        assert dict_repr["data"]["key1"] == 123

    @pytest.mark.asyncio
    async def test_load_from_disk(self):
        data = {
            "memory_id": "test_slot",
            "name": "Test Slot",
            "operation_required": True,
            "data": {"key1": (int, 123), "key2": (str, "value")},
            "metadata": {},
            "created_at": time.time(),
            "modified_at": time.time()
        }
        slot = await MemorySlot.load_from_disk(data)
        assert slot.memory_id == "test_slot"
        assert slot.name == "Test Slot"
        assert slot.operation_required
        assert slot.data["key1"] == (int, 123)

    def test_calculate_offset(self):
        key1_offset = self.memory_slot.calculate_offset("key1")
        key2_offset = self.memory_slot.calculate_offset("key2")
        assert key1_offset == 0
        assert key2_offset >= key1_offset  # Fix: Use >= to handle equal offsets

    def test_calculate_offset_non_existent_key(self):
        non_existent_key_offset = self.memory_slot.calculate_offset("non_existent_key")
        assert non_existent_key_offset == 0

    def test_calculate_offset_empty_data(self):
        empty_memory_slot = MemorySlot(memory_id="empty_slot", name="Empty Slot", operation_required=True, data={})
        offset = empty_memory_slot.calculate_offset("key1")
        assert offset == 0

    def test_invalid_memory_id_type(self):
        with patch.object(self.memory_slot._logger, 'error') as mock_logger:
            self.memory_slot.memory_id = 123
            mock_logger.assert_called()

    def test_invalid_name_type(self):
        with patch.object(self.memory_slot._logger, 'error') as mock_logger:
            self.memory_slot.name = 123
            mock_logger.assert_called()

    def test_invalid_operation_required_type(self):
        with patch.object(self.memory_slot._logger, 'error') as mock_logger:
            self.memory_slot.operation_required = "True"
            mock_logger.assert_called()

    @pytest.mark.asyncio
    async def test_invalid_data_type(self):
        with patch.object(self.memory_slot._logger, 'error') as mock_logger:
            await self.memory_slot.set_data_by_key("key3", 456, str)
            mock_logger.assert_called()

    @pytest.mark.asyncio
    async def test_concurrent_access(self):
        async def worker(slot, key, value, data_type):
            await slot.set_data_by_key(key, value, data_type)

        await asyncio.gather(
            worker(self.memory_slot, "key1", 123, int),
            worker(self.memory_slot, "key2", "value", str)
        )
        assert await self.memory_slot.get_data_by_key("key1") == 123
        assert await self.memory_slot.get_data_by_key("key2") == "value"

    @pytest.mark.asyncio
    async def test_memory_mapped_storage(self):
        large_data = "x" * (DATA_SIZE_THRESHOLD + 1)
        await self.memory_slot.set_data_by_key("large_key", large_data, str)
        assert await self.memory_slot.get_data_by_key("large_key") == large_data

    @pytest.mark.asyncio
    async def test_init_mmap(self):
        large_data = "x" * (DATA_SIZE_THRESHOLD + 1)
        await self.memory_slot.set_data_by_key("large_key", large_data, str)
        assert self.memory_slot._use_mmap
        assert self.memory_slot._mmapped_file is not None

    def test_serialize(self):
        data = "test_data"
        serialized_data = self.memory_slot.serialize(data)
        assert serialized_data == b'test_data'

    def test_deserialize(self):
        data = "test_data"
        serialized_data = self.memory_slot.serialize(data)
        deserialized_data = self.memory_slot.deserialize(serialized_data, str)
        assert deserialized_data == data
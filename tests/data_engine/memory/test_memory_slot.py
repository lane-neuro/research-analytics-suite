import pytest
import time
from research_analytics_suite.data_engine.memory.MemorySlot import MemorySlot


@pytest.fixture
def memory_slot():
    return MemorySlot(memory_id="test_slot", name="Test Slot", operation_required=True, data={
        "key1": (int, 123),
        "key2": (str, "value")
    })


def test_memory_id(memory_slot):
    assert memory_slot.memory_id == "test_slot"
    memory_slot.memory_id = "new_id"
    assert memory_slot.memory_id == "new_id"


def test_name(memory_slot):
    assert memory_slot.name == "Test Slot"
    memory_slot.name = "New Name"
    assert memory_slot.name == "New Name"


def test_operation_required(memory_slot):
    assert memory_slot.operation_required
    memory_slot.operation_required = False
    assert not memory_slot.operation_required


def test_data(memory_slot):
    assert memory_slot.data == {
        "key1": (int, 123),
        "key2": (str, "value")
    }
    new_data = {"key3": (float, 1.23)}
    memory_slot.data = new_data
    assert memory_slot.data == new_data


def test_metadata(memory_slot):
    assert memory_slot.metadata == {}
    new_metadata = {"meta1": "data"}
    memory_slot.metadata = new_metadata
    assert memory_slot.metadata == new_metadata


def test_created_at(memory_slot):
    assert isinstance(memory_slot.created_at, float)


def test_modified_at(memory_slot):
    assert isinstance(memory_slot.modified_at, float)


@pytest.mark.asyncio
async def test_get_data_by_key(memory_slot):
    assert await memory_slot.get_data_by_key("key1") == 123
    assert await memory_slot.get_data_by_key("key2") == "value"


@pytest.mark.asyncio
async def test_set_data_by_key(memory_slot):
    await memory_slot.set_data_by_key("key3", 456, int)
    assert await memory_slot.get_data_by_key("key3") == 456


@pytest.mark.asyncio
async def test_remove_data_by_key(memory_slot):
    await memory_slot.remove_data_by_key("key1")
    assert "key1" not in memory_slot.data


@pytest.mark.asyncio
async def test_clear_data(memory_slot):
    await memory_slot.clear_data()
    assert memory_slot.data == {}


@pytest.mark.asyncio
async def test_has_key(memory_slot):
    assert await memory_slot.has_key("key1")
    assert not await memory_slot.has_key("key3")


@pytest.mark.asyncio
async def test_update_data(memory_slot):
    new_data = {"key3": (float, 1.23)}
    await memory_slot.update_data(new_data)
    assert memory_slot.data == {**memory_slot.data, **new_data}


@pytest.mark.asyncio
async def test_merge_data(memory_slot):
    new_data = {"key3": (float, 1.23)}
    await memory_slot.merge_data(new_data)
    assert memory_slot.data["key3"] == (float, 1.23)


@pytest.mark.asyncio
async def test_data_keys(memory_slot):
    keys = await memory_slot.data_keys()
    assert "key1" in keys
    assert "key2" in keys


@pytest.mark.asyncio
async def test_data_values(memory_slot):
    values = await memory_slot.data_values()
    assert 123 in values
    assert "value" in values


@pytest.mark.asyncio
async def test_data_items(memory_slot):
    items = await memory_slot.data_items()
    assert ("key1", (int, 123)) in items
    assert ("key2", (str, "value")) in items


@pytest.mark.asyncio
async def test_to_dict(memory_slot):
    dict_repr = await memory_slot.to_dict()
    assert dict_repr["memory_id"] == "test_slot"
    assert dict_repr["name"] == "Test Slot"
    assert dict_repr["operation_required"]
    assert dict_repr["data"]["key1"] == 123


@pytest.mark.asyncio
async def test_load_from_disk():
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

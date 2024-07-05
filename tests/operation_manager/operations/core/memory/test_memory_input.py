import pytest
import numpy as np
from research_analytics_suite.data_engine.memory.MemorySlot import MemorySlot
from research_analytics_suite.operation_manager.operations.core.memory import MemoryInput


@pytest.fixture
def memory_input():
    mem_input = MemoryInput(name="TestMemoryInput")
    slot1 = MemorySlot(name="slot1", data={'values': (list, [1, 2, 3, 4, 5])}, memory_id="slot1", operation_required=True)
    slot2 = MemorySlot(name="slot2", data={'values': (list, [None, 2, None, 4, 5])}, memory_id="slot2", operation_required=False)
    mem_input.slots = [slot1, slot2]
    return mem_input


def test_add_dependency(memory_input):
    memory_input.add_dependency("slot1", "slot2")
    assert memory_input.list_dependencies("slot1") == ["slot2"]

    memory_input.add_dependency("slot1", "slot3")
    assert memory_input.list_dependencies("slot1") == ["slot2", "slot3"]


def test_remove_dependency(memory_input):
    memory_input.add_dependency("slot1", "slot2")
    memory_input.add_dependency("slot1", "slot3")

    memory_input.remove_dependency("slot1", "slot2")
    assert memory_input.list_dependencies("slot1") == ["slot3"]

    memory_input.remove_dependency("slot1", "slot3")
    assert memory_input.list_dependencies("slot1") == []


def test_list_dependencies(memory_input):
    memory_input.add_dependency("slot1", "slot2")
    memory_input.add_dependency("slot1", "slot3")

    dependencies = memory_input.list_dependencies("slot1")
    assert dependencies == ["slot2", "slot3"]

    dependencies_empty = memory_input.list_dependencies("slot2")
    assert dependencies_empty == []

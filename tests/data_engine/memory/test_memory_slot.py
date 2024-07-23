import pytest
import os
from research_analytics_suite.data_engine.memory.MemorySlot import MemorySlot


class TestMemorySlot:

    def test_memory_slot_initialization(self):
        slot = MemorySlot("1", "test_slot", {"key": "value"}, "test_mmap.dat")
        assert slot.memory_id == "1"
        assert slot.name == "test_slot"
        assert slot.get_data() == {"key": "value"}
        slot.close()  # Ensure the file is closed before deletion
        if os.path.exists("test_mmap.dat"):
            os.remove("test_mmap.dat")

    def test_memory_slot_large_data(self):
        large_data = "x" * int(2e6 + 1)
        slot = MemorySlot("1", "large_slot", large_data, "large_test_mmap.dat")
        assert slot.memory_id == "1"
        assert slot.name == "large_slot"
        assert slot.get_data() == large_data
        slot.close()  # Ensure the file is closed before deletion
        if os.path.exists("large_test_mmap.dat"):
            os.remove("large_test_mmap.dat")

    def test_memory_slot_set_data(self):
        slot = MemorySlot("1", "test_slot", {"key": "value"}, "test_mmap.dat")
        slot.set_data({"new_key": "new_value"})
        assert slot.get_data() == {"new_key": "new_value"}
        slot.close()  # Ensure the file is closed before deletion
        if os.path.exists("test_mmap.dat"):
            os.remove("test_mmap.dat")

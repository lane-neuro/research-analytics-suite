import pytest
import os
import tempfile
import asyncio
from research_analytics_suite.data_engine.memory.MemorySlot import MemorySlot


@pytest.fixture(scope='function')
@pytest.mark.asyncio
async def memory_slot():
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = f"{temp_dir}/test.db"
        slot = MemorySlot(
            "1", "test_slot", {"key": "value"}, db_path, f"{temp_dir}/test_mmap.dat")
        await slot.setup()
        yield slot
        slot.close()  # Ensure the slot is closed after each test
        if os.path.exists(f"{temp_dir}/test.db"):
            os.remove(f"{temp_dir}/test.db")
        if os.path.exists(f"{temp_dir}/test_mmap.dat"):
            os.remove(f"{temp_dir}/test_mmap.dat")


class TestMemorySlot:

    @pytest.mark.asyncio
    async def test_initial_data(self, memory_slot):
        data = await memory_slot.data
        assert data == {"key": "value"}, "Initial data should match the provided value."

    @pytest.mark.asyncio
    async def test_data_set_and_get(self, memory_slot):
        new_data = {"new_key": "new_value"}
        await memory_slot.set_data(new_data)
        data = await memory_slot.data
        assert data == new_data, "Data after setting should match the new value."

    @pytest.mark.asyncio
    async def test_data_persistence(self, memory_slot):
        new_data = {"persistent_key": "persistent_value"}
        await memory_slot.set_data(new_data)

        # Re-initialize memory slot to simulate retrieval from storage
        new_slot = MemorySlot(
            "1", "test_slot", None, memory_slot.db_path, memory_slot._file_path)
        await new_slot.setup()
        data = await new_slot.data
        assert data == new_data, "Data should persist after re-initialization."

    @pytest.mark.asyncio
    async def test_memory_mapped_storage(self, memory_slot):
        large_data = {"key": "x" * int(memory_slot.DATA_SIZE_THRESHOLD + 1)}
        await memory_slot.set_data(large_data)

        assert memory_slot._use_mmap, "Memory-mapped storage should be used for large data."

        data = await memory_slot.data
        assert data == large_data, "Data should match the large data set using memory-mapped storage."

    @pytest.mark.asyncio
    async def test_metadata_update(self, memory_slot):
        old_modified_at = memory_slot._modified_at
        new_data = {"new_key": "new_value"}

        # Adding a small delay to ensure timestamp difference
        await asyncio.sleep(0.001)

        await memory_slot.set_data(new_data)

        print(f"Old modified_at: {old_modified_at}, New modified_at: {memory_slot._modified_at}")
        assert memory_slot._modified_at > old_modified_at, "Modified timestamp should update after setting new data."
        
    @pytest.mark.asyncio
    async def test_memory_slot_close(self, memory_slot):
        memory_slot.close()
        assert memory_slot._mmapped_file is None or memory_slot._mmapped_file.closed, "Memory-mapped file should be closed."
        assert memory_slot._file is None or memory_slot._file.closed, "File should be closed."

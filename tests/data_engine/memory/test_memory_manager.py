import pytest
import tempfile
from unittest.mock import MagicMock
from research_analytics_suite.data_engine.memory.MemoryManager import MemoryManager


@pytest.fixture(scope='class')
async def memory_manager():
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = f"{temp_dir}/memory_manager.db"
        manager = MemoryManager(db_path=db_path)
        manager._logger = MagicMock()
        manager._logger.info = MagicMock()
        manager._logger.debug = MagicMock()
        manager._logger.error = MagicMock()
        await manager.initialize()
        yield manager


@pytest.mark.asyncio
class TestMemoryManager:

    @pytest.fixture(autouse=True)
    async def setup_class(self, memory_manager):
        self.manager = memory_manager

    async def test_memory_manager_initialization(self):
        assert self.manager._initialized

    async def test_create_memory_slot(self):
        memory_slot = await self.manager.create_memory_slot("1", "test_slot", {"key": "value"}, "test_mmap.dat")
        assert memory_slot.memory_id == "1"
        assert memory_slot.name == "test_slot"
        assert memory_slot.data == {"key": "value"}

    async def test_get_memory_slot(self):
        await self.manager.create_memory_slot("1", "test_slot", {"key": "value"}, "test_mmap.dat")
        memory_slot = await self.manager.get_memory_slot("1")
        assert memory_slot.memory_id == "1"
        assert memory_slot.name == "test_slot"
        assert memory_slot.data == {"key": "value"}

    async def test_update_memory_slot(self):
        await self.manager.create_memory_slot("1", "test_slot", {"key": "value"}, "test_mmap.dat")
        await self.manager.update_memory_slot("1", {"new_key": "new_value"})
        memory_slot = await self.manager.get_memory_slot("1")
        assert memory_slot.data == {"new_key": "new_value"}

    async def test_delete_memory_slot(self):
        await self.manager.create_memory_slot("1", "test_slot", {"key": "value"}, "test_mmap.dat")
        await self.manager.delete_memory_slot("1")
        memory_slot = await self.manager.get_memory_slot("1")
        assert memory_slot is None

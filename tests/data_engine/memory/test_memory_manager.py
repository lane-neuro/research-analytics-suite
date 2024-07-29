import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from research_analytics_suite.data_engine.memory.MemoryManager import MemoryManager
from research_analytics_suite.data_engine.memory.MemorySlot import MemorySlot


@pytest.fixture(scope="function")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


class TestMemoryManager:
    @pytest.fixture(autouse=True)
    def setup(self):
        with patch('research_analytics_suite.utils.CustomLogger') as MockLogger:
            with patch('research_analytics_suite.utils.Config') as MockConfig:
                with patch('research_analytics_suite.data_engine.memory.DataCache') as MockDataCache:
                    MockLogger.return_value = MagicMock()
                    MockLogger.return_value.error = MagicMock()
                    MockLogger.return_value.debug = MagicMock()
                    MockLogger.return_value.info = MagicMock()
                    MockConfig.return_value = MagicMock()
                    MockDataCache.return_value = MagicMock()

                    self.memory_manager = MemoryManager()
                    self.memory_manager._logger = MockLogger()
                    self.memory_manager._config = MockConfig()
                    self.memory_manager._data_cache = MockDataCache()

                    # Explicitly set the return values for the DataCache methods
                    self.memory_manager._data_cache.get_key = MagicMock()
                    self.memory_manager._data_cache.set = MagicMock()
                    self.memory_manager._data_cache.delete = MagicMock()
                    self.memory_manager._data_cache.cache_values = MagicMock()
                    self.memory_manager._data_cache.close = AsyncMock()

    @pytest.mark.asyncio
    async def test_initialize(self):
        await self.memory_manager.initialize()
        assert self.memory_manager._initialized is True

    @pytest.mark.asyncio
    async def test_initialize_twice(self):
        await self.memory_manager.initialize()
        assert self.memory_manager._initialized is True

        # Initialize again and check that it doesn't reinitialize
        await self.memory_manager.initialize()
        assert self.memory_manager._initialized is True  # Should still be true without reinitialization

    @pytest.mark.asyncio
    async def test_update_slot_with_non_existing_id(self):
        memory_id = "nonexistingid"
        self.memory_manager._data_cache.get_key.return_value = None

        with patch.object(MemorySlot, 'setup', new_callable=AsyncMock):
            with patch.object(MemorySlot, 'set_data', new_callable=AsyncMock):
                updated_memory_id = await self.memory_manager.update_slot(memory_id=memory_id, data="new_value")

        self.memory_manager._data_cache.set.assert_called_once()
        assert updated_memory_id == memory_id

    @pytest.mark.asyncio
    async def test_delete_non_existing_slot(self):
        memory_id = "nonexistingid"
        self.memory_manager._data_cache.get_key.return_value = None

        # Should not raise any exception
        await self.memory_manager.delete_slot(memory_id=memory_id)

        # Verify delete was not called because the slot doesn't exist
        self.memory_manager._data_cache.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_slot_data_retrieval_error(self):
        memory_id = "nonexistingid"
        self.memory_manager._data_cache.get_key.return_value = None

        data = await self.memory_manager.slot_data(memory_id=memory_id)
        assert data is None

    @pytest.mark.asyncio
    async def test_validate_slots_with_empty_list(self):
        memory_ids = []
        valid_slots, invalid_slots = await self.memory_manager.validate_slots(memory_ids=memory_ids)

        assert valid_slots == []
        assert invalid_slots == []

    @pytest.mark.asyncio
    async def test_create_slot(self):
        memory_id = await self.memory_manager.create_slot(name="test_slot", data="value", db_path=":memory:")
        self.memory_manager._data_cache.set.assert_called_once()
        assert len(memory_id) == 8  # UUID truncated to 8 characters

    @pytest.mark.asyncio
    async def test_update_slot(self):
        memory_id = "12345678"
        self.memory_manager._data_cache.get_key.return_value = None

        with patch.object(MemorySlot, 'setup', new_callable=AsyncMock):
            with patch.object(MemorySlot, 'set_data', new_callable=AsyncMock):
                updated_memory_id = await self.memory_manager.update_slot(memory_id=memory_id, data="new_value")

        self.memory_manager._data_cache.set.assert_called_once()
        assert updated_memory_id == memory_id

    @pytest.mark.asyncio
    async def test_delete_slot(self):
        memory_id = "12345678"
        mock_slot = MagicMock(spec=MemorySlot)
        mock_slot.file_path = "test_mmap.dat"
        self.memory_manager._data_cache.get_key.return_value = mock_slot

        with patch('os.remove', MagicMock()) as mock_remove:
            await self.memory_manager.delete_slot(memory_id=memory_id)
            mock_remove.assert_called_once_with("test_mmap.dat")

        self.memory_manager._data_cache.delete.assert_called_once_with(key=memory_id)

    @pytest.mark.asyncio
    async def test_list_slots(self):
        memory_slot_mock_1 = MagicMock(spec=MemorySlot)
        memory_slot_mock_1.memory_id = "id_01"
        memory_slot_mock_1.name = "name1"
        memory_slot_mock_1.data = 100

        memory_slot_mock_2 = MagicMock(spec=MemorySlot)
        memory_slot_mock_2.memory_id = "id_02"
        memory_slot_mock_2.name = "name2"
        memory_slot_mock_2.data = "data2"
        expected_slots = [memory_slot_mock_1, memory_slot_mock_2]

        self.memory_manager._data_cache.cache_values.return_value = expected_slots

        slots = await self.memory_manager.list_slots()

        self.memory_manager._data_cache.cache_values.assert_called_once()
        assert slots == expected_slots

    @pytest.mark.asyncio
    async def test_slot_name(self):
        expected_name = "test_slot"
        memory_slot_mock = MagicMock(spec=MemorySlot)
        memory_slot_mock.name = expected_name

        self.memory_manager._data_cache.get_key.return_value = memory_slot_mock

        memory_id = "12345678"
        name = await self.memory_manager.slot_name(memory_id=memory_id)
        assert name == expected_name

    @pytest.mark.asyncio
    async def test_validate_slots(self):
        valid_slot_mock = MagicMock(spec=MemorySlot)
        valid_slot_mock.data = AsyncMock(return_value={"key": "value"})

        self.memory_manager.slot_data = AsyncMock(side_effect=[valid_slot_mock.data(), None])
        memory_ids = ["12345678", "87654321"]

        valid_slots, invalid_slots = await self.memory_manager.validate_slots(memory_ids=memory_ids)

        assert valid_slots == ["12345678"]
        assert invalid_slots == ["87654321"]

    @pytest.mark.asyncio
    async def test_cleanup(self):
        await self.memory_manager.cleanup()
        self.memory_manager._data_cache.close.assert_called_once()

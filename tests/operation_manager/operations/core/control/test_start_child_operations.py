import pytest
from unittest.mock import AsyncMock, MagicMock

from research_analytics_suite.operation_manager.operations.core.control.StartOperation import start_child_operations


class TestStartChildOperations:
    @pytest.fixture
    def setup_operation(self):
        self.mock_operation = MagicMock()
        yield self.mock_operation

    @pytest.mark.asyncio
    async def test_no_child_operations(self, setup_operation):
        self.mock_operation.inheritance = []
        self.mock_operation.parallel = False

        await start_child_operations(self.mock_operation)

        # No assertions needed as no operations should be started

    @pytest.mark.asyncio
    async def test_child_operations_in_parallel(self, setup_operation):
        child_operation_1 = MagicMock()
        child_operation_2 = MagicMock()
        child_operation_1.start_operation = AsyncMock()
        child_operation_2.start_operation = AsyncMock()

        self.mock_operation.inheritance = [child_operation_1, child_operation_2]
        self.mock_operation.parallel = True

        await start_child_operations(self.mock_operation)

        child_operation_1.start_operation.assert_awaited_once()
        child_operation_2.start_operation.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_child_operations_sequentially(self, setup_operation):
        child_operation_1 = MagicMock()
        child_operation_2 = MagicMock()
        child_operation_1.start_operation = AsyncMock()
        child_operation_2.start_operation = AsyncMock()

        self.mock_operation.inheritance = [child_operation_1, child_operation_2]
        self.mock_operation.parallel = False

        await start_child_operations(self.mock_operation)

        child_operation_1.start_operation.assert_awaited_once()
        child_operation_2.start_operation.assert_awaited_once()
        # Ensure the second start is awaited after the first
        assert child_operation_1.start_operation.await_count == 1
        assert child_operation_2.start_operation.await_count == 1

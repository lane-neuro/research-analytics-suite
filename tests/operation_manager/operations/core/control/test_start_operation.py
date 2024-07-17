import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock

from research_analytics_suite.operation_manager.operations.core.control.StartOperation import start_operation


class TestStartOperation:
    @pytest.fixture(autouse=True)
    def setup_operation(self):
        self.mock_operation = MagicMock()
        self.mock_operation.start = AsyncMock()
        self.mock_operation.handle_error = Mock()
        self.mock_operation.inheritance = []
        yield self.mock_operation

    @pytest.mark.asyncio
    async def test_start_operation_without_inheritance(self):
        self.mock_operation.inheritance = []
        self.mock_operation.status = ""

        await start_operation(self.mock_operation)

        assert self.mock_operation.status == "started"
        self.mock_operation.handle_error.assert_not_called()

    @pytest.mark.asyncio
    @patch('research_analytics_suite.operation_manager.operations.core.control.StartOperation.start_child_operations', new_callable=AsyncMock)
    async def test_start_operation_with_inheritance(self, mock_start_child_operations):
        self.mock_operation.inheritance = ["child_operation"]
        self.mock_operation.status = ""

        await start_operation(self.mock_operation)

        mock_start_child_operations.assert_awaited_once_with(self.mock_operation)

        assert self.mock_operation.status == "started"
        self.mock_operation.handle_error.assert_not_called()

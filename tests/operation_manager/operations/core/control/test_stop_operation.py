import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from research_analytics_suite.operation_manager.operations.core.control import stop_operation


@pytest.mark.asyncio
async def test_stop_operation_running_no_child_operations():
    operation = MagicMock()
    operation.status = "running"
    operation.inheritance = None
    operation.task = AsyncMock()
    operation.task.cancel = MagicMock()

    await stop_operation(operation)

    operation.task.cancel.assert_called_once()
    assert operation.status == "stopped"
    operation.add_log_entry.assert_called_with(f"[STOP] {operation.name}")


@pytest.mark.asyncio
async def test_stop_operation_running_with_child_operations():
    operation = MagicMock()
    operation.status = "running"
    operation.inheritance = [MagicMock()]
    operation.task = AsyncMock()
    operation.task.cancel = MagicMock()

    child_op = operation.inheritance[0]
    child_op.stop = AsyncMock()

    with patch('research_analytics_suite.operation_manager.operations.core.control.StopOperation.stop_child_operations',
               new=AsyncMock()) as mock_stop_children:
        await stop_operation(operation, child_operations=True)

        mock_stop_children.assert_awaited_once()
        operation.task.cancel.assert_called_once()
        assert operation.status == "stopped"
        operation.add_log_entry.assert_called_with(f"[STOP] {operation.name}")


@pytest.mark.asyncio
async def test_stop_operation_already_stopped():
    operation = MagicMock()
    operation.status = "stopped"

    await stop_operation(operation)

    operation.add_log_entry.assert_called_with(f"[STOP] {operation.name} - Already stopped")
    operation.task.cancel.assert_not_called()


@pytest.mark.asyncio
async def test_stop_operation_exception_handling():
    operation = MagicMock()
    operation.status = "running"
    operation.task = AsyncMock()
    operation.task.cancel = MagicMock(side_effect=Exception("Test error"))

    await stop_operation(operation)

    operation.task.cancel.assert_called_once()
    operation.handle_error.assert_called_once()
    operation.add_log_entry.assert_called_with(f"[STOP] {operation.name}")


@pytest.mark.asyncio
async def test_stop_child_operations():
    parent_operation = MagicMock()
    child_operation_1 = MagicMock()
    child_operation_2 = MagicMock()

    child_operation_1.stop = AsyncMock()
    child_operation_2.stop = AsyncMock()

    parent_operation.inheritance = [
        child_operation_1,
        child_operation_2
    ]

    from research_analytics_suite.operation_manager.operations.core.control.StopOperation import stop_child_operations
    await stop_child_operations(parent_operation)

    child_operation_1.stop.assert_awaited_once()
    child_operation_2.stop.assert_awaited_once()

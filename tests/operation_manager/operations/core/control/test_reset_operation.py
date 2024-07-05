import pytest
from unittest.mock import MagicMock, AsyncMock

from research_analytics_suite.operation_manager.operations.core.control import reset_operation


@pytest.mark.asyncio
async def test_reset_operation_running_no_child_operations():
    operation = MagicMock()
    operation.status = "running"
    operation.inheritance = None
    operation.stop = AsyncMock()
    operation.start = AsyncMock()

    await reset_operation(operation)

    operation.stop.assert_awaited_once()
    operation.start.assert_awaited_once()
    assert operation.progress == 0
    operation.add_log_entry.assert_called_with(f"[RESET] {operation.name}")


@pytest.mark.asyncio
async def test_reset_operation_paused_with_child_operations():
    operation = MagicMock()
    operation.status = "paused"
    operation.inheritance = {"child": MagicMock()}
    operation.stop = AsyncMock()
    operation.start = AsyncMock()
    operation.reset_child_operations = AsyncMock()

    await reset_operation(operation, child_operations=True)

    operation.reset_child_operations.assert_awaited_once()
    operation.stop.assert_awaited_once()
    operation.start.assert_awaited_once()
    assert operation.progress == 0
    operation.add_log_entry.assert_called_with(f"[RESET] {operation.name}")


@pytest.mark.asyncio
async def test_reset_operation_completed_no_child_operations():
    operation = MagicMock()
    operation.status = "completed"
    operation.inheritance = None
    operation.stop = AsyncMock()
    operation.start = AsyncMock()

    await reset_operation(operation)

    operation.stop.assert_awaited_once()
    operation.start.assert_awaited_once()
    assert operation.progress == 0
    operation.add_log_entry.assert_called_with(f"[RESET] {operation.name}")


@pytest.mark.asyncio
async def test_reset_operation_error_with_child_operations():
    operation = MagicMock()
    operation.status = "error"
    operation.inheritance = {"child": MagicMock()}
    operation.stop = AsyncMock()
    operation.start = AsyncMock()
    operation.reset_child_operations = AsyncMock()

    await reset_operation(operation, child_operations=True)

    operation.reset_child_operations.assert_awaited_once()
    operation.stop.assert_awaited_once()
    operation.start.assert_awaited_once()
    assert operation.progress == 0
    operation.add_log_entry.assert_called_with(f"[RESET] {operation.name}")


@pytest.mark.asyncio
async def test_reset_operation_already_reset():
    operation = MagicMock()
    operation.status = "reset"  # This status indicates the operation is already reset

    await reset_operation(operation)

    operation.add_log_entry.assert_called_with(f"[RESET] {operation.name} - Already reset")
    operation.stop.assert_not_called()
    operation.start.assert_not_called()


@pytest.mark.asyncio
async def test_reset_operation_exception_handling():
    operation = MagicMock()
    operation.status = "running"
    operation.stop = AsyncMock(side_effect=Exception("Test error"))
    operation.start = AsyncMock()

    await reset_operation(operation)

    operation.stop.assert_awaited_once()
    operation.start.assert_not_awaited()
    operation.handle_error.assert_called_once()
    operation.add_log_entry.assert_called_with(f"[RESET] {operation.name} - Error occurred during reset")

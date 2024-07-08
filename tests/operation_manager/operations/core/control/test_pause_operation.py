import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from research_analytics_suite.operation_manager.operations.core.control import pause_operation


@pytest.mark.asyncio
async def test_pause_operation_running_no_child_operations():
    operation = MagicMock()
    operation.status = "running"
    operation.inheritance = None
    operation.pause_event.clear = AsyncMock()

    await pause_operation(operation)

    operation.pause_event.clear.assert_awaited_once()
    assert operation.status == "paused"
    operation.add_log_entry.assert_called_with(f"[PAUSE] {operation.name}")


@pytest.mark.asyncio
async def test_pause_operation_running_with_child_operations():
    operation = MagicMock()
    operation.status = "running"
    operation.inheritance = {"child": MagicMock()}
    operation.pause_event.clear = AsyncMock()

    with patch('research_analytics_suite.operation_manager.operations.core.control.PauseOperation'
               '.pause_child_operations', new=AsyncMock()) as mock_pause_children:
        await pause_operation(operation, child_operations=True)

        mock_pause_children.assert_awaited_once()
        operation.pause_event.clear.assert_awaited_once()
        assert operation.status == "paused"
        operation.add_log_entry.assert_called_with(f"[PAUSE] {operation.name}")


@pytest.mark.asyncio
async def test_pause_operation_exception_handling():
    operation = MagicMock()
    operation.status = "running"
    operation.pause_event.clear = AsyncMock(side_effect=Exception("Test error"))

    await pause_operation(operation)

    operation.handle_error.assert_called()
    operation.add_log_entry.assert_called_with(f"[PAUSE] {operation.name}")


@pytest.mark.asyncio
async def test_pause_operation_already_paused():
    operation = MagicMock()
    operation.status = "paused"

    await pause_operation(operation)

    operation.add_log_entry.assert_called_with(f"[PAUSE] {operation.name} - Already paused")
    operation.pause_event.clear.assert_not_called()


@pytest.mark.asyncio
async def test_pause_operation_not_running():
    operation = MagicMock()
    operation.status = "completed"  # Any state other than "running"

    await pause_operation(operation)

    operation.add_log_entry.assert_called_with(f"[PAUSE] {operation.name} - Already paused")
    operation.pause_event.clear.assert_not_called()


@pytest.mark.asyncio
async def test_pause_operation_no_inheritance():
    operation = MagicMock()
    operation.status = "running"
    del operation.inheritance
    operation.pause_event = AsyncMock()

    await pause_operation(operation, child_operations=True)

    operation.pause_event.clear.assert_awaited_once()
    assert operation.status == "paused"
    operation.add_log_entry.assert_called_with(f"[PAUSE] {operation.name}")


@pytest.mark.asyncio
async def test_pause_operation_no_child_operations_flag():
    operation = MagicMock()
    operation.status = "running"
    operation.inheritance = {"child": MagicMock()}
    operation.pause_event.clear = AsyncMock()

    with patch('research_analytics_suite.operation_manager.operations.core.control.PauseOperation'
               '.pause_child_operations', new=AsyncMock()) as mock_pause_children:
        await pause_operation(operation, child_operations=False)

        mock_pause_children.assert_not_awaited()
        operation.pause_event.clear.assert_awaited_once()
        assert operation.status == "paused"
        operation.add_log_entry.assert_called_with(f"[PAUSE] {operation.name}")


@pytest.mark.asyncio
async def test_pause_operation_no_pause_event():
    operation = MagicMock()
    operation.status = "running"
    del operation.pause_event

    await pause_operation(operation)

    operation.handle_error.assert_called()
    operation.add_log_entry.assert_called_with(f"[PAUSE] {operation.name}")

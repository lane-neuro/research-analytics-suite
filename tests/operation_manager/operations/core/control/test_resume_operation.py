import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from research_analytics_suite.operation_manager.operations.core.control import resume_operation


@pytest.mark.asyncio
async def test_resume_operation_paused_no_child_operations():
    operation = MagicMock()
    operation.status = "paused"
    operation.inheritance = None
    operation.pause_event.set = AsyncMock()

    await resume_operation(operation)

    operation.pause_event.set.assert_awaited_once()
    assert operation.status == "running"
    operation.add_log_entry.assert_called_with(f"[RESUME] {operation.name}")


@pytest.mark.asyncio
async def test_resume_operation_paused_with_child_operations():
    operation = MagicMock()
    operation.status = "paused"
    operation.inheritance = {"child": MagicMock()}
    operation.pause_event.set = AsyncMock()

    child_op = operation.inheritance["child"]
    child_op.resume = AsyncMock()

    with patch('research_analytics_suite.operation_manager.operations.core.control.ResumeOperation'
               '.resume_child_operations',
               new=AsyncMock()) as mock_resume_children:
        await resume_operation(operation, child_operations=True)

        mock_resume_children.assert_awaited_once()
        operation.pause_event.set.assert_awaited_once()
        assert operation.status == "running"
        operation.add_log_entry.assert_called_with(f"[RESUME] {operation.name}")


@pytest.mark.asyncio
async def test_resume_operation_already_running():
    operation = MagicMock()
    operation.status = "running"

    await resume_operation(operation)

    operation.add_log_entry.assert_called_with(f"[RESUME] {operation.name} - Already running")
    operation.pause_event.set.assert_not_called()


@pytest.mark.asyncio
async def test_resume_operation_exception_handling():
    operation = MagicMock()
    operation.status = "paused"
    operation.pause_event.set = AsyncMock(side_effect=Exception("Test error"))

    await resume_operation(operation)

    operation.pause_event.set.assert_awaited_once()
    operation.handle_error.assert_called_once()
    operation.add_log_entry.assert_called_with(f"[RESUME] {operation.name}")


@pytest.mark.asyncio
async def test_resume_child_operations():
    parent_operation = MagicMock()
    child_operation_1 = MagicMock()
    child_operation_2 = MagicMock()

    child_operation_1.resume = AsyncMock()
    child_operation_2.resume = AsyncMock()

    parent_operation.inheritance = {
        "child1": child_operation_1,
        "child2": child_operation_2
    }

    from research_analytics_suite.operation_manager.operations.core.control.ResumeOperation import \
        resume_child_operations
    await resume_child_operations(parent_operation)

    child_operation_1.resume.assert_awaited_once()
    child_operation_2.resume.assert_awaited_once()


@pytest.mark.asyncio
async def test_resume_child_operations_inheritance_none():
    parent_operation = MagicMock()
    parent_operation.inheritance = None

    from research_analytics_suite.operation_manager.operations.core.control.ResumeOperation import \
        resume_child_operations
    await resume_child_operations(parent_operation)

    # Ensure no exceptions and nothing is called
    assert parent_operation.inheritance is None

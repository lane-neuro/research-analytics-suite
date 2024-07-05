import pytest
from unittest.mock import MagicMock, AsyncMock

from research_analytics_suite.operation_manager.operations.core.control import start_operation


class Operation:
    status = None
    inheritance = None
    parallel = True


@pytest.mark.asyncio
async def test_start_operation_with_child_operations():
    operation = MagicMock(spec=Operation)
    operation.inheritance = {"child1": MagicMock(spec=Operation), "child2": MagicMock(spec=Operation)}
    operation.parallel = True
    operation.start = AsyncMock()
    operation.handle_error = MagicMock()

    child1 = operation.inheritance["child1"]
    child1.start = AsyncMock()
    child2 = operation.inheritance["child2"]
    child2.start = AsyncMock()

    await start_operation(operation)

    child1.start.assert_awaited_once()
    child2.start.assert_awaited_once()
    assert operation.status == "started"


@pytest.mark.asyncio
async def test_start_operation_no_child_operations():
    operation = MagicMock(spec=Operation)
    operation.inheritance = None
    operation.start = AsyncMock()
    operation.handle_error = MagicMock()

    await start_operation(operation)

    operation.start.assert_awaited_once()
    assert operation.status == "started"


@pytest.mark.asyncio
async def test_start_operation_sequential_children():
    operation = MagicMock(spec=Operation)
    operation.inheritance = {"child1": MagicMock(spec=Operation), "child2": MagicMock(spec=Operation)}
    operation.parallel = False
    operation.start = AsyncMock()
    operation.handle_error = MagicMock()

    child1 = operation.inheritance["child1"]
    child1.start = AsyncMock()
    child2 = operation.inheritance["child2"]
    child2.start = AsyncMock()

    await start_operation(operation)

    child1.start.assert_awaited_once()
    child2.start.assert_awaited_once()
    assert operation.status == "started"


@pytest.mark.asyncio
async def test_start_operation_exception_handling():
    operation = MagicMock(spec=Operation)
    operation.inheritance = None
    operation.handle_error = MagicMock()

    operation.start = AsyncMock(side_effect=Exception("Test error"))

    await start_operation(operation)

    operation.start.assert_awaited_once()
    operation.handle_error.assert_called_once()


@pytest.mark.asyncio
async def test_start_child_operations_parallel():
    parent_operation = MagicMock(spec=Operation)
    parent_operation.parallel = True
    child_operation_1 = MagicMock(spec=Operation)
    child_operation_2 = MagicMock(spec=Operation)

    child_operation_1.start = AsyncMock()
    child_operation_2.start = AsyncMock()

    parent_operation.inheritance = {
        "child1": child_operation_1,
        "child2": child_operation_2
    }

    from research_analytics_suite.operation_manager.operations.core.control.StartOperation import start_child_operations
    await start_child_operations(parent_operation)

    child_operation_1.start.assert_awaited_once()
    child_operation_2.start.assert_awaited_once()


@pytest.mark.asyncio
async def test_start_child_operations_sequential():
    parent_operation = MagicMock(spec=Operation)
    parent_operation.parallel = False
    child_operation_1 = MagicMock(spec=Operation)
    child_operation_2 = MagicMock(spec=Operation)

    child_operation_1.start = AsyncMock()
    child_operation_2.start = AsyncMock()

    parent_operation.inheritance = {
        "child1": child_operation_1,
        "child2": child_operation_2
    }

    from research_analytics_suite.operation_manager.operations.core.control.StartOperation import start_child_operations
    await start_child_operations(parent_operation)

    child_operation_1.start.assert_awaited_once()
    child_operation_2.start.assert_awaited_once()

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from research_analytics_suite.operation_manager.operations.core.inheritance import (
    start_child_operations,
    pause_child_operations,
    resume_child_operations,
    stop_child_operations,
    reset_child_operations,
)


@pytest.mark.asyncio
async def test_start_child_operations():
    operation = MagicMock()
    child_operation = MagicMock()
    child_operation.start = AsyncMock()
    operation.inheritance = {"child_id": child_operation}

    await start_child_operations(operation)

    child_operation.start.assert_awaited_once()


@pytest.mark.asyncio
async def test_pause_child_operations():
    operation = MagicMock()
    child_operation = MagicMock()
    child_operation.pause = AsyncMock()
    operation.inheritance = {"child_id": child_operation}

    await pause_child_operations(operation)

    child_operation.pause.assert_awaited_once_with(True)


@pytest.mark.asyncio
async def test_resume_child_operations():
    operation = MagicMock()
    child_operation = MagicMock()
    child_operation.resume = AsyncMock()
    operation.inheritance = {"child_id": child_operation}

    await resume_child_operations(operation)

    child_operation.resume.assert_awaited_once()


@pytest.mark.asyncio
async def test_stop_child_operations():
    operation = MagicMock()
    child_operation = MagicMock()
    child_operation.stop = AsyncMock()
    operation.inheritance = {"child_id": child_operation}

    await stop_child_operations(operation)

    child_operation.stop.assert_awaited_once()


@pytest.mark.asyncio
async def test_reset_child_operations():
    operation = MagicMock()
    child_operation = MagicMock()
    child_operation.reset = AsyncMock()
    operation.inheritance = {"child_id": child_operation}

    await reset_child_operations(operation)

    child_operation.reset.assert_awaited_once()
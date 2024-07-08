# test_update_progress.py
import asyncio
import pytest


class MockOperation:
    def __init__(self):
        self.is_complete = False
        self.status = "running"
        self.progress = 0


@pytest.mark.skip(reason="Takes too long to run")
async def test_update_progress_increments_progress():
    operation = MockOperation()

    # Run the update_progress function in the background
    from research_analytics_suite.operation_manager.operations.core.progress import update_progress
    update_task = asyncio.create_task(update_progress(operation))

    # Let the progress update for a few seconds
    await asyncio.sleep(2)

    # Stop the operation
    operation.is_complete = True
    await update_task

    # Check that the progress was incremented correctly
    assert operation.progress >= 2


@pytest.mark.skip(reason="Takes too long to run")
async def test_update_progress_stops_when_complete():
    operation = MockOperation()

    # Run the update_progress function in the background
    from research_analytics_suite.operation_manager.operations.core.progress import update_progress
    update_task = asyncio.create_task(update_progress(operation))

    # Let the progress update for a short period
    await asyncio.sleep(1)

    # Stop the operation
    operation.is_complete = True
    await update_task

    # Check that the progress was incremented
    assert operation.progress >= 1

    # Check that progress stops updating after completion
    progress_after_complete = operation.progress
    await asyncio.sleep(2)
    assert operation.progress == progress_after_complete

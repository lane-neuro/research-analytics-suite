import pytest
import asyncio
from unittest.mock import MagicMock
from research_analytics_suite.operation_manager.task.TaskCounter import TaskCounter
from research_analytics_suite.utils.CustomLogger import CustomLogger


@pytest.fixture
def sequencer():
    """
    Fixture for creating a sequencer mock.
    """
    return MagicMock()


@pytest.fixture
def task_creator(sequencer):
    """
    Fixture for creating a TaskCreator instance with mocked dependencies.
    """
    from research_analytics_suite.operation_manager import TaskCreator
    tc = TaskCreator(sequencer)
    tc.task_counter = MagicMock(spec=TaskCounter)
    tc._logger = MagicMock(spec=CustomLogger)
    return tc


@pytest.mark.asyncio
async def test_create_task(task_creator):
    """
    Test creating and scheduling a new task.
    """
    async def dummy_coro():
        await asyncio.sleep(0.1)
        return "done"

    task_name = "TestTask"
    task_creator.task_counter.new_task.return_value = "[1]TestTask"

    task = task_creator.create_task(dummy_coro(), task_name)

    assert isinstance(task, asyncio.Task)
    assert task.get_name() == "[1]TestTask"
    assert task in task_creator.tasks
    task_creator.task_counter.new_task.assert_called_once_with(task_name)


class MockOperationType:
    pass


def test_task_exists(task_creator):
    """
    Test checking if a task of the specified operation type exists.
    """
    operation_type = MockOperationType

    # Simulate a running task of the specified type
    task = MagicMock(spec=MockOperationType)
    task.status = "running"
    task_creator.tasks.add(task)

    task_exists = task_creator.task_exists(operation_type)
    assert task_exists

    # Reset tasks and sequencer
    task_creator.tasks.clear()
    task_creator.sequencer.sequencer = []

    # Simulate a task in the sequencer
    operation_chain = MagicMock()
    operation_chain.head.operation = MagicMock(spec=MockOperationType)
    task_creator.sequencer.sequencer.append(operation_chain)

    task_exists = task_creator.task_exists(operation_type)
    assert task_exists


@pytest.mark.asyncio
async def test_cancel_task(task_creator):
    """
    Test cancelling a task by its name.
    """
    async def dummy_coro():
        await asyncio.sleep(0.1)

    task_name = "TestTask"
    task_creator.task_counter.new_task.return_value = "[1]TestTask"

    task = task_creator.create_task(dummy_coro(), task_name)

    # Ensure the task is created
    assert task in task_creator.tasks

    # Cancel the task
    result = task_creator.cancel_task("[1]TestTask")
    assert result is True
    assert task not in task_creator.tasks

    # Yield to the event loop to process the cancellation
    await asyncio.sleep(0)
    assert task.cancelled()

    # Try to cancel a non-existent task
    result = task_creator.cancel_task("[2]TestTask")
    assert result is False
    
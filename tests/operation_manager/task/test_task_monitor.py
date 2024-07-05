import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation
from research_analytics_suite.operation_manager.operations.system.ConsoleOperation import ConsoleOperation
from research_analytics_suite.utils.CustomLogger import CustomLogger


@pytest.fixture
def task_creator():
    """Fixture for creating a task creator mock."""
    return MagicMock()


@pytest.fixture
def sequencer():
    """Fixture for creating a sequencer mock."""
    return MagicMock()


@pytest.fixture
def task_monitor(task_creator, sequencer):
    """Fixture for creating a TaskMonitor instance with mocked dependencies."""
    from research_analytics_suite.operation_manager import TaskMonitor
    tm = TaskMonitor(task_creator, sequencer)
    tm._logger = MagicMock(spec=CustomLogger)
    return tm


@pytest.mark.asyncio
async def test_handle_tasks(task_monitor, task_creator, sequencer):
    """Test the handle_tasks method of TaskMonitor."""

    # Mock task
    task = MagicMock()
    task.get_name.return_value = "TestTask"
    task.done.return_value = True
    task_creator.tasks = {task}

    # Mock operation
    operation = MagicMock(spec=BaseOperation)
    operation.is_complete = True
    operation.is_loop = False
    operation.get_results_from_memory = AsyncMock(return_value="result")
    sequencer.find_operation_by_task.return_value = operation

    await task_monitor.handle_tasks()

    task_monitor._logger.debug.assert_any_call("handle_tasks: [INIT]")
    task_monitor._logger.debug.assert_any_call("handle_tasks: [CHECK] TestTask")
    task_monitor._logger.debug.assert_any_call("handle_tasks: [OP] TestTask")
    task_monitor._logger.debug.assert_any_call("handle_tasks: [DONE] TestTask")

    operation.add_log_entry.assert_called_once_with("handle_tasks: [OUTPUT] result")
    assert task not in task_creator.tasks
    sequencer.remove_operation_from_sequencer.assert_called_once_with(operation)


@pytest.mark.asyncio
async def test_handle_tasks_no_operation(task_monitor, task_creator, sequencer):
    """Test handle_tasks when no operation is found for a task."""

    task = MagicMock()
    task.get_name.return_value = "TestTask"
    task.done.return_value = True
    task_creator.tasks = {task}

    sequencer.find_operation_by_task.return_value = None

    await task_monitor.handle_tasks()

    task_monitor._logger.debug.assert_any_call("handle_tasks: [INIT]")
    task_monitor._logger.debug.assert_any_call("handle_tasks: [CHECK] TestTask")
    task_monitor._logger.error.assert_called_once()


@pytest.mark.asyncio
async def test_handle_tasks_exception(task_monitor, task_creator, sequencer):
    """Test handle_tasks when an exception occurs."""

    task = MagicMock()
    task.get_name.return_value = "TestTask"
    task.done.return_value = True
    task_creator.tasks = {task}

    operation = MagicMock(spec=BaseOperation)
    operation.is_complete = True
    operation.is_loop = False
    operation.get_results_from_memory = AsyncMock(side_effect=Exception("Test Exception"))
    sequencer.find_operation_by_task.return_value = operation

    await task_monitor.handle_tasks()

    task_monitor._logger.debug.assert_any_call("handle_tasks: [INIT]")
    task_monitor._logger.debug.assert_any_call("handle_tasks: [CHECK] TestTask")
    task_monitor._logger.debug.assert_any_call("handle_tasks: [OP] TestTask")
    task_monitor._logger.error.assert_called_once()


@pytest.mark.asyncio
async def test_handle_tasks_console_operation(task_monitor, task_creator, sequencer):
    """Test handle_tasks when the operation is a ConsoleOperation."""

    task = MagicMock()
    task.get_name.return_value = "TestTask"
    task.done.return_value = True
    task_creator.tasks = {task}

    operation = MagicMock(spec=ConsoleOperation)
    operation.is_complete = True
    operation.is_loop = False
    operation.get_results_from_memory = AsyncMock(return_value="result")
    sequencer.find_operation_by_task.return_value = operation

    await task_monitor.handle_tasks()

    task_monitor._logger.debug.assert_any_call("handle_tasks: [INIT]")
    task_monitor._logger.debug.assert_any_call("handle_tasks: [CHECK] TestTask")
    task_monitor._logger.debug.assert_any_call("handle_tasks: [OP] TestTask")
    task_monitor._logger.debug.assert_any_call("handle_tasks: [DONE] TestTask")

    assert task not in task_creator.tasks
    sequencer.remove_operation_from_sequencer.assert_called_once_with(operation)
    assert task_monitor.op_control.console_operation_in_progress is False


def test_get_task_statuses(task_monitor, task_creator):
    """Test the get_task_statuses method of TaskMonitor."""

    # Mock tasks
    task1 = MagicMock()
    task1.get_name.return_value = "Task1"
    task1.done.return_value = False

    task2 = MagicMock()
    task2.get_name.return_value = "Task2"
    task2.done.return_value = True

    task_creator.tasks = {task1, task2}

    statuses = task_monitor.get_task_statuses()
    assert statuses == {
        "Task1": "running",
        "Task2": "done"
    }


def test_pause_all_tasks(task_monitor, task_creator):
    """Test the pause_all_tasks method of TaskMonitor."""

    # Mock tasks
    task1 = MagicMock()
    task1.get_name.return_value = "Task1"
    task1.done.return_value = False

    task2 = MagicMock()
    task2.get_name.return_value = "Task2"
    task2.done.return_value = False

    task3 = MagicMock()
    task3.get_name.return_value = "Task3"
    task3.done.return_value = True

    task_creator.tasks = {task1, task2, task3}

    task_monitor.pause_all_tasks()

    task1.cancel.assert_called_once()
    task2.cancel.assert_called_once()
    task3.cancel.assert_not_called()

    task_monitor._logger.debug.assert_any_call("pause_all_tasks: [PAUSE] Task1")
    task_monitor._logger.debug.assert_any_call("pause_all_tasks: [PAUSE] Task2")


@pytest.mark.asyncio
async def test_resume_all_tasks(task_monitor, task_creator):
    """Test the resume_all_tasks method of TaskMonitor."""

    async def dummy_coro():
        await asyncio.sleep(0.1)

    # Mock tasks
    task1 = MagicMock()
    task1.get_name.return_value = "Task1"
    task1.done.return_value = False
    task1.get_coro.return_value = await dummy_coro()

    task2 = MagicMock()
    task2.get_name.return_value = "Task2"
    task2.done.return_value = False
    task2.get_coro.return_value = await dummy_coro()

    task_creator.tasks = {task1, task2}

    task_monitor.pause_all_tasks()

    # Ensure tasks are paused
    assert "Task1" in task_monitor.paused_tasks
    assert "Task2" in task_monitor.paused_tasks

    with patch("asyncio.create_task") as mock_create_task:
        new_task1 = MagicMock()
        new_task2 = MagicMock()
        mock_create_task.side_effect = [new_task1, new_task2]

        task_monitor.resume_all_tasks()

        mock_create_task.assert_any_call(task1.get_coro(), name="Task1")
        mock_create_task.assert_any_call(task2.get_coro(), name="Task2")

        assert new_task1 in task_creator.tasks
        assert new_task2 in task_creator.tasks

        task_monitor._logger.debug.assert_any_call("resume_all_tasks: [RESUME] Task1")
        task_monitor._logger.debug.assert_any_call("resume_all_tasks: [RESUME] Task2")

    # Ensure paused tasks list is cleared
    assert len(task_monitor.paused_tasks) == 0

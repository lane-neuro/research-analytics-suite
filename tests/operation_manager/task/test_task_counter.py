import pytest
from unittest.mock import MagicMock


@pytest.fixture
def task_counter():
    """
    Fixture for creating a TaskCounter instance with a mocked logger.
    """
    from research_analytics_suite.operation_manager import TaskCounter
    tc = TaskCounter()
    tc._logger = MagicMock()
    return tc


def test_initial_counter(task_counter):
    """
    Test that the initial counter is set to zero.
    """
    assert task_counter.counter == 0


def test_new_task(task_counter):
    """
    Test creating a new task and check if the counter increments.
    """
    task_name = "TestTask"
    new_task_name = task_counter.new_task(task_name)
    assert task_counter.counter == 1
    assert new_task_name == "[1]TestTask"
    task_counter._logger.debug.assert_called_once_with(f"TaskCounter.new_task: [NEW] [1]{task_name}")


def test_multiple_new_tasks(task_counter):
    """
    Test creating multiple new tasks and check if the counter increments correctly.
    """
    task_name1 = "TestTask1"
    task_name2 = "TestTask2"

    new_task_name1 = task_counter.new_task(task_name1)
    new_task_name2 = task_counter.new_task(task_name2)

    assert task_counter.counter == 2
    assert new_task_name1 == "[1]TestTask1"
    assert new_task_name2 == "[2]TestTask2"
    assert task_counter._logger.debug.call_count == 2
    task_counter._logger.debug.assert_any_call(f"TaskCounter.new_task: [NEW] [1]{task_name1}")
    task_counter._logger.debug.assert_any_call(f"TaskCounter.new_task: [NEW] [2]{task_name2}")


def test_logger_called(task_counter):
    """
    Test that the logger is called correctly.
    """
    task_name = "TestTask"
    task_counter.new_task(task_name)
    task_counter._logger.debug.assert_called_once_with(f"TaskCounter.new_task: [NEW] [1]{task_name}")


def test_empty_task_name(task_counter):
    """
    Test that a ValueError is raised when creating a task with an empty name.
    """
    with pytest.raises(ValueError, match="Task name cannot be empty."):
        task_counter.new_task("")


if __name__ == "__main__":
    pytest.main()

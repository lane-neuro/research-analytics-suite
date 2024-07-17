import pytest
from unittest.mock import MagicMock
from research_analytics_suite.operation_manager.task.TaskCounter import TaskCounter


class TestTaskCounter:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_logger = MagicMock()
        self.task_counter = TaskCounter()
        self.task_counter._logger = self.mock_logger
        self.mock_logger.debug = MagicMock()
        self.mock_logger.error = MagicMock()

    def test_initialization(self):
        assert self.task_counter.counter == 0

    def test_new_task(self):
        task_name = "test_task"
        new_task_name = self.task_counter.new_task(task_name)

        assert new_task_name == "[1]test_task"
        assert self.task_counter.counter == 1
        self.mock_logger.debug.assert_called_with("TaskCounter.new_task: [NEW] [1]test_task")

    def test_new_task_with_empty_name(self):
        with pytest.raises(ValueError, match="Task name cannot be empty."):
            self.task_counter.new_task("")

        assert self.task_counter.counter == 0

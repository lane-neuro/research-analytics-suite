import pytest
import asyncio
from unittest.mock import MagicMock

from research_analytics_suite.operation_manager.task.TaskCreator import TaskCreator


class TestTaskCreator:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_sequencer = MagicMock()
        self.mock_task_counter = MagicMock()
        self.mock_logger = MagicMock()

        self.task_creator = TaskCreator(self.mock_sequencer)
        self.task_creator.task_counter = self.mock_task_counter
        self.task_creator._logger = self.mock_logger
        self.task_creator._logger.debug = MagicMock()
        self.task_creator._logger.info = MagicMock()

    @pytest.mark.asyncio
    async def test_task_exists(self):
        mock_task = asyncio.create_task(asyncio.sleep(1), name="[123]test_task")
        self.task_creator.tasks.add(mock_task)
        assert self.task_creator.task_exists("test_task") is True

    @pytest.mark.asyncio
    async def test_create_task(self):
        async def sample_coro():
            await asyncio.sleep(1)
            return "done"

        task_name = "test_task"
        self.mock_task_counter.new_task.return_value = task_name
        task = self.task_creator.create_task(sample_coro(), task_name)
        await asyncio.sleep(0.1)  # Let the event loop run a bit

        assert task in self.task_creator.tasks
        assert task.get_name() == task_name

    @pytest.mark.asyncio
    async def test_cancel_task(self):
        async def sample_coro():
            await asyncio.sleep(1)
            return "done"

        task_name = "[72]task_to_cancel"
        self.mock_task_counter.new_task.return_value = task_name
        task = self.task_creator.create_task(sample_coro(), task_name)
        await asyncio.sleep(0.1)  # Let the event loop run a bit

        assert self.task_creator.cancel_task('task_to_cancel') is True
        assert task not in self.task_creator.tasks

    def test_cancel_task_not_found(self):
        assert self.task_creator.cancel_task("non_existent_task") is False

    @pytest.mark.asyncio
    async def test_create_task_with_duplicate_name(self):
        async def sample_coro():
            await asyncio.sleep(1)
            return "done"

        task_name = "duplicate_task"
        self.mock_task_counter.new_task.side_effect = [task_name, f"{task_name}_1"]
        task1 = self.task_creator.create_task(sample_coro(), task_name)
        task2 = self.task_creator.create_task(sample_coro(), task_name)
        await asyncio.sleep(0.1)  # Let the event loop run a bit

        assert task1 in self.task_creator.tasks
        assert task2 in self.task_creator.tasks
        assert task1.get_name() == task_name
        assert task2.get_name() == f"{task_name}_1"

    @pytest.mark.asyncio
    async def test_task_completion_removes_from_set(self):
        async def sample_coro():
            await asyncio.sleep(0.1)
            return "done"

        task_name = "[21]completion_task"
        self.mock_task_counter.new_task.return_value = task_name
        task = self.task_creator.create_task(sample_coro(), task_name)
        await task
        await asyncio.sleep(0.1)  # Allow event loop to process task completion

        assert {task} not in self.task_creator.tasks

    @pytest.mark.asyncio
    async def test_logging_on_task_creation(self):
        async def sample_coro():
            await asyncio.sleep(1)
            return "done"

        task_name = "[52]logging_task"
        self.mock_task_counter.new_task.return_value = task_name
        self.task_creator.create_task(sample_coro(), task_name)
        await asyncio.sleep(0.1)  # Let the event loop run a bit

        self.task_creator._logger.debug.assert_called_with(f"Task {task_name} created.")

    @pytest.mark.asyncio
    async def test_logging_on_task_cancellation(self):
        async def sample_coro():
            await asyncio.sleep(1)
            return "done"

        task_name = "[51]logging_cancel_task"
        self.mock_task_counter.new_task.return_value = task_name
        task = self.task_creator.create_task(sample_coro(), task_name)
        await asyncio.sleep(0.1)  # Let the event loop run a bit

        self.task_creator.cancel_task('logging_cancel_task')
        self.task_creator._logger.info.assert_called_with(f"Task logging_cancel_task cancelled.")

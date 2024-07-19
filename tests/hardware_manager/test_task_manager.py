import pytest
from unittest import mock
import multiprocessing

from research_analytics_suite.hardware_manager.TaskManager import TaskManager


class TestTaskManager:
    @pytest.fixture
    def logger(self):
        with mock.patch('research_analytics_suite.utils.CustomLogger') as logger:
            yield logger

    @pytest.fixture
    def task_manager(self, logger):
        return TaskManager(logger)

    def test_initialization(self, task_manager, logger):
        assert task_manager.logger == logger

    def test_manage_tasks(self, task_manager, logger):
        hardware_info = {
            'cpu': {'logical_cores': 4}
        }
        task_results = [1000000000, 2000000000, 3000000000, 4000000000]

        with mock.patch('multiprocessing.Pool') as mock_pool:
            mock_pool.return_value.__enter__.return_value.map.return_value = task_results
            task_manager.manage_tasks(hardware_info)
            logger.info.assert_any_call("Managing tasks for hardware...")
            logger.info.assert_any_call(f"Task results: {task_results}")

            # Verifying that each result is logged
            for i, result in enumerate(task_results):
                logger.info.assert_any_call(f"Task result from core {i}: {result}")

    def test_cpu_bound_task(self, task_manager, logger):
        result = task_manager.cpu_bound_task(0)
        assert result == sum(i * i for i in range(1000000))
        logger.info.assert_called_with("Running task on CPU core 0")

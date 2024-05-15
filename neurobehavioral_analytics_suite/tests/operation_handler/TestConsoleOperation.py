import unittest
from unittest.mock import Mock, patch
from neurobehavioral_analytics_suite.operation_handler.ConsoleOperation import ConsoleOperation
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler


class TestConsoleOperation(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.error_handler = ErrorHandler()
        self.operation_handler = Mock()
        self.logger = Mock()
        self.local_vars = {}
        self.console_operation = ConsoleOperation(self.error_handler, self.operation_handler, self.logger,
                                                  self.local_vars)

    @patch('aioconsole.ainput', return_value="exit")
    async def test_execute_exits_on_exit_command(self, mock_ainput):
        await self.console_operation.execute()
        self.assertEqual(self.console_operation.status, "stopped")

    @patch('aioconsole.ainput', return_value="test_input")
    async def test_execute_processes_non_empty_input(self, mock_ainput):
        await self.console_operation.execute()
        self.operation_handler.process_user_input.assert_called_once_with("test_input")

    async def test_start_changes_status_to_started(self):
        await self.console_operation.start()
        self.assertEqual(self.console_operation.status, "started")

    async def test_stop_cancels_task_if_exists(self):
        self.console_operation.task = Mock()
        await self.console_operation.stop()
        self.console_operation.task.cancel.assert_called_once()

    async def test_stop_does_not_cancel_task_if_not_exists(self):
        self.console_operation.task = None
        await self.console_operation.stop()
        self.assertIsNone(self.console_operation.task)

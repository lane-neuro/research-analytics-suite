import unittest
from unittest.mock import AsyncMock, patch
from neurobehavioral_analytics_suite.operation_handler.CustomOperation import CustomOperation
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler


class TestCustomOperation(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.error_handler = ErrorHandler()
        self.func = AsyncMock()
        self.local_vars = {}
        self.custom_operation = CustomOperation(self.error_handler, self.func, self.local_vars)

    async def test_operation_starts_and_updates_status(self):
        await self.custom_operation.start()
        self.assertEqual(self.custom_operation.status, "started")

    async def test_operation_stops_and_updates_status(self):
        await self.custom_operation.stop()
        self.assertEqual(self.custom_operation.status, "stopped")

    async def test_operation_pauses_and_updates_status(self):
        await self.custom_operation.pause()
        self.assertEqual(self.custom_operation.status, "paused")

    async def test_operation_resumes_and_updates_status(self):
        await self.custom_operation.resume()
        self.assertEqual(self.custom_operation.status, "running")

    async def test_operation_resets_and_updates_status_after_start(self):
        await self.custom_operation.start()
        await self.custom_operation.reset()
        self.assertEqual(self.custom_operation.status, "started")

    @patch('neurobehavioral_analytics_suite.operation_handler.CustomOperation.CustomOperation.execute',
           new_callable=AsyncMock)
    async def operation_executes_func_and_updates_result(self, mock_exec):
        await self.custom_operation.execute()
        mock_exec.assert_called_once()

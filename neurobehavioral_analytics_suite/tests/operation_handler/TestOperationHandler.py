import unittest
from unittest.mock import Mock, patch, AsyncMock

from neurobehavioral_analytics_suite.operation_handler.Operation import Operation
from neurobehavioral_analytics_suite.operation_handler.OperationHandler import OperationHandler
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler


class TestOperationHandler(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        with patch.object(OperationHandler, 'exec_loop', new_callable=AsyncMock):
            self.error_handler = ErrorHandler()
            self.operation_handler = OperationHandler()

    async def test_operation_handler_starts_operations(self):
        operation = Mock(spec=Operation)
        operation.name = "test_operation"
        operation.status = "idle"
        await self.operation_handler.queue.add_operation(operation)
        await self.operation_handler.start_operations()
        self.assertEqual(operation.status, "started")

    async def test_operation_handler_executes_operation(self):
        operation = Mock(spec=Operation)
        operation.name = "test_operation"
        operation.status = "started"
        await self.operation_handler.queue.add_operation(operation)
        await self.operation_handler.execute_operation(operation)
        self.assertEqual(operation.status, "completed")

    async def test_operation_handler_processes_user_input(self):
        with patch('builtins.input', return_value='stop'):
            response = await self.operation_handler.process_user_input('stop')
        self.assertEqual(response, "OperationHandler.process_user_input: Stopping all operations...")

    async def test_operation_handler_stops_all_operations(self):
        operation1 = Mock(spec=Operation)
        operation1.name = "test_operation1"
        operation1.status = "running"
        operation2 = Mock(spec=Operation)
        operation2.name = "test_operation2"
        operation2.status = "running"
        await self.operation_handler.queue.add_operation(operation1)
        await self.operation_handler.queue.add_operation(operation2)
        await self.operation_handler.stop_all_operations()
        self.assertEqual(operation1.status, "stopped")
        self.assertEqual(operation2.status, "stopped")

    async def test_operation_handler_gets_operation_status(self):
        operation = Mock(spec=Operation)
        operation.name = "test_operation"
        operation.status = "running"
        await self.operation_handler.queue.add_operation(operation)
        status = self.operation_handler.get_operation_status(operation)
        self.assertEqual(status, "running")

    async def test_operation_handler_gets_all_operations_status(self):
        operation1 = Mock(spec=Operation)
        operation1.name = "test_operation1"
        operation1.status = "running"
        operation2 = Mock(spec=Operation)
        operation2.name = "test_operation2"
        operation2.status = "idle"
        await self.operation_handler.queue.add_operation(operation1)
        await self.operation_handler.queue.add_operation(operation2)
        statuses = self.operation_handler.get_all_operations_status()
        self.assertEqual(statuses, {operation1: "running", operation2: "idle"})

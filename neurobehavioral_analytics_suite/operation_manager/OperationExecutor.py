"""
Module description.

Longer description.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import asyncio

from neurobehavioral_analytics_suite.operation_manager.OperationChain import OperationChain
from neurobehavioral_analytics_suite.operation_manager.operation.persistent.ConsoleOperation import ConsoleOperation


class OperationExecutor:
    def __init__(self, operation_control, queue, task_manager, logger, error_handler):
        self.op_control = operation_control
        self.queue = queue
        self.task_manager = task_manager
        self.logger = logger
        self.error_handler = error_handler

    async def execute_operation(self, operation) -> asyncio.Task:
        try:
            if operation.status == "started":
                self.logger.info(f"execute_operation: [RUN] {operation.task.get_name()}")
                await operation.execute()
                return operation.task
        except Exception as e:
            self.error_handler.handle_error(e, self)

    async def execute_all(self) -> None:
        """
        Executes all Operation instances in the queue.

        This method executes the operations asynchronously. It waits for all operations tocomplete before returning.

        Raises:
            Exception: If an exception occurs during the execution of an operation, it is caught and handled by the
            ErrorHandler instance.
        """
        self.logger.debug("OperationControl: Queue Size: " + str(self.queue.size()))

        # Create a copy of the queue for iteration
        queue_copy = set(self.queue.queue)

        for operation_chain in queue_copy:
            top_operations = set()
            if isinstance(operation_chain, OperationChain):
                current_node = operation_chain.head
                if current_node is not None:
                    top_operations.add(current_node.operation)
            else:
                top_operations.add(operation_chain.operation)

            for operation in top_operations:
                if not operation.task or operation.task.done():
                    if isinstance(operation, ConsoleOperation) and not self.op_control.console_operation_in_progress:
                        continue
                    self.logger.debug(f"execute_all: [OP] {operation.name} - {operation.status} - {operation.task}")

                    if not operation.task:
                        operation.task = await self.task_manager.create_task(self.execute_operation(operation),
                                                                       name=operation.name)
                    if isinstance(operation, ConsoleOperation):
                        self.op_control.console_operation_in_progress = True

"""
OperationLifecycleManager Module.

This module defines the OperationLifecycleManager class responsible for managing the overall lifecycle of operations
within the Neurobehavioral Analytics Suite. It handles starting, stopping, pausing, and resuming operations.

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
from neurobehavioral_analytics_suite.operation_manager.OperationExecutor import OperationExecutor
from neurobehavioral_analytics_suite.operation_manager.OperationQueue import OperationQueue
from neurobehavioral_analytics_suite.operation_manager.task.TaskMonitor import TaskMonitor
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler
from neurobehavioral_analytics_suite.utils.CustomLogger import CustomLogger


class OperationLifecycleManager:
    """Manages the lifecycle of operations."""

    def __init__(self, queue: OperationQueue, operation_manager, executor: OperationExecutor,
                 persistent_op_checker, task_monitor: TaskMonitor, logger: CustomLogger, error_handler: ErrorHandler):
        """
        Initializes the OperationLifecycleManager with the given parameters.

        Args:
            queue: The operations queue.
            operation_manager: The operations manager.
            executor: The operations operation_executor.
            logger: CustomLogger for logging lifecycle-related information.
            error_handler: Handler for managing errors.
        """
        self.queue = queue
        self.operation_manager = operation_manager
        self.operation_executor = executor
        self.persistent_operation_checker = persistent_op_checker
        self.task_monitor = task_monitor
        self.logger = logger
        self.error_handler = error_handler

    async def start_all_operations(self):
        """Starts all operations in the queue."""
        for operation_chain in self.queue.queue:
            if isinstance(operation_chain, OperationChain):
                current_node = operation_chain.head
                while current_node is not None:
                    operation = current_node.operation
                    if operation.status == "idle":
                        operation.init_operation()
                        await operation.start()
                    current_node = current_node.next_node
            else:
                operation = operation_chain.operation
                if operation.status == "idle":
                    operation.init_operation()
                    await operation.start()

    async def stop_all_operations(self):
        """Stops all operations in the queue."""
        for operation_node in self.queue.queue:
            if isinstance(operation_node, OperationChain):
                current_node = operation_node.head
                while current_node is not None:
                    await self.operation_manager.stop_operation(current_node.operation)
                    current_node = current_node.next_node
            else:
                await self.operation_manager.stop_operation(operation_node)

    async def resume_all_operations(self):
        """Resumes all paused operations in the queue."""
        for operation_list in self.queue.queue:
            operation = self.queue.get_head_operation_from_chain(operation_list)
            await self.operation_manager.resume_operation(operation)

    async def pause_all_operations(self):
        """Pauses all operations in the queue."""
        for operation_list in self.queue.queue:
            operation = self.queue.get_head_operation_from_chain(operation_list)
            await self.operation_manager.pause_operation(operation)

    async def exec_loop(self):
        """Executes the main loop of the operations manager."""
        tasks = [self.persistent_operation_checker.check_persistent_operations(),
                 self.start_all_operations(),
                 self.operation_executor.execute_ready_operations(),
                 self.task_monitor.handle_tasks()]

        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.error_handler.handle_error(e, self)
            self.logger.error(f"OperationLifecycleManager.exec_loop: Exception occurred: {e}")

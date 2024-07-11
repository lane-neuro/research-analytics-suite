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

from research_analytics_suite.commands import command, register_commands
from research_analytics_suite.operation_manager.chains.OperationChain import OperationChain
from research_analytics_suite.operation_manager.execution.OperationExecutor import OperationExecutor
from research_analytics_suite.operation_manager.management.OperationSequencer import OperationSequencer
from research_analytics_suite.operation_manager.task.TaskMonitor import TaskMonitor
from research_analytics_suite.utils.CustomLogger import CustomLogger


@register_commands
class OperationLifecycleManager:
    """Manages the lifecycle of operations."""

    def __init__(self, sequencer: OperationSequencer, operation_manager, executor: OperationExecutor,
                 system_op_checker, task_monitor: TaskMonitor):
        """
        Initializes the OperationLifecycleManager with the given parameters.

        Args:
            sequencer: The operations sequencer.
            operation_manager: The operations manager.
            executor: The operations operation_executor.
        """
        self.sequencer = sequencer
        self.operation_manager = operation_manager
        self.operation_executor = executor
        self.system_operation_checker = system_op_checker
        self.task_monitor = task_monitor
        self._logger = CustomLogger()

    async def start_all_operations(self):
        """Starts all operations in the sequencer."""
        for operation_chain in self.sequencer.sequencer:
            if isinstance(operation_chain, OperationChain):
                current_node = operation_chain.head
                while current_node is not None:
                    operation = current_node.operation
                    if operation.status == "idle":
                        await operation.initialize_operation()
                        await operation.start()
                    current_node = current_node.next_node
            else:
                operation = operation_chain.operation
                if operation.status == "idle":
                    await operation.initialize_operation()
                    await operation.start()

    @command
    async def stop_all_operations(self):
        """Stops all operations in the sequencer."""
        for operation_node in self.sequencer.sequencer:
            if isinstance(operation_node, OperationChain):
                current_node = operation_node.head
                while current_node is not None:
                    await self.operation_manager.stop_operation(current_node.operation)
                    current_node = current_node.next_node
            else:
                await self.operation_manager.stop_operation(operation_node)

    async def resume_all_operations(self):
        """Resumes all paused operations in the sequencer."""
        for operation_list in self.sequencer.sequencer:
            operation = self.sequencer.get_head_operation_from_chain(operation_list)
            await self.operation_manager.resume_operation(operation)

    async def pause_all_operations(self):
        """Pauses all operations in the sequencer."""
        for operation_list in self.sequencer.sequencer:
            operation = self.sequencer.get_head_operation_from_chain(operation_list)
            await self.operation_manager.pause_operation(operation)

    async def exec_loop(self):
        """Executes the main loop of the operations manager."""
        tasks = [self.system_operation_checker.check_system_operations(),
                 self.start_all_operations(),
                 self.operation_executor.execute_ready_operations(),
                 self.task_monitor.handle_tasks()]

        try:
            await asyncio.gather(*tasks)
        except Exception as e:  # Catch all exceptions, the main loop has critically failed and the suite must exit
            self._logger.error(e, self.__class__.__name__)
            raise e

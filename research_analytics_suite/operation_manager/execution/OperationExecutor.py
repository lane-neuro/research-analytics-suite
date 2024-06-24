"""
OperationExecutor Module.

This module defines the OperationExecutor class, which is responsible for executing operations within the
research analytics suite. It handles the execution of ready operations in the sequencer and manages their status
and logging.

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

from research_analytics_suite.operation_manager.chains.OperationChain import OperationChain
from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation
from research_analytics_suite.operation_manager.operations.persistent.ConsoleOperation import ConsoleOperation
from research_analytics_suite.utils.CustomLogger import CustomLogger


class OperationExecutor:
    """
    A class to execute operations within the research analytics suite.

    This class manages the execution of ready operations in the sequencer, ensuring that they are run and their statuses
    are updated accordingly.
    """

    def __init__(self, sequencer, task_creator):
        """
        Initializes the OperationExecutor with the necessary components.

        Args:
            sequencer: Sequencer holding operations to be executed.
            task_creator: Task creator for generating asyncio tasks.
        """
        from research_analytics_suite.operation_manager.control.OperationControl import OperationControl
        self.op_control = OperationControl()

        self.sequencer = sequencer
        self.task_creator = task_creator
        self._logger = CustomLogger()

    async def execute_operation(self, operation: 'BaseOperation') -> asyncio.Task:
        """
        Executes a single operation.

        Args:
            operation (BaseOperation): The operation to execute.

        Returns:
            asyncio.Task: The asyncio task for the operation execution.
        """
        try:
            if operation.status == "started":
                await operation.execute()
                return operation.task
        except Exception as e:
            self._logger.error(e, self)

    async def execute_ready_operations(self) -> None:
        """
        Executes ready operations in the sequencer.

        This method iterates over the operations in the sequencer, checks their readiness, and executes them asynchronously.
        It waits for all operations to complete before returning.

        Raises:
            Exception: If an exception occurs during the execution of an operation, it is caught and handled by the
            ErrorHandler instance.
        """
        self._logger.debug("OperationControl: Sequencer Size: " + str(self.sequencer.size()))

        # Create a copy of the sequencer for iteration
        sequencer_copy = set(self.sequencer.sequencer)

        for operation_chain in sequencer_copy:
            chain_operations = set()
            if isinstance(operation_chain, OperationChain):
                for node in operation_chain:
                    chain_operations.add(node.operation)

            for operation in chain_operations:
                if not operation.task or operation.task.done():
                    if isinstance(operation, ConsoleOperation) and not self.op_control.console_operation_in_progress:
                        continue
                    self._logger.debug(f"execute_all: [OP] {operation.name} - {operation.status} - {operation.task}")

                    if not operation.task and operation.is_ready is True:
                        try:
                            operation.task = self.task_creator.create_task(
                                self.execute_operation(operation),
                                name=operation.name
                            )
                            operation.add_log_entry(f"[TASK] {operation.name}")
                        except Exception as e:
                            self._logger.error(e, self)
                    if isinstance(operation, ConsoleOperation):
                        self.op_control.console_operation_in_progress = True

"""
OperationManager Module.

This module defines the OperationManager class, which manages the creation, queuing, and control of operations within
the research analytics suite. It provides methods to add, resume, pause, and stop operations.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from research_analytics_suite.operation_manager.operations.ABCOperation import ABCOperation
from research_analytics_suite.utils.CustomLogger import CustomLogger


class OperationManager:
    """
    A class to manage operations within the research analytics suite.

    This class provides methods to add operations to the queue, and to resume, pause, and stop operations.
    """

    def __init__(self, queue, task_creator):
        """
        Initializes the OperationManager with the necessary components.

        Args:
            queue: Queue holding operations to be managed.
            task_creator: Task creator for generating asyncio tasks.
        """
        from research_analytics_suite.operation_manager.OperationControl import OperationControl
        self.op_control = OperationControl()

        self.queue = queue
        self.task_creator = task_creator
        self._logger = CustomLogger()

    async def add_operation(self, operation_type, *args, **kwargs) -> ABCOperation:
        """
        Creates a new Operation and adds it to the queue.

        Args:
            operation_type: The type of operation to be created.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Operation: The created operation.
        """
        try:
            operation = operation_type(*args, **kwargs)
            await self.queue.add_operation_to_queue(operation)
            operation.add_log_entry(f"[QUEUE] {operation.name}")

            if operation.parent_operation is not None:
                await operation.parent_operation.add_child_operation(operation)

            return operation
        except Exception as e:
            self._logger.error(e, operation_type)

    async def add_operation_if_not_exists(self, operation_type, *args, **kwargs) -> ABCOperation:
        """
        Adds an operation to the queue if it does not already exist.

        Args:
            operation_type: The type of operation to be created.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        if not self.task_creator.task_exists(operation_type):
            return await self.add_operation(operation_type=operation_type, *args, **kwargs)

    async def resume_operation(self, operation: ABCOperation) -> None:
        """
        Resumes a specific operation.

        Args:
            operation (ABCOperation): The operation to resume.
        """
        if operation.status == "paused":
            await operation.resume()

    async def pause_operation(self, operation: ABCOperation) -> None:
        """
        Pauses a specific operation.

        Args:
            operation (ABCOperation): The operation to pause.
        """
        if operation.status == "running":
            await operation.pause()

    async def stop_operation(self, operation: ABCOperation) -> None:
        """
        Stops a specific operation.

        Args:
            operation (ABCOperation): The operation to stop.
        """
        await operation.stop()

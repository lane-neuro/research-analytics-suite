"""
OperationManager Module.

This module defines the OperationManager class, which manages the creation, queuing, and control of operations within
the neurobehavioral analytics suite. It provides methods to add, resume, pause, and stop operations.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

from neurobehavioral_analytics_suite.operation_manager.operations.Operation import Operation


class OperationManager:
    """
    A class to manage operations within the neurobehavioral analytics suite.

    This class provides methods to add operations to the queue, and to resume, pause, and stop operations.
    """

    def __init__(self, operation_control, queue, task_creator, logger, error_handler):
        """
        Initializes the OperationManager with the necessary components.

        Args:
            operation_control: Control interface for operations.
            queue: Queue holding operations to be managed.
            task_creator: Task creator for generating asyncio tasks.
            logger: Logger instance for logging messages.
            error_handler: Error handler for managing errors.
        """
        self.op_control = operation_control
        self.queue = queue
        self.task_creator = task_creator
        self.logger = logger
        self.error_handler = error_handler

    async def add_operation(self, operation_type, *args, **kwargs) -> Operation:
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
            self.logger.info(f"add_operation: [QUEUE] {operation.name}")
            return operation
        except Exception as e:
            self.logger.error(f"add_operation: {e}")

    async def add_operation_if_not_exists(self, operation_type, *args, **kwargs) -> None:
        """
        Adds an operation to the queue if it does not already exist.

        Args:
            operation_type: The type of operation to be created.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        if not self.task_creator.task_exists(operation_type):
            await self.add_operation(operation_type, *args, **kwargs)

    async def resume_operation(self, operation: Operation) -> None:
        """
        Resumes a specific operation.

        Args:
            operation (Operation): The operation to resume.
        """
        if operation.status == "paused":
            await operation.resume()

    async def pause_operation(self, operation: Operation) -> None:
        """
        Pauses a specific operation.

        Args:
            operation (Operation): The operation to pause.
        """
        if operation.status == "running":
            await operation.pause()

    async def stop_operation(self, operation: Operation) -> None:
        """
        Stops a specific operation.

        Args:
            operation (Operation): The operation to stop.
        """
        await operation.stop()

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
from neurobehavioral_analytics_suite.operation_manager.operation.Operation import Operation


class OperationManager:
    def __init__(self, handler, queue, task_manager, logger, error_handler):
        self.handler = handler
        self.queue = queue
        self.task_manager = task_manager
        self.logger = logger
        self.error_handler = error_handler

    async def add_operation(self, operation_type, *args, **kwargs) -> Operation:
        """
        Creates a new Operation and adds it to the queue.

        Args:
            operation_type: The type of operation to be created.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        op = operation_type(*args, **kwargs)
        new_op = await self.queue.add_operation_to_queue(op)
        self.logger.info(f"add_operation: [QUEUE] {new_op.name}")
        return new_op

    async def add_operation_if_not_exists(self, operation_type, *args, **kwargs):
        if not self.task_manager.task_exists(operation_type):
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

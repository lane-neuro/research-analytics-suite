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
    def __init__(self, queue, logger, error_handler):
        self.queue = queue
        self.logger = logger
        self.error_handler = error_handler

    async def add_operation(self, func, name: str = "Operation") -> Operation:
        """
        Creates a new Operation and adds it to the queue.

        Args:
            func (callable): The function to be executed by the Operation.
            name (str, optional): The name of the Operation. Defaults to "Operation".
        """
        self.logger.info(f"add_operation: [START] {name}")
        operation = Operation(name=name, error_handler=self.error_handler, func=func)
        self.logger.info(f"add_operation: New Operation: {operation.name}")
        await self.queue.add_operation_to_queue(operation)
        return operation

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

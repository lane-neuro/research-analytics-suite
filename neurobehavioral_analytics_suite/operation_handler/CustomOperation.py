"""
A module that defines the CustomOperation class, which is a subclass of the BaseOperation class.

The CustomOperation class is designed to handle custom operations that require func processing. It provides methods
for setting the func to be processed and executing the operation.

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

from neurobehavioral_analytics_suite.operation_handler.BaseOperation import BaseOperation
from neurobehavioral_analytics_suite.operation_handler.Operation import Operation
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler


class CustomOperation(BaseOperation):
    """
    A class used to represent a Custom Operation in the NeuroBehavioral Analytics Suite.

    This class provides methods for setting the data to be processed and executing the operation.

    Attributes:
        func (callable): A function to be executed.
        error_handler (ErrorHandler): An instance of ErrorHandler to handle any exceptions that occur.
        operation (Operation): The operation associated with the task.
    """

    def __init__(self, error_handler: ErrorHandler, func, local_vars, name: str = "CustomOperation"):
        """
        Initializes the CustomOperation with the func to be processed and an ErrorHandler instance.

        Args:
            func (callable): A function to be executed.
            error_handler (ErrorHandler): An instance of ErrorHandler to handle any exceptions that occur.
        """

        super().__init__()
        self.func = func
        self.error_handler = error_handler
        self.local_vars = local_vars
        self.operation = Operation(self)
        self.task = None
        self.persistent = False
        self.complete = False
        self.name = name
        self.status = "idle"
        self.result = None

    async def execute(self):
        """
        Executes the func.
        """
        self.status = "running"
        temp_vars = self.local_vars.copy()

        try:
            # Execute the function
            exec(self.func, {}, temp_vars)
            self.result = temp_vars
            self.local_vars = temp_vars

            return self.result

        except Exception as e:
            self.error_handler.handle_error(e, self)
            self.result = self.local_vars

            return self.result

    async def start(self) -> None:
        """
        Starts the operation and assigns the operation to the operation attribute.
        """

        # Check if the operation has already been started
        if self.operation is not None and self.task and not self.task.done():
            return

        self.status = "started"
        self.operation = Operation(self)
        if self.operation is not None:
            self.task = self.operation.start()

    async def stop(self) -> None:
        """
        Stops the operation by stopping the operation.
        """

        if self.operation is not None:
            await self.operation.stop()
            self.operation = None
            self.task = None

    async def pause(self) -> None:
        """
        Pauses the operation by pausing the operation.
        """

        if self.operation is not None and self.task and not self.task.done():
            await self.operation.pause()

    async def resume(self) -> None:
        """
        Resumes the operation by resuming the operation.
        """

        if self.operation is not None and self.task and self.task.done():
            await self.operation.resume()

    def get_status(self) -> str:
        """
        Returns the status of the operation.

        Returns:
            str: The status of the operation.
        """

        if self.operation is not None:
            return self.operation.get_status()
        return "idle"

    async def reset(self) -> None:
        """
        Resets the operation by resetting the operation.
        """

        if self.operation is not None and self.task and not self.task.done():
            await self.operation.reset()
            self.operation = None
            self.task = None

    def progress(self) -> int:
        """
        Returns the progress of the operation.

        Returns:
            int: The progress of the operation.
        """

        if self.operation is not None:
            return self.operation.progress()
        return 0

    def is_completed(self) -> bool:
        """
        Checks if the operation is complete.

        Returns:
            bool: True if the operation is complete, False otherwise.
        """

        return self.complete

"""
A module that defines the CustomOperation class, which is a subclass of the BaseOperation class.

The CustomOperation class is designed to handle custom operations that require data processing. It provides methods
for setting the data to be processed and executing the operation.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

from neurobehavioral_analytics_suite.operation_handler.BaseOperation import BaseOperation
from neurobehavioral_analytics_suite.operation_handler.Operation import Operation
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler


class CustomOperation(BaseOperation):
    """
    A class used to represent a Custom Operation in the NeuroBehavioral Analytics Suite.

    This class provides methods for setting the data to be processed and executing the operation.

    Attributes:
        data (str): A formatted string to print out the data that the operation will process.
        error_handler (ErrorHandler): An instance of ErrorHandler to handle any exceptions that occur.
        operation (Operation): The operation associated with the task.
    """

    def __init__(self, data, error_handler: ErrorHandler, name: str = "CustomOperation"):
        """
        Initializes the CustomOperation with the data to be processed and an ErrorHandler instance.

        Args:
            data (str): A formatted string to print out the data that the operation will process.
            error_handler (ErrorHandler): An instance of ErrorHandler to handle any exceptions that occur.
        """

        super().__init__()
        self.data = data
        self.error_handler = error_handler
        self.operation = Operation(self)
        self.task = None
        self.persistent = False
        self.complete = False
        self.name = name
        self.status = "idle"

    async def execute(self) -> str:
        """
        Prints the data.

        This is a placeholder implementation and should be replaced with actual data processing code.
        """

        print(f"CustomOperation.execute: Entered w/ {self.task.get_name()}")  # Debugging print statement
        self.status = "running"

        try:
            # Your task execution code here
            print(f"Processing data: {self.data}")

            # Mark the task as complete
            self.complete = True

            # If there's another operation linked to this one, mark it as complete too
            if self.operation is not None:
                self.operation.complete = True

        except Exception as e:
            self.error_handler.handle_error(e, self)

        print(f"CustomOperation.execute: returning: {self.task.get_name()}")  # Debugging print statement
        return self.data  # Return a result instead of a task

    async def start(self) -> None:
        """
        Starts the operation and assigns the operation to the operation attribute.
        """

        # Check if the operation has already been started
        if self.operation is not None and self.task and not self.task.done():
            print(f"CustomOperation.start: [ALREADY RUNNING] {self.task.get_name()}")
            return

        print(f"CustomOperation.start: Starting operation: {self.data} --- {self.task.get_name()}")
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

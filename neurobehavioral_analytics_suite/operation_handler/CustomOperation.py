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

import asyncio
from abc import abstractmethod

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

    def __init__(self, data, error_handler: ErrorHandler):
        """
        Initializes the CustomOperation with the data to be processed and an ErrorHandler instance.

        Args:
            data (str): A formatted string to print out the data that the operation will process.
            error_handler (ErrorHandler): An instance of ErrorHandler to handle any exceptions that occur.
        """

        super().__init__()
        self.data = data
        self.error_handler = error_handler
        self.operation = None
        self.task = None
        self.persistent = False
        self.complete = False

    async def execute(self):
        """
        Prints the data.

        This is a placeholder implementation and should be replaced with actual data processing code.
        """

        print("CustomOperation.execute called")  # Debugging print statement

        try:
            # Your task execution code here
            print(f"Processing data: {self.data}")

            # Mark the task as complete
            self.complete = True

            # If there's another operation linked to this one, mark it as complete too
            if self.operation is not None:
                self.operation.complete = True

        except Exception as e:
            # Handle any exceptions that might occur during task execution
            print(f"An error occurred: {e}")

        print(f"CustomOperation.execute completed: task: {self.task.done()}")  # Debugging print statement
        return self.data

    async def start(self):
        """
        Starts the operation and assigns the operation to the operation attribute.
        """

        # Check if the operation has already been started
        if self.operation is not None:
            print(f"Operation: {self.data} has already been started")
            return

        print(f"Starting operation: {self.data}")
        self.operation = Operation(self)
        if self.operation is not None:
            self.task = await self.operation.start()
            return self.task

    async def stop(self):
        """
        Stops the operation by stopping the operation.
        """

        if self.operation is not None:
            self.operation.stop()
            self.operation = None
            self.task = None

    async def pause(self):
        """
        Pauses the operation by pausing the operation.
        """

        if self.operation is not None and self.task and not self.task.done():
            self.operation.pause()

    async def resume(self):
        """
        Resumes the operation by resuming the operation.
        """

        if self.operation is not None and self.task and self.task.done():
            self.operation.resume()

    def get_status(self):
        """
        Returns the status of the operation.

        Returns:
            str: The status of the operation.
        """

        if self.operation is not None:
            return self.operation.get_status()
        return "idle"

    async def reset(self):
        """
        Resets the operation by resetting the operation.
        """

        if self.operation is not None and self.task and not self.task.done():
            self.operation.reset()
            self.operation = None
            self.task = None  # Change here

    def status(self):
        """
        Returns the status of the operation.

        Returns:
            str: The status of the operation.
        """

        return self.get_status()

    def progress(self):
        """
        Returns the progress of the operation.

        Returns:
            int: The progress of the operation.
        """

        if self.operation is not None:
            return self.operation.progress()
        return 0

    def is_completed(self):
        """
        Checks if the operation is complete.

        Returns:
            bool: True if the operation is complete, False otherwise.
        """

        return self.complete

"""
A module that defines the ConsoleOperation class, which is a subclass of the CustomOperation class.

The ConsoleOperation class is designed to handle user-input data from the console. It provides methods for
displaying a prompt for user input and processing the input data.

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
import logging
from aioconsole import ainput
from neurobehavioral_analytics_suite.operation_handler.CustomOperation import CustomOperation
from neurobehavioral_analytics_suite.utils import ErrorHandler


class ConsoleOperation(CustomOperation):
    """
    A class used to represent a Console Operation in the NeuroBehavioral Analytics Suite.

    This class provides methods for displaying a prompt for user input and processing the input data.

    Attributes:
        prompt (str): A string that is displayed as a prompt for user input.
        data (str): A formatted string to print out the data that the operation will process.
        logger (logging.Logger): A logger instance used for logging information.
    """

    def __init__(self, error_handler: ErrorHandler, operation_handler, prompt: str = '->> ', data=None):
        """
        Initializes the ConsoleOperation with a prompt for user input and the data to be processed.

        Args:
            error_handler (ErrorHandler): An instance of ErrorHandler to handle any exceptions that occur.
            prompt (str): A string that is displayed as a prompt for user input.
            data (str): A formatted string to print out the data that the operation will process.
        """

        super().__init__(data, error_handler)
        self.operation_handler = operation_handler
        self.error_handler = error_handler
        self.prompt = prompt
        self.logger = logging.getLogger(__name__)
        self.task = None
        self.status = "idle"

    async def execute(self):
        """
        Handles user-input data from the console.

        This method is responsible for asynchronously waiting for user input from the console & returns the input data.

        Returns:
            str: User-input data from the console.
        """

        line = await ainput(self.prompt)
        self.logger.info(f"User input: {line}")
        return line

    async def start(self):
        """
        Starts the operation.
        """

        try:
            user_input = await self.execute()
            self.operation_handler.process_user_input(user_input)
        except asyncio.CancelledError:
            pass

    def stop(self):
        """Stops the operation and handles any exceptions that occur during execution."""

        try:
            if self.task:
                self.task.cancel()
        except Exception as e:
            self.error_handler.handle_error(e, self)

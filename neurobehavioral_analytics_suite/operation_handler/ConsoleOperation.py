"""
A module that defines the ConsoleOperation class, which is a subclass of the CustomOperation class.

The ConsoleOperation class is designed to handle user-input func from the console. It provides methods for
displaying a prompt for user input and processing the input func.

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
import sys

import aioconsole
from neurobehavioral_analytics_suite.operation_handler.CustomOperation import CustomOperation
from neurobehavioral_analytics_suite.utils import ErrorHandler


class ConsoleOperation(CustomOperation):
    """
    A class used to represent a Console Operation in the NeuroBehavioral Analytics Suite.

    This class provides methods for displaying a prompt for user input and processing the input data.

    Attributes:
        prompt (str): A string that is displayed as a prompt for user input.
        func (str): A formatted string to print out the data that the operation will process.
        logger (logging.Logger): A logger instance used for logging information.
    """

    def __init__(self, error_handler: ErrorHandler, operation_handler, logger, local_vars, prompt: str = '->> ',
                 data=None, name: str = "ConsoleOperation"):
        """
        Initializes the ConsoleOperation with a prompt for user input and the func to be processed.

        Args:
            error_handler (ErrorHandler): An instance of ErrorHandler to handle any exceptions that occur.
            prompt (str): A string that is displayed as a prompt for user input.
            data (str): A formatted string to print out the func that the operation will process.
        """

        super().__init__(error_handler, data, local_vars)
        self.complete = False
        self.operation_handler = operation_handler
        self.error_handler = error_handler
        self.prompt = prompt
        self.logger = logger
        self.task = None
        self.name = name
        self.status = "idle"
        self.persistent = True

    async def execute(self) -> None:
        """Processes user input and sends it to the operation handler."""
        self.status = "running"
        self.task = asyncio.current_task()
        while True:  # Loop until a specific user input is received
            try:
                user_input = await aioconsole.ainput(self.prompt)  # Read user input
                user_input = user_input.strip()  # strip newline

                if user_input == "":  # Check for empty input
                    continue

                self.logger.debug(f"ConsoleOperation.execute: Received user input: {user_input}")

                if user_input == "exit":  # Exit condition
                    self.status = "stopped"
                    break

                await self.operation_handler.process_user_input(user_input)
            except UnicodeDecodeError as e:  # Catch specific exception
                self.logger.error(f"ConsoleOperation.execute: Exception occurred: {e}")
                break
            except Exception as e:  # Catch all other exceptions
                self.logger.error(f"ConsoleOperation.execute: Unexpected exception occurred: {e}")
                break

    async def start(self) -> None:
        """
        Starts the operation.
        """
        self.logger.debug("ConsoleOperation.start: [START]")  # Debugging print statement
        try:
            self.status = "started"  # Update the status of the operation
        except Exception as e:
            self.error_handler.handle_error(e, self)

    async def stop(self) -> None:
        """Stops the operation and handles any exceptions that occur during execution."""
        try:
            if self.task:
                self.task.cancel()
        except Exception as e:
            self.error_handler.handle_error(e, self)

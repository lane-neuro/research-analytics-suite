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
import logging

import aioconsole

from neurobehavioral_analytics_suite.operation_manager.operations.CustomOperation import CustomOperation
from neurobehavioral_analytics_suite.utils import ErrorHandler
from neurobehavioral_analytics_suite.utils.UserInputManager import UserInputManager


class ConsoleOperation(CustomOperation):
    """
    A class used to represent a Console Operation in the NeuroBehavioral Analytics Suite.

    This class provides methods for displaying a prompt for user input and processing the input data.

    Attributes:
        prompt (str): A string that is displayed as a prompt for user input.
        func (str): A formatted string to print out the data that the operations will process.
        logger (logging.Logger): A logger instance used for logging information.
    """

    def __init__(self, error_handler: ErrorHandler, user_input_handler: UserInputManager, logger, local_vars,
                 prompt: str = '->> ', data=None, name: str = "ConsoleOperation"):
        """
        Initializes the ConsoleOperation with a prompt for user input and the func to be processed.

        Args:
            error_handler (ErrorHandler): An instance of ErrorHandler to handle any exceptions that occur.
            prompt (str): A string that is displayed as a prompt for user input.
            data (str): A formatted string to print out the func that the operations will process.
        """

        super().__init__(error_handler=error_handler, func=self.execute, local_vars=local_vars, name=name)
        self.user_input_handler = user_input_handler
        self.error_handler = error_handler
        self.prompt = prompt
        self.logger = logger
        self.task = None
        self.name = name
        self._status = "idle"
        self.persistent = True

    async def execute(self) -> None:
        """Processes user input and sends it to the operations handler."""
        self._status = "running"

        while True:  # Loop until a specific user input is received
            try:
                user_input = await aioconsole.ainput(self.prompt)  # Read user input
                user_input = user_input.strip()  # strip newline

                if user_input == "":  # Check for empty input
                    continue

                self.logger.debug(f"ConsoleOperation.execute: Received user input: {user_input}")

                if user_input == "exit":  # Exit condition
                    self._status = "stopped"
                    break

                await self.user_input_handler.process_user_input(user_input)
            except UnicodeDecodeError as e:  # Catch specific exception
                self.logger.error(f"ConsoleOperation.execute: Exception occurred: {e}")
                break
            except Exception as e:  # Catch all other exceptions
                self.logger.error(f"ConsoleOperation.execute: Unexpected exception occurred: {e}")
                break
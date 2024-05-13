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
import queue
import sys
import threading

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

    def __init__(self, error_handler: ErrorHandler, operation_handler, loop, prompt: str = '->> ', data=None):
        """
        Initializes the ConsoleOperation with a prompt for user input and the data to be processed.

        Args:
            error_handler (ErrorHandler): An instance of ErrorHandler to handle any exceptions that occur.
            prompt (str): A string that is displayed as a prompt for user input.
            data (str): A formatted string to print out the data that the operation will process.
        """

        super().__init__(data, error_handler)
        self.complete = False
        self.operation_handler = operation_handler
        self.error_handler = error_handler
        self.prompt = prompt
        self.logger = logging.getLogger(__name__)
        self.task = None
        self.name = "ConsoleOperation"
        self.status = "idle"
        self.persistent = True
        self.loop = loop
        self.input_queue = queue.Queue()
        self.input_thread = threading.Thread(target=self.read_input)
        self.input_thread.start()

    def read_input(self) -> None:
        """Reads user input in a separate thread and adds it to the input queue."""
        while True:
            try:
                line = sys.stdin.readline()
                self.input_queue.put(line)
            except UnicodeDecodeError as e:
                self.error_handler.handle_error(e, self)

    async def execute(self) -> None:
        """Processes user input and sends it to the operation handler."""
        while not self.input_queue.empty():
            user_input = self.input_queue.get().strip()  # strip newline
            self.logger.info(f"ConsoleOperation.execute: Received user input: {user_input}")
            response = await self.operation_handler.process_user_input(user_input)
            self.logger.info(f"ConsoleOperation.execute: {response}")

    async def start(self) -> None:
        """
        Starts the operation.
        """
        self.logger.info("ConsoleOperation.start: [START]")  # Debugging print statement
        try:
            self.status = "running"  # Update the status of the operation
        except Exception as e:
            self.error_handler.handle_error(e, self)

    async def stop(self) -> None:
        """Stops the operation and handles any exceptions that occur during execution."""
        try:
            if self.task:
                self.task.cancel()
        except Exception as e:
            self.error_handler.handle_error(e, self)

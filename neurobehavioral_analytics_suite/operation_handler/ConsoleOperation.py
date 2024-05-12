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
        self.status = "idle"
        self.persistent = True
        self.loop = loop
        self.input_queue = queue.Queue()
        self.input_thread = threading.Thread(target=self.read_input)
        self.input_thread.start()

    def read_input(self):
        while True:
            try:
                line = sys.stdin.readline()
                self.input_queue.put(line)
            except UnicodeDecodeError:
                pass

    async def execute(self):
        while not self.input_queue.empty():
            user_input = self.input_queue.get()
            user_input = user_input.strip()  # strip newline
            response = self.operation_handler.process_user_input(user_input)
            return response

    async def start(self):
        """
        Starts the operation.
        """

        try:
            self.task = asyncio.ensure_future(self.execute())
            response = await self.task
            return response
        except asyncio.CancelledError:
            pass

    def stop(self):
        """Stops the operation and handles any exceptions that occur during execution."""

        try:
            if self.task:
                self.task.cancel()
        except Exception as e:
            self.error_handler.handle_error(e, self)

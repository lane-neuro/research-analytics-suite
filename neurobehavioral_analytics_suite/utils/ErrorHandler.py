"""
A module for the ErrorHandler class, which handles and logs errors that occur during runtime.

This class provides methods for logging errors to a specified file and handling errors that
occur during the execution of operations. It can be extended to include additional error
handling functionality as needed.

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


class ErrorHandler:
    """
    A class for handling and logging errors that occur during runtime.

    Attributes:
        logger (logging.Logger): A logger for logging error messages.
    """

    def __init__(self):
        """
        Initializes the ErrorHandler.
        """

        self.has_error = False
        self.error = None
        self.logger = logging.getLogger('operation_handler')
        self.logger.setLevel(logging.ERROR)
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def handle_error(self, error, operation):
        """
        Handles an error that occurred during the execution of an operation.

        This method logs the error message and the operation that caused the error.

        Args:
            error (Exception): The error that occurred.
            operation (Operation): The operation during which the error occurred.
        """

        self.error = error
        self.logger.error(f"An error occurred during the execution of operation {operation}: {error}")
        self.has_error = True

    async def check_for_errors(self):
        while True:
            if self.error:
                self.has_error = True
            else:
                self.has_error = False
            await asyncio.sleep(1)

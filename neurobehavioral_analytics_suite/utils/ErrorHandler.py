"""
A module that defines the ErrorHandler class, which is responsible for handling and logging errors during runtime.

The ErrorHandler class provides methods for logging errors to a specified file and handling errors that occur during
the execution of operations. It can be extended to include additional error handling functionality as needed.

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
import traceback


class ErrorHandler:
    """
    A class for handling and logging errors that occur during runtime.

    This class provides methods for logging errors to a specified file and handling errors that occur during the
    execution of operations. It can be extended to include additional error handling functionality as needed.

    Attributes:
        has_error (bool): A flag indicating whether an error has occurred.
        error (Exception): The error that occurred.
        logger (logging.Logger): A logger for logging error messages.
    """

    def __init__(self):
        """
        Initializes the ErrorHandler with a logger for logging error messages.
        """

        self.has_error = False
        self.error = None
        self.logger = logging.getLogger('operation_handler')
        self.logger.setLevel(logging.ERROR)
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def handle_error(self, e, context):
        """
        Handles an error that occurred during the execution of an operation.

        This method logs the error message and the operation that caused the error. It also sets the `has_error` flag
        to True.

        Args:
            e (Exception): The error that occurred.
            context: The contextual information for the error.
        """

        error_info = traceback.format_exc()
        error_message = f"An error occurred in {context}: {e}\n{error_info}"
        self.logger.error(error_message)
        self.has_error = True

    async def check_for_errors(self):
        """
        Continuously checks for errors.

        This method runs indefinitely, checking if an error has occurred every second. If an error has occurred, it
        sets the `has_error` flag to True. Otherwise, it sets the `has_error` flag to False.
        """

        while True:
            if self.error:
                self.has_error = True
            else:
                self.has_error = False
            await asyncio.sleep(1)  # Sleep for 1 second before checking again

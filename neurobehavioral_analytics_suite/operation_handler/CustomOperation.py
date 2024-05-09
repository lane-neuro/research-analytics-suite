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
from neurobehavioral_analytics_suite.operation_handler.BaseOperation import BaseOperation
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler


class CustomOperation(BaseOperation):
    """
    A class used to represent a Custom Operation in the NeuroBehavioral Analytics Suite.

    This class provides methods for setting the data to be processed and executing the operation.

    Attributes:
        data (str): A formatted string to print out the data that the operation will process.
        error_handler (ErrorHandler): An instance of ErrorHandler to handle any exceptions that occur.
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

    async def execute(self):
        """
        Prints the data and simulates a long-running operation by sleeping for 1 second.

        This is a placeholder implementation and should be replaced with actual data processing code.
        """

        print(f"Processing data: {self.data}")
        await asyncio.sleep(.5)

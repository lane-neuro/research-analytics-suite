"""
A module that defines the SubOperation class, which is a simpler version of an operation, specifically for the
sub-tasks in the Operation class.

The SubOperation class provides methods to start, stop, and reset a sub-operation. It also handles any exceptions that
occur during the execution of the sub-operation.

Typical usage example:

    error_handler = ErrorHandler()
    sub_operation = SubOperation(func, error_handler)
    sub_operation.start()

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
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler


class SubOperation:
    """
    A class for managing a simpler version of an operation, specifically for the sub-tasks in the Operation class.

    This class provides methods to start, stop, and reset a sub-operation. It also handles any exceptions that occur
    during the execution of the sub-operation.

    Attributes:
        func (callable): A callable representing the sub-operation to be performed.
        error_handler (ErrorHandler): An ErrorHandler instance to handle any exceptions that occur.
        persistent (bool): A boolean indicating whether the sub-operation should run indefinitely.
        task (asyncio.Task): An asyncio.Task instance representing the running sub-operation.
    """

    def __init__(self, func, error_handler: ErrorHandler = ErrorHandler(), persistent: bool = False):
        """
        Initializes the SubOperation with a callable function, an ErrorHandler instance, and a boolean indicating
        whether the sub-operation should run indefinitely.

        Args:
            func (callable): A callable representing the sub-operation to be performed.
            error_handler (ErrorHandler): An ErrorHandler instance to handle any exceptions that occur.
            persistent (bool): A boolean indicating whether the sub-operation should run indefinitely.
        """

        self.func = func
        self.error_handler = error_handler
        self.persistent = persistent
        self.task = None

    def start(self):
        """
        Starts the sub-operation.

        This method creates an asyncio task for the sub-operation and handles any exceptions that occur during its
        execution.
        """

        try:
            self.task = asyncio.create_task(self.func())
        except Exception as e:
            self.error_handler.handle_error(e, self)

    def stop(self):
        """
        Stops the sub-operation.

        This method cancels the asyncio task for the sub-operation if it exists.
        """

        if self.task is not None:
            self.task.cancel()

    def reset(self):
        """
        Resets the sub-operation.

        This method stops the sub-operation and then starts it again.
        """

        self.stop()
        self.start()

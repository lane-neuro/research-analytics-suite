"""
A module that defines the CustomOperation class, a subclass of the BaseOperation class.

The CustomOperation class is designed to handle custom operations that require function processing. It provides methods
for setting the function to be processed and executing the operation.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

from typing import Tuple
from neurobehavioral_analytics_suite.operation_handler.operations.Operation import Operation
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler


class CustomOperation(Operation):
    """A class used to represent a Custom Operation in the NeuroBehavioral Analytics Suite.

    This class provides methods for setting the data to be processed and executing the operation.

    Attributes:
        func (callable): A function to be executed.
        error_handler (ErrorHandler): An instance of ErrorHandler to handle any exceptions that occur.
    """

    def __init__(self, error_handler: ErrorHandler, func, local_vars, name: str = "CustomOperation"):
        """Initializes the CustomOperation with the function to be processed and an ErrorHandler instance.

        Args:
            error_handler (ErrorHandler): An instance of ErrorHandler to handle any exceptions that occur.
            func (callable): A function to be executed.
            local_vars (dict): Local variables to be used in the function execution.
            name (str): The name of the operation.
        """
        super().__init__(name=name, error_handler=error_handler, func=func)
        self.func = func
        self.error_handler = error_handler
        self.local_vars = local_vars
        self.task = None
        self.persistent = False
        self.complete = False
        self.name = name
        self.status = "idle"
        self.result_output = None

    async def execute(self):
        """Executes the operation and updates the status and result output accordingly.

        Returns:
            dict: The result output after function execution.
        """
        self.status = "running"
        temp_vars = self.local_vars.copy()

        try:
            exec(self.func, {}, temp_vars)
            self.result_output = temp_vars
            self.local_vars = temp_vars
            self.status = "completed"
            return self.result_output

        except Exception as e:
            self.error_handler.handle_error(e, self)
            self.result_output = temp_vars
            self.status = "error"
            return self.result_output

    async def start(self):
        """Starts the operation and updates the status accordingly."""
        try:
            self.status = "started"
        except Exception as e:
            self.error_handler.handle_error(e, self)
            self.status = "error"

    async def stop(self):
        """Stops the operation and updates the status accordingly."""
        try:
            self.status = "stopped"
        except Exception as e:
            self.error_handler.handle_error(e, self)
            self.status = "error"

    async def pause(self):
        """Pauses the operation and updates the status accordingly."""
        try:
            self.status = "paused"
            self.pause_event.clear()
        except Exception as e:
            self.error_handler.handle_error(e, self)
            self.status = "error"

    async def resume(self) -> None:
        """Resumes the operation and updates the status accordingly."""
        try:
            self.status = "running"
            self.pause_event.set()
        except Exception as e:
            self.error_handler.handle_error(e, self)
            self.status = "error"

    async def reset(self) -> None:
        """Resets the operation and updates the status accordingly."""
        try:
            self.progress = 0
            self.complete = False
            self.pause_event.clear()
            await self.stop()
            self.status = "stopped"
            await self.start()
            self.status = "started"
        except Exception as e:
            self.error_handler.handle_error(e, self)
            self.status = "error"

    def progress(self) -> Tuple[int, str]:
        """Returns the current progress and status of the operation.

        Returns:
            Tuple[int, str]: A tuple containing the current progress and status of the operation.
        """
        return self.progress, self.status

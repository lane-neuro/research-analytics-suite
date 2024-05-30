"""
This module contains the DaskOperation class, a subclass of the Operation class.

The DaskOperation class is used to represent a Dask Operation in the NeuroBehavioral Analytics Suite.
It provides methods for setting the data to be processed and executing the operation.

Typical usage example:

    dask_operation = DaskOperation(error_handler, func, local_vars)
    dask_operation.execute()

Attributes:
    func (callable): A function to be executed.
    error_handler (ErrorHandler): An instance of ErrorHandler to handle any exceptions that occur.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

from asyncio import Event
from typing import Tuple

from dask import delayed
from neurobehavioral_analytics_suite.operation_manager.operation.Operation import Operation
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler


class DaskOperation(Operation):
    """
    A class used to represent a Dask Operation in the NeuroBehavioral Analytics Suite.

    This class provides methods for setting the data to be processed and executing the operation.

    Attributes:
        func (callable): A function to be executed.
        error_handler (ErrorHandler): An instance of ErrorHandler to handle any exceptions that occur.
    """

    def __init__(self, error_handler: ErrorHandler, func, local_vars, name: str = "DaskOperation"):
        """
        Initializes the DaskOperation with the func to be processed and an ErrorHandler instance.

        Args:
            func (callable): A function to be executed.
            error_handler (ErrorHandler): An instance of ErrorHandler to handle any exceptions that occur.
        """

        super().__init__()
        self.func = func
        self.error_handler = error_handler
        self.local_vars = local_vars
        self.task = None
        self.persistent = False
        self.complete = False
        self.name = name
        self._status = "idle"
        self.result = None
        self.pause_event = Event()
        self.progress = 0

    async def execute(self):
        """
        Executes the operation.
        """
        self._status = "running"
        temp_vars = self.local_vars.copy()

        try:
            # Execute the function
            dask_func = delayed(self.func)
            result = dask_func.compute()
            temp_vars['result_output'] = result
            self.result = temp_vars
            self.local_vars = temp_vars

            return self.result

        except Exception as e:
            self.error_handler.handle_error(e, self)
            self.result = self.local_vars

            return self.result

    async def start(self):
        """Starts the operation and handles any exceptions that occur during execution."""
        await super().start()

    async def stop(self):
        """Stops the operation and handles any exceptions that occur during execution."""
        await super().stop()

    async def pause(self):
        """Pauses the operation and handles any exceptions that occur during execution."""
        await super().pause()

    async def resume(self) -> None:
        """Resumes the operation and handles any exceptions that occur during execution."""
        await super().resume()

    async def reset(self) -> None:
        """Resets the operation and handles any exceptions that occur during execution."""
        await super().reset()

    def progress(self) -> Tuple[int, str]:
        """Returns the current progress and status of the operation.

        Returns:
            A tuple containing the current progress and status of the operation.
        """
        return super().progress()

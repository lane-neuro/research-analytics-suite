"""
A module that defines the Operation class, which is responsible for managing tasks.

The Operation class represents a task that can be started, stopped, paused, resumed, and reset. It also tracks the
progress of the task and handles any exceptions that occur during execution.

    Typical usage example:

    error_handler = ErrorHandler()
    operation = Operation(BaseOperation(), error_handler)
    operation.start()

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
from abc import ABC, abstractmethod
from typing import Tuple

from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler


class Operation(ABC):
    """
    An abstract base class that defines a common interface for all operations.

    This class requires that any child class implement the execute, start, pause, stop, and resume methods.

    Attributes:
        status (str): The current status of the operation.
        progress (int): The current progress of the operation.
        persistent (bool): Whether the operation should run indefinitely.
        complete (bool): Whether the operation is complete.
        error_handler (ErrorHandler): An instance of ErrorHandler to handle any exceptions that occur.
        pause_event (asyncio.Event): An asyncio.Event instance for pausing and resuming the operation.
    """

    @property
    def status(self):
        return self._status

    def __init__(self, name: str = "Operation", error_handler: ErrorHandler = ErrorHandler(),
                 persistent: bool = False, func=None):
        """Initializes Operation with the operation to be managed and whether it should run indefinitely.

        Args:
            error_handler: An instance of ErrorHandler to handle any exceptions that occur.
            persistent: A boolean indicating whether the operation should run indefinitely.
        """
        self.name = name
        self.error_handler = error_handler
        self.func = func
        self.persistent = persistent
        self.status = "idle"
        self.task = None
        self.progress = 0
        self.complete = False
        self.pause_event = asyncio.Event()
        self.pause_event.set()
        self.type = type(self)

    @abstractmethod
    def progress(self) -> Tuple[int, str]:
        """Returns the progress of the operation."""
        pass

    async def update_progress(self):
        """Updates the progress of the operation until it's complete.

        This method sleeps for 1 second between each check.

        Note:
            This is a coroutine and should be awaited.
        """
        while not self.complete:
            if self.status == "running":
                await self.pause_event.wait()
                self.progress = self.progress + 1
            await asyncio.sleep(1)

    @abstractmethod
    async def execute(self):
        """
        Executes the operation.
        """
        self.status = "running"
        try:
            # Execute the function
            self.func()
            if not self.persistent:
                self.status = "completed"
        except Exception as e:
            self.error_handler.handle_error(e, self)
            self.status = "error"

    @abstractmethod
    async def start(self):
        """Starts the operation."""
        try:
            self.status = "started"
        except Exception as e:
            self.error_handler.handle_error(e, self)
            self.status = "error"

    @abstractmethod
    async def stop(self):
        """Stops the operation and handles any exceptions that occur during execution."""
        pass

    @abstractmethod
    async def pause(self):
        """Pauses the operation and handles any exceptions that occur during execution."""
        pass

    @abstractmethod
    async def resume(self):
        """Resumes the operation and handles any exceptions that occur during execution."""
        pass

    @abstractmethod
    async def reset(self):
        """Resets the operation and handles any exceptions that occur during execution."""
        pass

    def is_running(self):
        """Checks if the operation is currently running.

        Returns:
            True if the operation is running, False otherwise.
        """
        return self.status == "running"

    def is_complete(self):
        """Checks if the operation is complete.

        Returns:
            True if the operation is complete, False otherwise.
        """
        return self.complete

    def get_progress(self):
        """Gets the current progress of the operation.

        Returns:
            The current progress of the operation.
        """
        return self.progress

    def get_status(self):
        """Gets the current status of the operation.

        Returns:
            The current status of the operation.
        """
        return self.status

    @status.setter
    def status(self, value):
        self._status = value

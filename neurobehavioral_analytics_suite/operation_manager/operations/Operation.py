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
from concurrent.futures import ProcessPoolExecutor
from typing import Tuple

from neurobehavioral_analytics_suite.operation_manager.operations.BaseOperation import BaseOperation
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler


class Operation(BaseOperation):
    """
    An Operation class that defines a common interface for all operations, inherited from BaseOperation.

    This class requires that any child class implement the execute, start, pause, stop, and resume methods.

    Attributes:
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
                 persistent: bool = False, func=None, is_cpu_bound: bool = False):
        """Initializes Operation with the operation to be managed and whether it should run indefinitely.

        Args:
            error_handler: An instance of ErrorHandler to handle any exceptions that occur.
            persistent: A boolean indicating whether the operation should run indefinitely.
        """
        super().__init__()
        self.name = name
        self.error_handler = error_handler
        self.func = func
        self.persistent = persistent
        self.is_cpu_bound = is_cpu_bound
        self._status = "idle"
        self.task = None
        self.progress = 0
        self.complete = False
        self.pause_event = asyncio.Event()
        self.pause_event.set()
        self.type = type(self)

    def init_operation(self):
        """
        Initialize any resources or setup required for the operation before it starts.
        """
        pass

    async def start(self):
        """Starts the operation."""
        try:
            self._status = "started"
        except Exception as e:
            self.error_handler.handle_error(e, self)
            self._status = "error"

    async def execute(self):
        """
        Executes the operation.
        """
        self._status = "running"
        try:
            if self.is_cpu_bound:
                with ProcessPoolExecutor() as executor:
                    self.func = executor.submit(self.func).result()
            else:
                self.func()
            if not self.persistent:
                self._status = "completed"
        except Exception as e:
            self.error_handler.handle_error(e, self)
            self._status = "error"

    def get_result(self):
        """
        Gets the result of the operation.

        Returns:
            The result of the operation.
        """
        return self.func

    async def pause(self):
        """Pauses the operation."""
        try:
            self._status = "paused"
            self.pause_event.clear()
        except Exception as e:
            self.error_handler.handle_error(e, self)
            self._status = "error"

    async def resume(self):
        """Resumes the operation and handles any exceptions that occur during execution."""
        try:
            self._status = "running"
            self.pause_event.set()
        except Exception as e:
            self.error_handler.handle_error(e, self)
            self._status = "error"

    async def stop(self):
        """Stops the operation and handles any exceptions that occur during execution."""
        try:
            if self.task:
                self.task.cancel()
            self._status = "stopped"
        except Exception as e:
            self.error_handler.handle_error(e, self)
            self._status = "error"

    async def reset(self):
        """Resets the operation and handles any exceptions that occur during execution."""
        try:
            self._status = "idle"
            self.progress = 0
            self.pause_event.clear()
            await self.stop()
            await self.start()
            self.pause_event.set()
        except Exception as e:
            self.error_handler.handle_error(e, self)
            self._status = "error"

    async def restart(self):
        """
        Restart the operation from the beginning.
        """
        try:
            await self.reset()
            await self.start()
            await self.execute()
        except Exception as e:
            self.error_handler.handle_error(e, self)
            self._status = "error"

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
        return self._status == "completed"

    def is_paused(self):
        """
        Check if the operation is currently paused.
        """
        return self._status == "paused"

    def is_stopped(self):
        """
        Check if the operation is currently stopped.
        """
        return self._status == "stopped"

    def progress(self) -> Tuple[int, str]:
        """Returns the progress of the operation."""
        return self.progress, self._status

    async def update_progress(self):
        """Updates the progress of the operation until it's complete.

        This method sleeps for 1 second between each check.

        Note:
            This is a coroutine and should be awaited.
        """
        while not self.is_complete():
            if self.status == "running":
                await self.pause_event.wait()
                self.progress = self.progress + 1
            await asyncio.sleep(1)

    def cleanup_operation(self):
        """
        Clean up any resources or perform any necessary teardown after the operation has completed or been stopped.
        """
        self.func = None
        self.progress = 0
        self.pause_event.clear()
        self._status = "idle"
        self.task = None

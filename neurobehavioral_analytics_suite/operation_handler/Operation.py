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

from neurobehavioral_analytics_suite.operation_handler.BaseOperation import BaseOperation
from neurobehavioral_analytics_suite.operation_handler.SubOperation import SubOperation
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler


class Operation(BaseOperation):
    """
    Represents an operation that can be started, stopped, paused, resumed, and reset.

    This class tracks the progress of the operation and handles any exceptions that occur during its execution.

    Attributes:
        status (str): The current status of the operation.
        progress (int): The current progress of the operation.
        persistent (bool): Whether the operation should run indefinitely.
        complete (bool): Whether the operation is complete.
        error_handler (ErrorHandler): An instance of ErrorHandler to handle any exceptions that occur.
        operation (BaseOperation): The operation to be managed.
        pause_event (asyncio.Event): An asyncio.Event instance for pausing and resuming the operation.
        sub_tasks (list): A list of asyncio.Future instances representing the sub-tasks of the operation.
    """

    def __init__(self, operation: BaseOperation, name: str = "Operation", error_handler: ErrorHandler = ErrorHandler(),
                 persistent: bool = False):
        """Initializes Operation with the operation to be managed and whether it should run indefinitely.

        Args:
            operation: An instance of BaseOperation representing the operation to be managed.
            error_handler: An instance of ErrorHandler to handle any exceptions that occur.
            persistent: A boolean indicating whether the operation should run indefinitely.
        """
        super().__init__()
        self.task = None
        self.operation = operation
        self.error_handler = error_handler
        self.persistent = persistent
        # self.sub_tasks = []

        self.name = name
        self.status = "idle"
        self.complete = False
        self.progress = 0

        # self.update_progress_operation = SubOperation(self.update_progress, "_progress", self.error_handler, True)
        # self.check_for_errors_operation = SubOperation(self.check_for_errors, "_error_check", self.error_handler,
        # True)
        #
        # self.add_sub_operation(self.update_progress_operation)
        # self.add_sub_operation(self.check_for_errors_operation)

        self.pause_event = asyncio.Event()
        self.pause_event.set()

    # def add_sub_operation(self, operation):
    #     """Adds a sub-operation to the operation."""
    #     self.sub_tasks.append(operation)

    def progress(self):
        """Returns the current progress and status of the operation.

        Returns:
            A tuple containing the current progress and status of the operation.
        """
        return self.progress, self.status

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
                if self.progress >= 100:
                    self.on_complete()
            await asyncio.sleep(1)

    async def check_for_errors(self):
        """Checks for errors in the operation until it's complete.

        This method stops the operation if an error is found and sleeps for 1 second between each check.
        """
        while not self.complete:
            if self.error_handler.has_error:
                # for task in self.sub_tasks:
                #     await task.stop()
                await self.stop()
                break
            await asyncio.sleep(1)

    async def execute(self):
        """Executes the operation."""
        try:
            print("Operation: execute")
            self.status = "running"
            if self.complete:
                return

            await self.operation.execute()
            self.on_complete()
        except Exception as e:
            self.error_handler.handle_error(e, self)
            self.status = "error"

    async def start(self):
        """Starts the operation and handles any exceptions that occur during execution."""
        try:
            self.status = "started"
            # for task in self.sub_tasks:
            #     await task.start()
            #     print(f"Operation.start: [START] (Sub-Task) {task}")
            await self.operation.start()
            # return await self.execute()
        except Exception as e:
            self.error_handler.handle_error(e, self)
            self.status = "error"

    async def stop(self):
        """Stops the operation and handles any exceptions that occur during execution."""
        try:
            self.status = "stopped"
            # for task in self.sub_tasks:
            #     await task.stop()
        except Exception as e:
            self.error_handler.handle_error(e, self)
            self.status = "error"

    async def pause(self):
        """Pauses the operation and handles any exceptions that occur during execution."""
        try:
            self.status = "paused"
            self.pause_event.clear()
            # for task in self.sub_tasks:
            #     await task.pause()
        except Exception as e:
            self.error_handler.handle_error(e, self)
            self.status = "error"

    async def resume(self):
        """Resumes the operation and handles any exceptions that occur during execution."""
        try:
            self.status = "running"
            self.pause_event.set()
            # for task in self.sub_tasks:
            #     await task.resume()
        except Exception as e:
            self.error_handler.handle_error(e, self)
            self.status = "error"

    async def reset(self):
        """Resets the operation and handles any exceptions that occur during execution."""
        try:
            self.status = "idle"
            self.progress = 0
            self.complete = False
            self.pause_event.clear()
            # for task in self.sub_tasks:
            #     await task.reset()
            await self.stop()
            await self.start()
        except Exception as e:
            self.error_handler.handle_error(e, self)
            self.status = "error"

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
        return self._status

    @property
    def status(self):
        """Returns the current status of the operation.

        Returns:
            str: The current status of the operation.
        """
        return self.get_status()

    def on_complete(self):
        """Method to be called when the operation is complete.

        This method can be overridden in subclasses to provide custom behavior when the operation is complete.
        """
        self.complete = True
        self.progress = 100
        self.status = "complete"

    def is_completed(self):
        """Checks if the operation is complete.

        Returns:
            bool: True if the operation is complete, False otherwise.
        """
        return self.complete

    @status.setter
    def status(self, value):
        self._status = value

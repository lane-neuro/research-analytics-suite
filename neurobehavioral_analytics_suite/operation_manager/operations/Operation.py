"""
A module that defines the Operation class, which is responsible for managing tasks.

The Operation class represents a task that can be started, stopped, paused, resumed, and reset. It also tracks the
progress of the task and handles any exceptions that occur during execution.

    Typical usage example:

    error_handler = ErrorHandler()
    operations = Operation(ABCOperation(), error_handler)
    operations.start()

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
from typing import Tuple, List
from neurobehavioral_analytics_suite.operation_manager.operations.ABCOperation import ABCOperation
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler


class Operation(ABCOperation):
    """
    An Operation class that defines a common interface for all operations, inherited from ABCOperation.

    This class requires that any child class implement the execute, start, pause, stop, and resume methods.
    """

    def __init__(self, error_handler: ErrorHandler, func, name: str = "Operation", persistent: bool = False,
                 is_cpu_bound: bool = False, concurrent: bool = False, parent_operation: 'Operation' = None):
        """Initializes Operation with the operations to be managed and whether it should run indefinitely.

        Args:
            name: The name of the operations.
            persistent: A boolean indicating whether the operations should run indefinitely.
            func: The function to be executed by the operations.
            is_cpu_bound: A boolean indicating whether the operations is CPU-bound.
        """
        super().__init__()
        self._name = name
        self.func = func
        self._persistent = persistent
        self._is_cpu_bound = is_cpu_bound
        self._status = "idle"
        self._task = None
        self._progress = 0
        self._complete = False
        self._pause_event = asyncio.Event()
        self._pause_event.set()
        self._error_handler = error_handler

        self.parent_operation = parent_operation
        self.child_operations: List[Operation] = []
        self.concurrent = concurrent
        self.gui_module = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        assert isinstance(value, str), "Name must be a string"
        self._name = value

    @property
    def persistent(self):
        return self._persistent

    @persistent.setter
    def persistent(self, value):
        assert isinstance(value, bool), "Persistent must be a boolean"
        self._persistent = value

    @property
    def is_cpu_bound(self):
        return self._is_cpu_bound

    @is_cpu_bound.setter
    def is_cpu_bound(self, value):
        assert isinstance(value, bool), "is_cpu_bound must be a boolean"
        self._is_cpu_bound = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        assert value in ["idle", "started", "waiting", "running", "paused", "stopped", "completed", "error"], \
            "Invalid status"
        self._status = value

    @property
    def task(self):
        return self._task

    @task.setter
    def task(self, value):
        self._task = value

    @property
    def progress(self) -> Tuple[int, str]:
        """Returns the progress of the operations."""
        return self._progress, self._status

    @progress.setter
    def progress(self, value):
        assert isinstance(value, int), "Progress must be an integer"
        self._progress = value

    def attach_gui_module(self, gui_module):
        self.gui_module = gui_module
        self.log_to_gui(f"Attached GUI module to operations: {self.name}")

    def init_operation(self):
        """
        Initialize any resources or setup required for the operations before it starts.
        """
        pass

    def add_child_operation(self, operation: 'Operation'):
        self.child_operations.append(operation)
        self.log_to_gui(f"Added child operations: {operation.name}")

    def remove_child_operation(self, operation: 'Operation'):
        self.child_operations.remove(operation)
        self.log_to_gui(f"Removed child operations: {operation.name}")

    def is_ready(self) -> bool:
        # An operations is ready if all nested operations are completed
        return all(op.status == "completed" for op in self.child_operations if not op.concurrent)

    async def start(self):
        """Starts the operations and all child operations."""
        try:
            for operation in self.child_operations:
                await operation.start()
            self._status = "started"
            self.log_to_gui(f"Operation parameters initialized")
        except Exception as e:
            self._error_handler.handle_error(e, self)
            self.log_to_gui(f"Error starting operations: {e}")
            self._status = "error"

    async def execute(self):
        """
        Executes the operations.
        """

        if self._status == "started" or self._status == "waiting":
            try:
                for child_op in self.child_operations:
                    if not child_op.concurrent and child_op.status != "completed":
                        self.log_to_gui(f"Executing child operations: {child_op.name}")
                        await child_op.execute()

                if self.is_cpu_bound:
                    with ProcessPoolExecutor() as executor:
                        self.status = "running"
                        self.log_to_gui(f"Executing operations")
                        self.func = executor.submit(self.func).result()
                else:
                    if self.func is not None:
                        if asyncio.iscoroutinefunction(self.func):
                            self._status = "running"
                            self.log_to_gui(f"Executing operations")
                            await self.func()
                        else:
                            self._status = "running"
                            self.log_to_gui(f"Executing operations")
                            await asyncio.get_event_loop().run_in_executor(None, func=self.func)
                    else:
                        raise ValueError("self.func is None")
                if not self._persistent:
                    self._status = "completed"
                    self.log_to_gui(f"Operation completed")
            except Exception as e:
                self._error_handler.handle_error(e, self)
                self.log_to_gui(f"Error executing operations: {e}")
                self._status = "error"

    def get_result(self):
        """
        Gets the result of the operations.

        Returns:
            The result of the operations.
        """
        return self.func

    async def pause(self):
        """Pauses the operations."""
        try:
            self._status = "paused"
            self._pause_event.clear()
            self.log_to_gui(f"Operation paused")
        except Exception as e:
            self._error_handler.handle_error(e, self)
            self.log_to_gui(f"Error pausing operations: {e}")
            self._status = "error"

    async def resume(self):
        """Resumes the operations and handles any exceptions that occur during execution."""
        try:
            self._status = "running"
            self.log_to_gui(f"Operation resumed")
            self._pause_event.set()
        except Exception as e:
            self._error_handler.handle_error(e, self)
            self.log_to_gui(f"Error resuming operations: {e}")
            self._status = "error"

    async def stop(self):
        """Stops the operations and handles any exceptions that occur during execution."""
        try:
            if self._task:
                self._task.cancel()
            self._status = "stopped"
            self.log_to_gui(f"Operation stopped")
        except Exception as e:
            self._error_handler.handle_error(e, self)
            self.log_to_gui(f"Error stopping operations: {e}")
            self._status = "error"

    async def reset(self):
        """Resets the operations and handles any exceptions that occur during execution."""
        try:
            self._status = "idle"
            self._progress = 0
            self._pause_event.clear()
            await self.stop()
            await self.start()
            self._pause_event.set()
            self.log_to_gui(f"Operation reset")
        except Exception as e:
            self._error_handler.handle_error(e, self)
            self.log_to_gui(f"Error resetting operations: {e}")
            self._status = "error"

    async def restart(self):
        """
        Restart the operations from the beginning.
        """
        try:
            await self.reset()
            await self.start()
            await self.execute()
            self.log_to_gui(f"Operation restarted")
        except Exception as e:
            self._error_handler.handle_error(e, self)
            self._status = "error"

    def is_running(self):
        """Checks if the operations is currently running.

        Returns:
            True if the operations is running, False otherwise.
        """
        return self._status == "running"

    def is_complete(self):
        """Checks if the operations is complete.

        Returns:
            True if the operations is complete, False otherwise.
        """
        return self._status == "completed"

    def is_paused(self):
        """
        Check if the operations is currently paused.
        """
        return self._status == "paused"

    def is_stopped(self):
        """
        Check if the operations is currently stopped.
        """
        return self._status == "stopped"

    async def update_progress(self):
        """Updates the progress of the operations until it's complete.

        This method sleeps for 1 second between each check.

        Note:
            This is a coroutine and should be awaited.
        """
        while not self.is_complete():
            if self._status == "running":
                await self._pause_event.wait()
                self._progress = self._progress + 1
            await asyncio.sleep(1)

    def log_to_gui(self, message: str):
        """
        Log a message to the GUI.

        Args:
            message: The message to log.
        """
        if self.gui_module is not None:
            self.gui_module.log_event(message)

    def cleanup_operation(self):
        """
        Clean up any resources or perform any necessary teardown after the operations has completed or been stopped.
        """
        # self.func = None
        self._progress = 0
        self._pause_event.clear()
        self._status = "idle"
        self._task = None

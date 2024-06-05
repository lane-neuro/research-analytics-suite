"""
This module defines the abstract base class ABCOperation, providing a common interface for all operations in the
NeuroBehavioral Analytics Suite. The ABCOperation class requires any child class to implement execute, start, pause,
stop, and resume methods. It also provides a property for the status of the operation, which can be "idle", "started",
"paused", "running", or "stopped". This class is designed to be inherited by other classes that represent specific
operations.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

from abc import ABC, abstractmethod
from typing import Tuple, List, Any, Dict
import asyncio


class ABCOperation(ABC):
    """
    An abstract base class that defines a common interface for all operations.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the operation instance.

        Args:
            error_handler (ErrorHandler): The error handler for managing errors.
            func (callable, optional): The function to be executed by the operation.
            name (str, optional): The name of the operation. Defaults to "Operation".
            persistent (bool, optional): Whether the operation should run indefinitely. Defaults to False.
            is_cpu_bound (bool, optional): Whether the operation is CPU-bound. Defaults to False.
            concurrent (bool, optional): Whether child operations should run concurrently. Defaults to False.
            parent_operation (ABCOperation, optional): The parent operation. Defaults to None.
        """
        self._name = kwargs.get('name', "Operation")
        self._func = kwargs.get('func', None)
        self._local_vars = kwargs.get('local_vars', None)
        self._persistent = kwargs.get('persistent', False)
        self._is_cpu_bound = kwargs.get('is_cpu_bound', False)
        self._status = "idle"
        self._task = None
        self._progress = 0
        self._complete = False
        self._pause_event = asyncio.Event()
        self._pause_event.set()

        error_handler = kwargs.get('error_handler')
        if error_handler is None:
            raise ValueError("error_handler is required")
        self._error_handler = error_handler

        self._parent_operation = kwargs.get('parent_operation', None)
        self._child_operations: List['ABCOperation'] = []
        self._concurrent = kwargs.get('concurrent', False)
        self._gui_module = None
        self._result_output: Any = None

        self._dependencies: Dict[str, List[str]] = {}

    @property
    def name(self) -> str:
        """Gets the name of the operation."""
        return self._name

    @name.setter
    def name(self, value: str):
        """Sets the name of the operation."""
        if not isinstance(value, str):
            raise ValueError("Name must be a string")
        self._name = value

    @property
    def func(self):
        """Gets the function to be executed by the operation."""
        return self._func

    @func.setter
    def func(self, value):
        """Sets the function to be executed by the operation."""
        if not callable(value) and not isinstance(value, str):
            raise ValueError("func must be a callable or a string")
        self._func = value

    @property
    def local_vars(self):
        """Gets the local variables for the function execution."""
        return self._local_vars

    @local_vars.setter
    def local_vars(self, value):
        """Sets the local variables for the function execution."""
        if not isinstance(value, dict):
            raise ValueError("local_vars must be a dictionary")
        self._local_vars = value

    @property
    def persistent(self) -> bool:
        """Gets whether the operation should run indefinitely."""
        return self._persistent

    @persistent.setter
    def persistent(self, value: bool):
        """Sets whether the operation should run indefinitely."""
        if not isinstance(value, bool):
            raise ValueError("Persistent must be a boolean")
        self._persistent = value

    @property
    def is_cpu_bound(self) -> bool:
        """Gets whether the operation is CPU-bound."""
        return self._is_cpu_bound

    @is_cpu_bound.setter
    def is_cpu_bound(self, value: bool):
        """Sets whether the operation is CPU-bound."""
        if not isinstance(value, bool):
            raise ValueError("is_cpu_bound must be a boolean")
        self._is_cpu_bound = value

    @property
    def status(self) -> str:
        """Gets the status of the operation."""
        return self._status

    @status.setter
    def status(self, value: str):
        """Sets the status of the operation."""
        valid_statuses = ["idle", "started", "waiting", "running", "paused", "stopped", "completed", "error"]
        if value not in valid_statuses:
            raise ValueError(f"Invalid status: {value}")
        self._status = value

    @property
    def task(self):
        """Gets the task associated with the operation."""
        return self._task

    @task.setter
    def task(self, value):
        """Sets the task associated with the operation."""
        self._task = value

    @property
    def progress(self) -> Tuple[int, str]:
        """Gets the progress of the operation."""
        return self._progress, self._status

    @progress.setter
    def progress(self, value: int):
        """Sets the progress of the operation."""
        if not isinstance(value, int):
            raise ValueError("Progress must be an integer")
        self._progress = value

    @property
    def child_operations(self) -> List['ABCOperation']:
        """Gets the list of child operations."""
        return self._child_operations

    @property
    def parent_operation(self):
        """Gets the parent operation."""
        return self._parent_operation

    @parent_operation.setter
    def parent_operation(self, value):
        """Sets the parent operation."""
        if value is not None and not isinstance(value, ABCOperation):
            raise ValueError("parent_operation must be an instance of ABCOperation or None")
        self._parent_operation = value

    @property
    def concurrent(self) -> bool:
        """Gets whether child operations should run concurrently."""
        return self._concurrent

    @concurrent.setter
    def concurrent(self, value: bool):
        """Sets whether child operations should run concurrently."""
        if not isinstance(value, bool):
            raise ValueError("concurrent must be a boolean")
        self._concurrent = value

    @property
    def gui_module(self):
        """Gets the GUI module attached to the operation."""
        return self._gui_module

    @gui_module.setter
    def gui_module(self, value):
        """Sets the GUI module attached to the operation."""
        self._gui_module = value

    @abstractmethod
    def init_operation(self):
        """Initialize any resources or setup required for the operation before it starts."""
        pass

    def is_ready(self) -> bool:
        """
        Check if the operation is ready to be executed.

        An operation is considered ready if all its child operations are complete.

        Returns:
            bool: True if the operation is ready, False otherwise.
        """
        return all(child.is_complete() for child in self._child_operations if not child.concurrent)

    async def start(self):
        """
        Start the operation and all child operations.
        """
        try:
            await self._start_child_operations()
            self._status = "started"
        except Exception as e:
            self._handle_error(e)
            self._status = "error"

    async def execute(self):
        """
        Execute the operation and all child operations.
        """
        try:
            await self._execute_child_operations()
            self._status = "running"
            await self._execute_func()
            self._status = "completed"
        except Exception as e:
            self._handle_error(e)
            self._status = "error"

    @abstractmethod
    async def _execute_func(self):
        """Execute the main function of the operation."""
        pass

    @abstractmethod
    def get_result(self):
        """Retrieve the result of the operation, if applicable."""
        return self._result_output

    async def pause(self):
        """
        Pause the operation and all child operations.
        """
        self._status = "paused"
        await self._pause_child_operations()

    async def resume(self):
        """
        Resume the operation and all child operations.
        """
        self._status = "running"
        await self._resume_child_operations()

    async def stop(self):
        """
        Stop the operation and all child operations.
        """
        self._status = "stopped"
        await self._stop_child_operations()

    async def reset(self):
        """
        Reset the operation and all child operations.
        """
        self._status = "idle"
        self._progress = 0
        await self._reset_child_operations()

    async def restart(self):
        """
        Restart the operation and all child operations.
        """
        await self.reset()
        await self.start()
        await self.execute()

    def is_running(self) -> bool:
        """
        Check if the operation is currently running.
        """
        return self._status == "running"

    def is_complete(self) -> bool:
        """
        Check if the operation is complete.
        """
        return self._status == "completed"

    def is_paused(self) -> bool:
        """
        Check if the operation is currently paused.
        """
        return self._status == "paused"

    def is_stopped(self) -> bool:
        """
        Check if the operation is currently stopped.
        """
        return self._status == "stopped"

    async def update_progress(self):
        """
        Update the progress of the operation.
        """
        while not self.is_complete():
            if self._status == "running":
                await self._pause_event.wait()
                self._progress += 1
            await asyncio.sleep(1)

    def add_child_operation(self, operation: 'ABCOperation', dependencies: List[str] = None):
        """
        Add a child operation to the current operation.

        Args:
            operation (ABCOperation): The child operation to be added.
            dependencies (List[str], optional): List of operation names that the child operation depends on. Defaults to None.
        """
        if not isinstance(operation, ABCOperation):
            raise ValueError("operation must be an instance of ABCOperation")
        self._child_operations.append(operation)
        if dependencies:
            self._dependencies[operation.name] = dependencies

    def remove_child_operation(self, operation: 'ABCOperation'):
        """
        Remove a child operation from the current operation.

        Args:
            operation (ABCOperation): The child operation to be removed.
        """
        if not isinstance(operation, ABCOperation):
            raise ValueError("operation must be an instance of ABCOperation")
        self._child_operations.remove(operation)
        if operation.name in self._dependencies:
            del self._dependencies[operation.name]

    def attach_gui_module(self, gui_module):
        """
        Attach a GUI module to the operation.

        Args:
            gui_module: The GUI module to be attached.
        """
        self._gui_module = gui_module

    def log_to_gui(self, message: str):
        """
        Log a message to the GUI.

        Args:
            message (str): The message to log.
        """
        if self._gui_module is not None:
            self._gui_module.log_event(message)

    def _handle_error(self, e):
        """
        Handle an error that occurred during the operation.

        Args:
            e: The exception that occurred.
        """
        self._status = "error"
        self._error_handler.handle_error(e, self)

    def cleanup_operation(self):
        """
        Clean up any resources or perform any necessary teardown after the operation has completed or been stopped.
        """
        self._progress = 0
        self._status = "idle"
        self._task = None

    async def _start_child_operations(self):
        """
        Start all child operations.
        """
        tasks = [op.start() for op in self._child_operations]
        if self._concurrent:
            await asyncio.gather(*tasks)
        else:
            for task in tasks:
                await task

    async def _execute_child_operations(self):
        """
        Execute all child operations.
        """
        if not self._dependencies:
            await self._run_operations(self._child_operations)
        else:
            execution_order = self._determine_execution_order()
            await self._run_operations(execution_order)

    async def _pause_child_operations(self):
        """
        Pause all child operations.
        """
        tasks = [op.pause() for op in self._child_operations]
        await asyncio.gather(*tasks)

    async def _resume_child_operations(self):
        """
        Resume all child operations.
        """
        tasks = [op.resume() for op in self._child_operations]
        await asyncio.gather(*tasks)

    async def _stop_child_operations(self):
        """
        Stop all child operations.
        """
        tasks = [op.stop() for op in self._child_operations]
        await asyncio.gather(*tasks)

    async def _reset_child_operations(self):
        """
        Reset all child operations.
        """
        tasks = [op.reset() for op in self._child_operations]
        await asyncio.gather(*tasks)

    async def _run_operations(self, operations):
        """
        Run the specified operations.

        Args:
            operations (List[ABCOperation]): The operations to run.
        """
        tasks = [op.execute() for op in operations if not op.is_complete()]
        if self._concurrent:
            await asyncio.gather(*tasks)
        else:
            for task in tasks:
                await task

    def _determine_execution_order(self) -> List['ABCOperation']:
        """
        Determine the execution order of child operations based on dependencies.

        Returns:
            List[ABCOperation]: The execution order of child operations.
        """
        execution_order = []
        processed = set()
        while len(processed) < len(self._child_operations):
            for op in self._child_operations:
                if op.name not in processed and all(dep in processed for dep in self._dependencies.get(op.name, [])):
                    execution_order.append(op)
                    processed.add(op.name)
        return execution_order

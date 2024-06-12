# abc_operation.py

import asyncio
import types
import uuid
from abc import ABC
from concurrent.futures import ProcessPoolExecutor
from typing import Tuple, List, Any, Dict

from research_analytics_suite.data_engine.Workspace import Workspace
from research_analytics_suite.utils.CustomLogger import CustomLogger


class ABCOperation(ABC):
    """
    An abstract base class that defines a common interface for all operations.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the operation instance.

        Args:
            func (callable): The function to be executed by the operation.
            name (str, optional): The name of the operation. Defaults to "Operation".
            persistent (bool, optional): Whether the operation should run indefinitely. Defaults to False.
            is_cpu_bound (bool, optional): Whether the operation is CPU-bound. Defaults to False.
            concurrent (bool, optional): Whether child operations should run concurrently. Defaults to False.
            parent_operation (ABCOperation, optional): The parent operation. Defaults to None.
        """
        self._workspace = Workspace()
        self._logger = CustomLogger()
        self.operation_logs = []
        self._unique_id = str(uuid.uuid4())

        self._name = kwargs.get('name', "Operation")
        self._func = kwargs.get('func')
        self._persistent = kwargs.get('persistent', False)
        self._is_cpu_bound = kwargs.get('is_cpu_bound', False)
        self._status = "idle"
        self._task = None
        self._progress = 0
        self._complete = False
        self._pause_event = asyncio.Event()
        self._pause_event.set()
        self._is_ready = False

        self._parent_operation = kwargs.get('parent_operation', None)
        self._child_operations: List['ABCOperation'] = []
        self._concurrent = kwargs.get('concurrent', False)
        self._gui_module = None
        self._result_output: Any = None

        self._dependencies: Dict[str, List[str]] = {}

        self._process_func()

    @property
    def name(self) -> str:
        """Gets the name of the operation."""
        return self._name

    @name.setter
    def name(self, value: str):
        """Sets the name of the operation."""
        if not isinstance(value, str):
            self._handle_error("\'name\' property must be a string")
        self._name = value

    @property
    def func(self) -> callable:
        """Gets the function to be executed by the operation."""
        return self._func

    @func.setter
    def func(self, value):
        """Sets the function to be executed by the operation."""
        self._func = value

    @property
    def persistent(self) -> bool:
        """Gets whether the operation should run indefinitely."""
        return self._persistent

    @persistent.setter
    def persistent(self, value: bool):
        """Sets whether the operation should run indefinitely."""
        if not isinstance(value, bool):
            self._handle_error("\'persistent\' property must be a boolean")
        self._persistent = value

    @property
    def is_cpu_bound(self) -> bool:
        """Gets whether the operation is CPU-bound."""
        return self._is_cpu_bound

    @is_cpu_bound.setter
    def is_cpu_bound(self, value: bool):
        """Sets whether the operation is CPU-bound."""
        if not isinstance(value, bool):
            self._handle_error("\'is_cpu_bound\' property must be a boolean")
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
            self._handle_error(f"Invalid status: {value}")
        self._status = value

    @property
    def task(self):
        """Gets the task associated with the operation."""
        return self._task

    @task.setter
    def task(self, value: asyncio.Task):
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
            self._handle_error("\'progress\' property must be an integer")
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
            self._handle_error("\'parent_operation\' must be an instance of Operation")
        self._parent_operation = value

    @property
    def concurrent(self) -> bool:
        """Gets whether child operations should run concurrently."""
        return self._concurrent

    @concurrent.setter
    def concurrent(self, value: bool):
        """Sets whether child operations should run concurrently."""
        if not isinstance(value, bool):
            self._handle_error("\'concurrent\' property must be a boolean")
        self._concurrent = value

    @property
    def gui_module(self):
        """Gets the GUI module attached to the operation."""
        return self._gui_module

    @gui_module.setter
    def gui_module(self, value):
        """Sets the GUI module attached to the operation."""
        self._gui_module = value

    def init_operation(self):
        """Initialize any resources or setup required for the operation before it starts."""
        pass

    @property
    def is_ready(self):
        """Check if the operation is ready to be executed."""
        return self._is_ready

    @is_ready.setter
    def is_ready(self, value):
        """
        Check if the operation is ready to be executed.
        """
        if not isinstance(value, bool):
            self._handle_error("\'is_ready\' property must be a boolean")
        if not value:
            self._is_ready = False
            return

        self._is_ready = True
        for child in self._child_operations:
            if not child.is_complete() and not child._concurrent:
                self._is_ready = False

    async def start(self):
        """
        Start the operation and all child operations.
        """
        try:
            await self._start_child_operations()
            self._status = "started"
        except Exception as e:
            self._handle_error(e)

    async def execute(self):
        """
        Execute the operation and all child operations.
        """
        try:
            await self.execute_child_operations()
            await self._run_operations([self])
            if not self._persistent:
                self._status = "completed"
                self.add_log_entry(f"[COMPLETE]")
        except Exception as e:
            self._handle_error(e)

    async def _run_operations(self, operations):
        tasks = []
        for op in operations:
            if op.status != "completed":
                if op.func is not None:
                    tasks.append(op.execute_func())

        if self._concurrent and tasks and len(tasks) > 0:
            await asyncio.gather(*tasks)
        elif not self._concurrent and tasks and len(tasks) > 0:
            for task in tasks:
                self._result_output = await task

    def _process_func(self):
        """
        Process the function associated with the operation.
        """
        try:
            if isinstance(self._func, str):  # If self._func is a string of code
                code = self._func
                self._func = lambda: exec(code, {}, self._workspace._user_variables)
                self.add_log_entry(f"[CODE] {code}")
            elif callable(self._func):  # If self._func is a callable function
                if isinstance(self._func, types.MethodType):  # If self._func is a bound method
                    self._func = self._func
                else:
                    t_func = self._func
                    self._func = lambda: t_func()
            else:
                self._handle_error(Exception("Invalid function type"))
        except Exception as e:
            self._handle_error(e)

    async def execute_func(self):
        """
        Execute the function associated with the operation.
        """
        try:
            if self._is_cpu_bound:
                with ProcessPoolExecutor() as executor:
                    self._status = "running"
                    self.add_log_entry(f"[RUN] {self.name}: CPU-bound Operation")
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(executor, self._func)
            else:
                if self._func is not None:
                    if callable(self._func):
                        self._status = "running"
                        self.add_log_entry(f"[RUN] {self._name}")
                        if asyncio.iscoroutinefunction(self._func):
                            await self._func()
                        else:
                            self._func()
                else:
                    self._handle_error(Exception("No function provided for operation"))
        except Exception as e:
            self._handle_error(e)
        finally:
            self._result_output = await self._workspace.get_user_variable(f'result_{self._unique_id}')
            return self._result_output

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

    async def add_child_operation(self, operation: 'ABCOperation', dependencies: List[str] = None):
        """
        Add a child operation to the current operation.

        Args:
            operation (ABCOperation): The child operation to be added.
            dependencies (List[str], optional): List of operation names that the child operation depends on.
                                                Defaults to None.
        """
        if not isinstance(operation, ABCOperation):
            self._handle_error("operation must be an instance of ABCOperation")
            return

        operation.parent_operation = self
        self._child_operations.append(operation)

        await operation.start()

        if dependencies:
            self._dependencies[operation.name] = dependencies

        self.add_log_entry(f"[CHILD] (new) {operation.name}")

    def remove_child_operation(self, operation: 'ABCOperation'):
        """
        Remove a child operation from the current operation.

        Args:
            operation (ABCOperation): The child operation to be removed.
        """
        if not isinstance(operation, ABCOperation):
            self._handle_error("operation must be an instance of ABCOperation")
            return

        self._child_operations.remove(operation)
        if operation.name in self._dependencies:
            del self._dependencies[operation.name]

    def attach_gui_module(self, gui_module):
        """
        Attach a GUI module to the operation.

        Args:
            gui_module: The GUI module to be attached.
        """
        try:
            self._gui_module = gui_module
            self.add_log_entry(f"[GUI] Hooked module")
        except Exception as e:
            self._handle_error(e)

    def add_log_entry(self, message):
        """
        Log a message to the GUI.

        Args:
            message (str): The message to log.
        """
        if self._status == "error" and isinstance(message, Exception):
            self._logger.error(message, self)
        else:
            self.operation_logs.insert(0, message)
            self._logger.info(f"[{self._name}] {message}")

    def _handle_error(self, e):
        """
        Handle an error that occurred during the operation.

        Args:
            e: The exception that occurred.
        """
        self._status = "error"
        self.add_log_entry(e)

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
        try:
            if self._concurrent:
                await asyncio.gather(*tasks)
            else:
                for task in tasks:
                    await task
        except Exception as e:
            self._handle_error(e)

    async def execute_child_operations(self):
        """
        Execute all child operations.
        """
        if not self._dependencies:
            if self._child_operations is not None:
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

    def _determine_execution_order(self) -> List['ABCOperation']:
        """
        Determine the execution order of child operations based on dependencies.

        Returns:
            List[ABCOperation]: The execution order of child operations.
        """
        self.add_log_entry(f"Determining execution order")
        execution_order = []
        processed = set()
        while len(processed) < len(self._child_operations):
            for op in self._child_operations:
                if op.name not in processed and all(dep in processed for dep in self._dependencies.get(op.name, [])):
                    execution_order.append(op)
                    processed.add(op.name)
        return execution_order


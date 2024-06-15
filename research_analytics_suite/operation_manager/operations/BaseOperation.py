# abc_operation.py

import asyncio
import os.path
import pickle
import types
import uuid
from abc import ABC
from concurrent.futures import ProcessPoolExecutor
from copy import copy
from typing import Tuple, List, Dict

import aiofiles

from research_analytics_suite.data_engine.Config import Config
from research_analytics_suite.data_engine.Workspace import Workspace
from research_analytics_suite.utils.CustomLogger import CustomLogger


class BaseOperation(ABC):
    """
    An abstract base class that defines a common interface for all operations.
    """
    _lock = asyncio.Lock()

    def __init__(self, *args, **kwargs):
        """
        Initialize the operation instance.
        """
        if not hasattr(self, '_initialized'):
            self.temp_args = args
            self.temp_kwargs = kwargs

            self._workspace = None
            self._logger = None
            self._config = None
            self._operation_control = None
            self._pause_event = None
            self._gui_module = None

            self.operation_logs = None

            self._name = None
            self._unique_id = f"{uuid.uuid4().hex[:8]}"
            self._func = None
            self._persistent = None
            self._is_cpu_bound = None
            self._status = None
            self._task = None
            self._progress = None
            self._is_ready = None

            self._parent_operation = None
            self._child_operations: List['BaseOperation'] = []
            self._concurrent = None
            self.result_output = dict()

            self._dependencies: Dict[str, List[str]] = {}
            self._initialized = False

    @property
    def unique_id(self) -> str:
        """Gets the unique ID of the operation."""
        return f"{self._name}_{self._unique_id}"

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
    def child_operations(self) -> List['BaseOperation']:
        """Gets the list of child operations."""
        return self._child_operations

    @property
    def parent_operation(self):
        """Gets the parent operation."""
        return self._parent_operation

    @parent_operation.setter
    def parent_operation(self, value):
        """Sets the parent operation."""
        if value is not None and not isinstance(value, BaseOperation):
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
            if not child.is_complete() and not child.concurrent:
                self._is_ready = False

    async def _process_func(self):
        """
        Process the function associated with the operation.
        """
        try:
            if isinstance(self._func, str):  # If self._func is a string of code
                code = self._func
                self._func = self._execute_code_func(code)
                self.add_log_entry(f"[CODE] {code}")
            elif callable(self._func):  # If self._func is a callable function
                if isinstance(self._func, types.MethodType):  # If self._func is a bound method
                    self._func = self._func
                else:
                    t_func = self._func
                    self._func = self._execute_callable_func(t_func)
            else:
                self._handle_error(Exception("Invalid function type"))
        except Exception as e:
            self._handle_error(e)

    def _execute_code_func(self, code):
        def func():
            exec(code, {}, self.result_output)

        return func

    def _execute_callable_func(self, t_func):
        def func():
            t_func()

        return func

    async def initialize_operation(self):
        """Initialize any resources or setup required for the operation before it starts."""
        if hasattr(self, '_initialized') and not self._initialized:
            async with BaseOperation._lock:
                if not self._initialized:
                    self._workspace = Workspace()
                    self._config = Config()
                    self._logger = CustomLogger()

                    from research_analytics_suite.operation_manager.OperationControl import OperationControl
                    self._operation_control = OperationControl()

                    self._pause_event = asyncio.Event()
                    self._pause_event.set()

                    self._gui_module = None

                    self.operation_logs = self.temp_kwargs.get('operation_logs', [])

                    self._name = self.temp_kwargs.get('name', "Operation")
                    self._func = self.temp_kwargs.get('func')
                    self._persistent = self.temp_kwargs.get('persistent', False)
                    self._is_cpu_bound = self.temp_kwargs.get('is_cpu_bound', False)
                    self._status = "idle"
                    self._task = None
                    self._progress = 0
                    self._is_ready = False

                    self._parent_operation = self.temp_kwargs.get('parent_operation', None)
                    self._child_operations: List['BaseOperation'] = self.temp_kwargs.get('child_operations', [])
                    self._concurrent = self.temp_kwargs.get('concurrent', False)
                    self.result_output = self.temp_kwargs.get('result_output', dict())

                    self._dependencies: Dict[str, List[str]] = self.temp_kwargs.get('dependencies', {})

                    self.add_log_entry(f"[INIT] {self._name}")
                    self._initialized = True

                    # Clean up temporary attributes
                    delattr(self, 'temp_args')
                    delattr(self, 'temp_kwargs')

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
            await self._process_func()
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
                await task
                self.add_log_entry(f"[RESULT] {self.result_output}")

    async def execute_func(self):
        """
        Execute the function associated with the operation.
        """
        try:
            if self._is_cpu_bound:
                with ProcessPoolExecutor() as executor:
                    self._status = "running"
                    self.add_log_entry(f"[RUN] {self.name}: CPU-bound Operation")
                    await asyncio.get_event_loop().run_in_executor(executor, self._func)
                    self.result_output = await self._workspace.add_user_variable(name=f"[RESULT] {self._name}",
                                                                                 value=self.result_output,
                                                                                 memory_id=f'result_{self._unique_id}')
                    self.add_log_entry(f"[RESULT] {self.result_output}")
            else:
                if self._func is not None:
                    if callable(self._func):
                        self._status = "running"
                        if asyncio.iscoroutinefunction(self._func):
                            self.add_log_entry(f"[RUN - ASYNC] {self._name}")
                            await self._func()
                            self.add_log_entry(f"[RESULT] {self.result_output}")
                            self.result_output = await self._workspace.add_user_variable(name=f"[RESULT] {self._name}",
                                                                                         value=self.result_output,
                                                                                         memory_id=
                                                                                         f'result_{self._unique_id}')
                        else:
                            self.add_log_entry(f"[RUN] {self._name}")
                            self._func()
                            self.add_log_entry(f"[RESULT] {self.result_output}")
                            self.result_output = await self._workspace.add_user_variable(name=f"[RESULT] {self._name}",
                                                                                         value=self.result_output,
                                                                                         memory_id=
                                                                                         f'result_{self._unique_id}')
                else:
                    self._handle_error(Exception("No function provided for operation"))
        except Exception as e:
            self._handle_error(e)

    def get_result(self):
        """Retrieve the result of the operation, if applicable."""
        return self.result_output

    async def pause(self, child_operations=False):
        """
        Pause the operation and all child operations, if applicable.
        """
        if self._status == "running":
            try:
                self.is_ready = False

                if child_operations and self._child_operations is not None:
                    await self._pause_child_operations()

                await self._pause_event.clear()
                self._status = "paused"
            except Exception as e:
                self._handle_error(e)
                return
            finally:
                self.add_log_entry(f"[PAUSE] {self.name}")
        else:
            self.add_log_entry(f"[PAUSE] {self.name} - Already paused")

    async def resume(self, child_operations=False):
        """
        Resume the operation and all child operations, if applicable.
        """
        if self._status == "paused":
            try:
                self.is_ready = True

                if child_operations and self._child_operations is not None:
                    await self._resume_child_operations()
                await self._pause_event.set()
                self._status = "running"
            except Exception as e:
                self._handle_error(e)
                return
            self.add_log_entry(f"[RESUME] {self.name}")
        else:
            self.add_log_entry(f"[RESUME] {self.name} - Already running")

    async def stop(self, child_operations=False):
        """
        Stop the operation and all child operations, if applicable.
        """
        if self._status == "running":
            try:
                self.is_ready = False

                if child_operations and self._child_operations is not None:
                    await self._stop_child_operations()
                self._task.cancel()
                self._status = "stopped"
            except Exception as e:
                self._handle_error(e)
                return
            self.add_log_entry(f"[STOP] {self.name}")
        else:
            self.add_log_entry(f"[STOP] {self.name} - Already stopped")

    async def reset(self, child_operations=False):
        """
        Reset the operation and all child operations, if applicable.
        """
        self.is_ready = False

        if (self._status == "running"
                or self._status == "paused"
                or self._status == "completed"
                or self._status == "error"):
            if child_operations and self._child_operations is not None:
                await self._reset_child_operations()
            await self.stop()
            await self.start()
            self._progress = 0
            self.add_log_entry(f"[RESET] {self.name}")
        else:
            self.add_log_entry(f"[RESET] {self.name} - Already reset")

    async def restart(self, child_operations=False):
        """
        Restart the operation and all child operations, if applicable.
        """
        self.is_ready = False
        await self.reset(child_operations)

        self.is_ready = True
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

    async def add_child_operation(self, operation: 'BaseOperation', dependencies: List[str] = None):
        """
        Add a child operation to the current operation.

        Args:
            operation (BaseOperation): The child operation to be added.
            dependencies (List[str], optional): List of operation names that the child operation depends on.
                                                Defaults to None.
        """
        if not isinstance(operation, BaseOperation):
            self._handle_error("operation must be an instance of BaseOperation")
            return

        self._child_operations.append(operation)

        if dependencies:
            self._dependencies[operation.name] = dependencies

        self.add_log_entry(f"[CHILD] (added) {operation.name}")

    def remove_child_operation(self, operation: 'BaseOperation'):
        """
        Remove a child operation from the current operation.

        Args:
            operation (BaseOperation): The child operation to be removed.
        """
        if not isinstance(operation, BaseOperation):
            self._handle_error("operation must be an instance of BaseOperation")
            return

        self._child_operations.remove(operation)
        if operation.name in self._dependencies:
            del self._dependencies[operation.name]
        self.add_log_entry(f"[CHILD] (removed) {operation.name}")

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
        tasks = [op.pause(True) for op in self._child_operations]
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

    def _determine_execution_order(self) -> List['BaseOperation']:
        """
        Determine the execution order of child operations based on dependencies.

        Returns:
            List[BaseOperation]: The execution order of child operations.
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

    async def save_operation_in_workspace(self, file_name: str):
        """Save the BaseOperation object to disk."""

        if file_name is None:
            file_name = self._name

        # Exclude non-serializable attributes
        stripped_state = self._pack_non_serializable_attributes()
        dir_path = (f"{self._config.BASE_DIR}/{self._config.WORKSPACE_NAME}/"
                    f"{self._config.WORKSPACE_OPERATIONS_DIR}")
        file_ext = f".pkl"

        os.makedirs(dir_path, exist_ok=True)

        if os.path.exists(f"{dir_path}/{file_name}{file_ext}"):
            # Find the next available workspace name
            i = 1
            while True:
                file_name = f"{self.name}-{i}"
                if not os.path.exists(f"{dir_path}/{file_name}{file_ext}"):
                    break
                i += 1

        file_path = f"{dir_path}/{file_name}{file_ext}"

        async with aiofiles.open(file_path, 'wb') as file:
            await file.write(pickle.dumps(stripped_state))

    def _pack_non_serializable_attributes(self):
        """Exclude non-serializable attributes before saving."""
        _self_copy = copy(self)
        _self_copy._operation_control = None
        _self_copy._logger = None
        _self_copy._workspace = None
        _self_copy._pause_event = None
        _self_copy._gui_module = None
        _self_copy._config = None
        _self_copy._lock = None
        _self_copy._task = None
        # _self_copy._func = None  # Set to None or dummy function
        _self_copy.__delattr__('_initialized')
        return _self_copy

    @staticmethod
    async def load_from_disk(file_path: str):
        """Load an BaseOperation object from disk."""
        async with aiofiles.open(file_path, 'rb') as file:
            data = await file.read()
            op_data = pickle.loads(data)

            args = {}

            # Create a kwargs dictionary with all attributes from op_data
            kwargs = {
                'operation_logs': op_data.operation_logs,
                'name': op_data._name,
                'unique_id': op_data._unique_id,
                'func': op_data._func,
                'persistent': op_data._persistent,
                'is_cpu_bound': op_data._is_cpu_bound,
                'status': op_data._status,
                'progress': op_data._progress,
                'is_ready': op_data._is_ready,
                'parent_operation': op_data._parent_operation,
                'child_operations': op_data._child_operations,
                'concurrent': op_data._concurrent,
                'result_output': op_data.result_output,
                'dependencies': op_data._dependencies
            }

            return type(BaseOperation), args, kwargs

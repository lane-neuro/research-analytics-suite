"""
BaseOperation Module

This module defines the BaseOperation class, an abstract base class for all operations in the research analytics suite.

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
import json
import os.path
import types
import uuid
from abc import ABC
from concurrent.futures import ProcessPoolExecutor
from typing import Tuple, List, Any

import aiofiles

from research_analytics_suite.data_engine.Config import Config
from research_analytics_suite.data_engine.Workspace import Workspace
from research_analytics_suite.utils.CustomLogger import CustomLogger


class BaseOperation(ABC):
    """
    An abstract base class that defines a common interface for all operations.
    """
    _lock = asyncio.Lock()
    _GENERATED_ID = None

    def __init__(self, *args, **kwargs):
        """
        Initialize the operation instance.
        """
        if not hasattr(self, '_initialized'):
            self.temp_args = args
            self.temp_kwargs = kwargs

            self._GENERATED_ID = uuid.uuid4()

            self._workspace = None
            self._logger = None
            self._config = None
            self._operation_control = None
            self._pause_event = None
            self._gui_module = None

            self._name = None
            self._unique_id = None
            self._version = 0
            self._action = None
            self._persistent = None
            self._is_cpu_bound = None
            self._concurrent = None
            self.result_output = dict()

            self._status = None
            self._task = None
            self._progress = None
            self._is_ready = None

            self._dependencies: dict[BaseOperation.unique_id, 'BaseOperation'] = (
                dict[BaseOperation.unique_id, 'BaseOperation']()
            )
            self._parent_operation = None
            self._child_operations: dict[BaseOperation.runtime_id, 'BaseOperation'] = (
                dict[BaseOperation.runtime_id, 'BaseOperation']()
            )
            self.operation_logs = []

            self._initialized = False

    def __setstate__(self, state):
        """
        Set the state of the operation.
        """
        self.__dict__.update(state)

    @staticmethod
    async def from_dict(data: dict, file_dir, parent_operation: 'BaseOperation' = None,
                        ) -> 'BaseOperation':
        """Create a BaseOperation instance from a dictionary."""
        data_metadata = data.copy()

        # Search for the operation file if data does not contain an action
        # An operation filename consists of the operation name, unique ID[:4], and version, if applicable
        if 'action' not in data_metadata.keys():
            operation_file = f"{data_metadata.get('name')}_{data_metadata.get('unique_id')[:4]}"
            if 'version' in data_metadata and data_metadata.get('version') != 0:
                operation_file += f"-{data_metadata.get('version')}"
            operation_file += ".json"
            operation_file = os.path.join(file_dir, operation_file)

            # Check if the operation file exists
            if os.path.exists(operation_file):
                # Use the operation file to populate the data dictionary
                try:
                    async with aiofiles.open(operation_file, mode='r') as f:
                        operation_data = await f.read()
                        op_file_data = json.loads(operation_data)

                        data_metadata['action'] = op_file_data.get('action')
                        data_metadata['dependencies'] = op_file_data.get('dependencies')
                        data_metadata['child_operations'] = op_file_data.get('child_operations')
                        # data_metadata['operation_logs'] = op_file_data.get('operation_logs')
                        data_metadata['persistent'] = op_file_data.get('persistent')
                        data_metadata['is_cpu_bound'] = op_file_data.get('is_cpu_bound')
                        data_metadata['concurrent'] = op_file_data.get('concurrent')
                except Exception as e:
                    raise e

            else:
                raise FileNotFoundError(f"Operation file not found for operation: {operation_file}")

        if parent_operation is not None:
            data_metadata['parent_operation'] = parent_operation

        # Check if the parent operation is a dictionary
        if isinstance(data_metadata.get('parent_operation'), dict):
            try:
                data_metadata['parent_operation'] = await BaseOperation.from_dict(
                    data=data_metadata.get('parent_operation'),
                    file_dir=file_dir
                )
            except Exception as e:
                raise e
        else:
            data_metadata['parent_operation'] = parent_operation

        # Initialize the base operation instance
        operation = BaseOperation()
        operation.temp_kwargs = data_metadata
        await operation.initialize_operation()

        return operation

    async def initialize_operation(self):
        """Initialize any resources or setup required for the operation before it starts."""
        if hasattr(self, '_initialized') and not self._initialized:
            async with self._lock:
                if not self._initialized:
                    self._workspace = Workspace()
                    self._logger = CustomLogger()
                    self._config = Config()

                    from research_analytics_suite.operation_manager.OperationControl import OperationControl
                    self._operation_control = OperationControl()

                    self._pause_event = asyncio.Event()
                    self._pause_event.set()

                    self._gui_module = None

                    self._name = self.temp_kwargs.get('name', "[missing name]")
                    self._unique_id = self.temp_kwargs.get('unique_id', f"{uuid.uuid4()}")
                    self._version = self.temp_kwargs.get('version', 0)
                    self._action = self.temp_kwargs.get('action')
                    self._persistent = self.temp_kwargs.get('persistent', False)
                    self._is_cpu_bound = self.temp_kwargs.get('is_cpu_bound', False)
                    self._concurrent = self.temp_kwargs.get('concurrent', False)
                    self.result_output = self.temp_kwargs.get('result_output', dict())

                    self._status = "idle"
                    self._task = None
                    self._progress = 0
                    self._is_ready = False

                    self._dependencies: dict[BaseOperation.unique_id, 'BaseOperation'] = self.temp_kwargs.get(
                        'dependencies', dict[BaseOperation.unique_id, 'BaseOperation']())

                    _file_dir = os.path.join(self._config.BASE_DIR, self._config.WORKSPACE_NAME,
                                             self._config.WORKSPACE_OPERATIONS_DIR)

                    self._parent_operation = self.temp_kwargs.get('parent_operation')

                    if self._child_operations is not None:
                        for u_id, child in enumerate(self._child_operations):

                            # Convert dictionary to BaseOperation instance
                            if isinstance(child, dict):
                                await self.link_child_operation(await BaseOperation.from_dict(data=child,
                                                                                              file_dir=_file_dir,
                                                                                              parent_operation=self))

                            # Set the parent operation of the child operation
                            if self._child_operations[u_id].parent_operation is None:
                                self._child_operations[u_id].parent_operation = self

                    self.operation_logs = self.temp_kwargs.get('operation_logs', [])
                    self.add_log_entry(f"[INIT] {self._name}")
                    self._initialized = True
                    await self._operation_control.operation_manager.add_initialized_operation(self)

                    # Clean up temporary attributes
                    delattr(self, 'temp_args')
                    delattr(self, 'temp_kwargs')

    @property
    def initialized(self) -> bool:
        """Gets whether the operation has been initialized."""
        return self._initialized

    @property
    def unique_id(self) -> str:
        """Gets the unique ID of the operation."""
        return f"{self._unique_id}"

    @property
    def short_id(self) -> str:
        """Gets the short unique ID of the operation."""
        return f"{self._unique_id[:4]}"

    @property
    def runtime_id(self) -> str:
        """Gets the runtime ID of the operation."""
        return f"{self.short_id}_{self._GENERATED_ID}"

    @property
    def version(self) -> int:
        """Gets the file index of the operation."""
        return self._version

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
    def action(self) -> callable:
        """Gets the action to be executed by the operation."""
        return self._action

    @action.setter
    def action(self, value):
        """Sets the action to be executed by the operation."""
        self._action = value

    def action_serializable(self) -> str:
        """Gets the serializable action to be executed by the operation."""
        if isinstance(self._action, types.MethodType) or isinstance(self._action, types.FunctionType):
            action = f"{self._action.__code__}"
        elif isinstance(self._action, str):
            action = self._action
        else:
            action = None
        return action

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
    def child_operations(self) -> dict[runtime_id, 'BaseOperation']:
        """Gets the list of child operations."""
        return self._child_operations

    @property
    def dependencies(self) -> dict[unique_id, 'BaseOperation']:
        """Gets the dependencies of the operation."""
        return self._dependencies

    @property
    def parent_operation(self) -> 'BaseOperation':
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
    def is_ready(self) -> bool:
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
        for child in self._child_operations.values():
            if not child.is_complete() and not child.concurrent:
                self._is_ready = False

    async def _prepare_action_for_exec(self):
        """
        Prepare the action for execution.
        """
        try:
            if isinstance(self._action, str):
                code = self._action
                self._action = self._execute_code_action(code)
                self.add_log_entry(f"[CODE] {code}")
            elif callable(self._action):
                if isinstance(self._action, types.MethodType):
                    self._action = self._action
                else:
                    t_action = self._action
                    self._action = self._execute_callable_action(t_action)
        except Exception as e:
            self._handle_error(e)

    def _execute_code_action(self, code) -> callable:
        def action():
            exec(code, {}, self.result_output)

        return action

    def _execute_callable_action(self, t_action) -> callable:
        def action():
            t_action()

        return action

    async def start(self):
        """
        Start the operation and all child operations.
        """
        try:
            if self._child_operations is not None:
                await self._start_child_operations()
            self._status = "started"
        except Exception as e:
            self._handle_error(e)

    async def execute(self):
        """
        Execute the operation and all child operations.
        """
        try:
            if self._child_operations is not None:
                await self.execute_child_operations()
            await self._prepare_action_for_exec()
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
                if op.action is not None:
                    tasks.append(op.execute_action())

        if self._concurrent and tasks and len(tasks) > 0:
            await asyncio.gather(*tasks)
        elif not self._concurrent and tasks and len(tasks) > 0:
            for task in tasks:
                await task
                self.add_log_entry(f"[RESULT] {self.result_output}")

    async def execute_action(self):
        """
        Execute the action associated with the operation.
        """
        try:
            if self._is_cpu_bound:
                with ProcessPoolExecutor() as executor:
                    self._status = "running"
                    self.add_log_entry(f"[RUN] {self.name}: CPU-bound Operation")
                    await asyncio.get_event_loop().run_in_executor(executor, self._action)
                    self.result_output = await self._workspace.add_user_variable(name=f"[RESULT] {self._name}",
                                                                                 value=self.result_output,
                                                                                 memory_id=f'result_{self._unique_id}')
                    self.add_log_entry(f"[RESULT] {self.result_output}")
            else:
                if self._action is not None:
                    if callable(self._action):
                        self._status = "running"
                        if asyncio.iscoroutinefunction(self._action):
                            self.add_log_entry(f"[RUN - ASYNC] {self._name}")
                            await self._action()
                            self.add_log_entry(f"[RESULT] {self.result_output}")
                            self.result_output = await self._workspace.add_user_variable(name=f"[RESULT] {self._name}",
                                                                                         value=self.result_output,
                                                                                         memory_id=
                                                                                         f'result_{self._unique_id}')
                        else:
                            self.add_log_entry(f"[RUN] {self._name}")
                            self._action()
                            self.add_log_entry(f"[RESULT] {self.result_output}")
                            self.result_output = await self._workspace.add_user_variable(name=f"[RESULT] {self._name}",
                                                                                         value=self.result_output,
                                                                                         memory_id=
                                                                                         f'result_{self._unique_id}')
                else:
                    self._handle_error(Exception("No action provided for operation"))
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

    async def add_child_operation(self, operation, dependencies: dict[Any, 'BaseOperation'] = None):
        """Add a child operation to the current operation.

        Args:
            operation: The child operation to be added.
            dependencies (dict, optional): List of operation names that the child operation depends on.
                                                Defaults to None.
        """
        if isinstance(operation, dict):
            # Convert dictionary to BaseOperation instance
            self._logger.info(f"Converting dictionary to BaseOperation instance")
            _file_dir = os.path.join(self._config.BASE_DIR, self._config.WORKSPACE_NAME,
                                     self._config.WORKSPACE_OPERATIONS_DIR)
            operation = await BaseOperation.from_dict(data=operation, parent_operation=self, file_dir=_file_dir)

        if not isinstance(operation, BaseOperation):
            self._handle_error("operation must be an instance of BaseOperation")
            return

        if dependencies is not None:
            self._dependencies[operation.unique_id] = dependencies.get(operation.unique_id)

        if not isinstance(operation.parent_operation, BaseOperation):
            operation.parent_operation = self

        if self._child_operations is None:
            self._child_operations = dict[BaseOperation.runtime_id, 'BaseOperation']()
        if operation.runtime_id not in self._child_operations.keys():
            self._child_operations[operation.runtime_id] = operation

        self.add_log_entry(f"[CHILD] (added) {operation.name}")

    async def link_child_operation(self, child_operation: 'BaseOperation',
                                   dependencies: dict[unique_id, 'BaseOperation'] = None) -> bool:
        """
        Link a child operation to the current operation.

        Args:
            child_operation (BaseOperation): The child operation to be linked.
            dependencies (dict[unique_id, BaseOperation]): The dependencies of the child operation.

        Returns:
            bool: True if the operation was successfully linked, False otherwise.
        """
        if not isinstance(child_operation, BaseOperation):
            self._handle_error("operation must be an instance of BaseOperation")
            return False

        if not isinstance(dependencies, dict):
            dependencies = dict[BaseOperation.unique_id, 'BaseOperation']()

        if child_operation.runtime_id not in self._child_operations.keys():
            if self._child_operations is None:
                self._child_operations = dict[BaseOperation.runtime_id, 'BaseOperation']()
            self._child_operations[child_operation.runtime_id] = child_operation
        else:
            self.add_log_entry(f"[CHILD] (runtime_id already exists) {child_operation.name} - doing nothing")
            return True

        if self._dependencies is not None:
            if child_operation.unique_id not in self._dependencies and dependencies.get(child_operation.unique_id):
                self._dependencies[child_operation.unique_id] = dependencies.get(child_operation.unique_id)

        child_operation.parent_operation = self
        self.add_log_entry(f"[CHILD] (linked) {child_operation.name}")
        return True

    def remove_child_operation(self, operation: 'BaseOperation'):
        """
        Remove a child operation from the current operation.

        Args:
            operation (BaseOperation): The child operation to be removed.
        """
        if not isinstance(operation, BaseOperation):
            self._handle_error("operation must be an instance of BaseOperation")
            return

        operation.parent_operation = None
        del self._child_operations[operation.runtime_id]
        if operation.unique_id in self._dependencies.keys():
            del self._dependencies[operation.unique_id]
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
        tasks = [op.start() for op in self._child_operations.values()]
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
                await self._run_operations(self._child_operations.values())
        else:
            execution_order = self._determine_execution_order()
            await self._run_operations(execution_order)

    async def _pause_child_operations(self):
        """
        Pause all child operations.
        """
        tasks = [op.pause(True) for op in self._child_operations.values()]
        await asyncio.gather(*tasks)

    async def _resume_child_operations(self):
        """
        Resume all child operations.
        """
        tasks = [op.resume() for op in self._child_operations.values()]
        await asyncio.gather(*tasks)

    async def _stop_child_operations(self):
        """
        Stop all child operations.
        """
        tasks = [op.stop() for op in self._child_operations.values()]
        await asyncio.gather(*tasks)

    async def _reset_child_operations(self):
        """
        Reset all child operations.
        """
        tasks = [op.reset() for op in self._child_operations.values()]
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
        while len(processed) < len(self._child_operations.keys()):
            for op in self._child_operations.values():
                if op.name not in processed and all(dep in processed for dep in self._dependencies.get(op.name, [])):
                    execution_order.append(op)
                    processed.add(op.name)
        return execution_order

    def pack_as_local_reference(self) -> dict:
        """Provide a reference to the unique_id, name, and version of the operation."""
        return {
            'unique_id': self._unique_id,
            'version': self._version,
            'name': self._name,
        }

    def _pack_for_save(self) -> dict:
        """Provide a dictionary representation of the operation."""

        _child_operations = None
        if self._child_operations is not None:
            _child_operations = [child.pack_as_local_reference() for child in self._child_operations.values()]

        return {
            'unique_id': self._unique_id,
            'version': self._version,
            'name': self._name,
            'action': self.action_serializable(),
            'persistent': self._persistent,
            'concurrent': self._concurrent,
            'is_cpu_bound': self._is_cpu_bound,
            'dependencies': self._dependencies if self._dependencies else None,
            'parent_operation': self._parent_operation.pack_as_local_reference() if self._parent_operation else None,
            'child_operations': _child_operations if _child_operations else None,
        }

    async def save_operation_in_workspace(self, overwrite: bool = False):
        """
        Save the BaseOperation object to disk.

        Args:
            overwrite (bool, optional): Whether to overwrite the existing operation file. Defaults to False.
        """

        file_ext = f".json"
        stripped_state = self._pack_for_save()

        dir_path = (f"{self._config.BASE_DIR}/{self._config.WORKSPACE_NAME}/"
                    f"{self._config.WORKSPACE_OPERATIONS_DIR}")
        os.makedirs(dir_path, exist_ok=True)

        # Generate a unique name for the operation file
        name = f"{self._name}_{self.short_id}"
        if self._version > 0:
            name = f"{name}_{self.short_id}-{self._version}"

        if self._version == 0 and os.path.exists(f"{dir_path}/{name}{file_ext}"):
            if not overwrite:
                # Find the next available operation version
                self._version = 1
                while True:
                    name = f"{self._name}_{self.short_id}-{self._version}"
                    if not os.path.exists(f"{dir_path}/{name}{file_ext}"):
                        break
                    self._version += 1

        file_path = f"{dir_path}/{name}{file_ext}"

        # Save the operation
        async with aiofiles.open(file_path, 'w') as file:
            await file.write(json.dumps(stripped_state))

    @staticmethod
    async def load_from_disk(file_path: str,
                             operation_group: dict[str, 'BaseOperation']) -> 'BaseOperation':
        """Load a BaseOperation object from disk."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        async with aiofiles.open(file_path, 'r') as file:
            try:
                data = await file.read()
                state = json.loads(data)
            except json.JSONDecodeError as e:
                raise json.JSONDecodeError(f"Failed to decode JSON from file: {file_path}", data, e.pos) from e
            except Exception as e:
                raise e

            # Ensure the loaded state is a dictionary
            if not isinstance(state, dict):
                raise TypeError("Loaded data must be a dictionary")

            # Create a BaseOperation instance from the state
            operation = await BaseOperation.from_dict(data=state, file_dir=os.path.dirname(file_path))

            if operation.runtime_id not in operation_group.keys():
                operation_group[operation.runtime_id] = operation
            return operation

    @staticmethod
    async def load_operation_group(file_path: str, operation_group: dict[runtime_id, 'BaseOperation'],
                                   iterate_child_operations: bool = True) -> dict[runtime_id, 'BaseOperation']:
        """Load a group of operations from disk."""

        processed_operations = set()  # Track processed operations to avoid duplicates

        async def load_and_process_operation(path, group):
            if not os.path.exists(path):
                raise FileNotFoundError(f"File not found: {path}")

            operation = await BaseOperation.load_from_disk(path, group)
            processed_operations.add(operation.runtime_id)

            parent = operation._parent_operation
            if isinstance(parent, dict):
                parent_id = parent['unique_id']
                if parent_id not in group.values().unique_id:
                    parent_file_path = BaseOperation._construct_file_path(file_dir, parent)
                    if os.path.exists(parent_file_path):
                        parent_operation = await load_and_process_operation(parent_file_path, group)
                        operation._parent_operation = parent_operation
                        group[parent_operation.runtime_id] = parent_operation
                    else:
                        raise FileNotFoundError(f"Parent operation file not found: {parent_file_path}")
                else:
                    # Find the instance of the parent operation in the group
                    for op in group.values():
                        if op.unique_id == parent_id:
                            operation._parent_operation = op
                            break

            if operation._child_operations and iterate_child_operations:
                if isinstance(operation._child_operations, list):
                    children = operation._child_operations
                    for child in children:
                        if isinstance(child, dict):
                            child_id = child['unique_id']
                            if child_id not in group.values().unique_id:
                                child_file_path = BaseOperation._construct_file_path(file_dir, child)
                                if os.path.exists(child_file_path):
                                    child_operation = await load_and_process_operation(child_file_path, group)
                                    await operation.add_child_operation(child_operation)
                                    await operation.link_child_operation(child_operation)
                                    group[child_operation.runtime_id] = child_operation
                                else:
                                    raise FileNotFoundError(f"Child operation file not found: {child_file_path}")

            return operation

        file_dir = os.path.dirname(file_path)
        if not os.path.exists(file_dir):
            raise FileNotFoundError(f"Directory not found: {file_dir}")

        root_operation = await load_and_process_operation(file_path, operation_group)
        operation_group[root_operation.runtime_id] = root_operation

        return operation_group

    @staticmethod
    def _construct_file_path(base_dir, operation_ref):
        """Helper method to construct file path for an operation reference."""
        name = operation_ref['name']
        short_id = operation_ref['unique_id'][:4]
        version = operation_ref['version']
        file_name = f"{name}_{short_id}.json" if version == 0 else f"{name}_{short_id}-{version}.json"
        return os.path.join(base_dir, file_name)

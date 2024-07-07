"""
BaseOperation Module

An Abstract Base Class that defines a common interface for all operations.

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
import os.path
import uuid
from abc import ABC
from typing import Tuple, final

from .control import start_operation, pause_operation, resume_operation, stop_operation, reset_operation
from .execution import execute_operation, execute_inherited_operations
from .progress import update_progress
from .inheritance import (add_child_operation, link_child_operation, remove_child_operation,
                          start_child_operations, pause_child_operations, resume_child_operations,
                          stop_child_operations, reset_child_operations)
from .workspace import save_operation_in_workspace, load_from_disk, load_operation_group, from_dict


class BaseOperation(ABC):
    """
    An Abstract Base Class that defines a common interface for all operations. The BaseOperation class provides a set
    of properties and methods that all operations must implement. Operations are the building blocks of the Research
    Analytics Suite (RAS) and are used to perform tasks on data. They can be executed independently or chained
    together to form complex workflows. It also includes functionality for managing child operations, dependencies,
    and logging. The BaseOperation class is designed to be subclassed by concrete Operation classes that implement
    specific functionality.

    Lifecycle of an Operation:
        1. Initialization       [methods: __init__, initialize_operation]
            - The operation is created with a unique ID and a name.
            - The action to be performed is defined.
            - The operation is linked to a workspace, logger, configuration, and operation control instance.
            - The operation is linked to a parent operation and any child operations.
        2. Execution            [methods: start, execute]
            - The operation is started, and any child operations are started.
            - The action is prepared for execution and any dependencies are resolved.
            - The action is executed.
        3. Completion           [methods: get_result]
            - The operation is marked as complete.
            - The result of the operation is stored within a user variable in the active workspace.
            - The operation logs are updated with the result.

    Brief Attribute Overview:
            (refer to property methods and docstrings for more details)
        name (str): The name of the operation.
        version (str): The version of the operation.
        description (str): The description of the operation.
        category_id (int): The category ID of the operation.
        author (str): The author of the operation.
        github (str): The GitHub username of the operation author.
        email (str): The email of the operation author.
        unique_id (str): The unique ID of the operation.
        action (callable): The action to be executed by the operation.
        task (asyncio.Task): The task associated with the operation.
        required_inputs (dict): The input requirements of the operation (e.g., memory slots required).
        memory_inputs (MemoryInput): Memory input slots associated with the operation.
        memory_outputs (MemoryOutput): Memory output slots associated with the operation.
        parent_operation (BaseOperation): The parent operation.
        inheritance (dict[str, BaseOperation]): The child operations.
        is_loop (bool): Whether the operation should run as a loop.
        is_cpu_bound (bool): Whether the operation is CPU-bound.
        parallel (bool): Whether child operations should run in parallel or sequentially.
        is_ready (bool): Whether the operation is ready to be executed.
        status (str): The status of the operation.
        progress (int): The progress of the operation.
        operation_logs (List[str]): The logs of the operation.
    """
    _lock = asyncio.Lock()
    _GENERATED_ID = None

    def __init__(self, *args, **kwargs):
        """
        Initialize the operation instance. Refer to the initialize_operation method for setup and the properties for
        details on the operation attributes.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
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
            self._version = None
            self._description = None
            self._category_id = None
            self._author = None
            self._github = None
            self._email = None

            self._unique_id = None
            self._action = None
            self._task = None

            self._action_callable = None

            self._required_inputs: dict[str, type] = {}
            self.memory_inputs = None
            self.memory_outputs = None

            self._parent_operation = None
            self._inheritance: dict[BaseOperation.runtime_id, 'BaseOperation'] = {}

            self._is_loop = None
            self._is_cpu_bound = None
            self._parallel = None

            self._is_ready = None
            self._status = None
            self._progress = None

            self.operation_logs = []

            self._initialized = False

    @final
    def __setstate__(self, state):
        """
        Set the state of the operation.

        Args:
            state: The state of the operation.
        """
        self.__dict__.update(state)

    async def initialize_operation(self):
        """Initialize any resources or setup required for the operation before it starts."""
        if hasattr(self, '_initialized') and not self._initialized:
            async with BaseOperation._lock:
                if not self._initialized:

                    from research_analytics_suite.data_engine.Workspace import Workspace
                    self._workspace = Workspace()

                    from research_analytics_suite.utils.CustomLogger import CustomLogger
                    self._logger = CustomLogger()

                    from research_analytics_suite.utils.Config import Config
                    self._config = Config()

                    from research_analytics_suite.operation_manager.control.OperationControl import OperationControl
                    self._operation_control = OperationControl()

                    self._pause_event = asyncio.Event()
                    self._pause_event.set()
                    self._gui_module = None

                    self._name = self.temp_kwargs.get('name', "[missing name]")
                    self._version = self.temp_kwargs.get('version', "0.0.1")
                    self._description = self.temp_kwargs.get('description', "[missing description]")
                    self._category_id = self.temp_kwargs.get('category_id', 0)
                    self._author = self.temp_kwargs.get('author', "[missing author]")
                    self._github = self.temp_kwargs.get('github', "[missing github]")
                    self._email = self.temp_kwargs.get('email', "[missing email]")

                    self._unique_id = self.temp_kwargs.get('unique_id', None)
                    if self._unique_id is None:
                        self._unique_id = f"{self._github}_{self._name}_{self._version}"
                    self._action = self.temp_kwargs.get('action')
                    self._task = None

                    self._action_callable = None

                    self._required_inputs: dict[str, type] = self.temp_kwargs.get(
                        'required_inputs', dict[str, type]())
                    from research_analytics_suite.operation_manager.operations.core.memory import MemoryInput
                    self.memory_inputs = MemoryInput(name=f"{self.name}_input")
                    from research_analytics_suite.operation_manager.operations.core.memory import MemoryOutput
                    self.memory_outputs = MemoryOutput(name=f"{self.name}_output")

                    self._parent_operation = self.temp_kwargs.get('parent_operation', None)

                    _file_dir = os.path.normpath(os.path.join(
                        self._config.BASE_DIR, 'workspaces', self._config.WORKSPACE_NAME,
                        self._config.WORKSPACE_OPERATIONS_DIR))

                    if self._inheritance is not None:
                        for u_id, child in enumerate(self._inheritance):

                            # Convert dictionary to BaseOperation instance
                            if isinstance(child, dict):
                                await self.link_child_operation(
                                    await BaseOperation.from_dict(data=child, file_dir=_file_dir,
                                                                  parent_operation=self))

                            # Set the parent operation of the child operation
                            if self._inheritance[u_id].parent_operation is None:
                                self._inheritance[u_id].parent_operation = self

                    self._is_loop = self.temp_kwargs.get('is_loop', False)
                    self._is_cpu_bound = self.temp_kwargs.get('is_cpu_bound', False)
                    self._parallel = self.temp_kwargs.get('parallel', False)

                    self._is_ready = False
                    self._status = "idle"
                    self._progress = 0

                    self.operation_logs = self.temp_kwargs.get('operation_logs', [])

                    self.add_log_entry(f"[INIT] {self._name}")
                    self._initialized = True
                    await self._operation_control.operation_manager.add_initialized_operation(self)

                    # Clean up temporary attributes
                    delattr(self, 'temp_args')
                    delattr(self, 'temp_kwargs')

    async def start(self):
        """
        Start the operation and all child operations.
        """
        await start_operation(self)

    async def pause(self, child_operations=False):
        """
        Pause the operation and all child operations, if applicable.

        Args:
            child_operations (bool, optional): Whether to pause child operations. Defaults to False.
        """
        await pause_operation(self, child_operations)

    async def resume(self, child_operations=False):
        """
        Resume the operation and all child operations, if applicable.

        Args:
            child_operations (bool, optional): Whether to resume child operations. Defaults to False.
        """
        await resume_operation(self, child_operations)

    async def stop(self, child_operations=False):
        """
        Stop the operation and all child operations, if applicable.

        Args:
            child_operations (bool, optional): Whether to stop child operations. Defaults to False.
        """
        await stop_operation(self, child_operations)

    async def restart(self, child_operations=False):
        """
        Restart the operation and all child operations, if applicable.

        Args:
            child_operations (bool, optional): Whether to restart child operations. Defaults to False.
        """
        await self.reset(child_operations)

        self.is_ready = True
        await self.execute()

    async def reset(self, child_operations=False):
        """
        Reset the operation and all child operations, if applicable.

        Args:
            child_operations (bool, optional): Whether to reset child operations. Defaults to False.
        """
        await reset_operation(self, child_operations)

    async def execute(self):
        """
        Execute the operation and all child operations.
        """
        await execute_operation(self)

    async def update_progress(self):
        """
        Update the progress of the operation.
        """
        await update_progress(self)

    @final
    async def add_child_operation(self, operation):
        """
        Add a child operation to the current operation.

        Args:
            operation: The child operation to be added.
        """
        await add_child_operation(self, operation)

    @final
    async def link_child_operation(self, child_operation):
        """
        Link a child operation to the current operation.

        Args:
            child_operation: The child operation to be linked.
        """
        await link_child_operation(self, child_operation)

    @final
    async def remove_child_operation(self, operation):
        """
        Remove a child operation from the current operation.

        Args:
            operation: The child operation to be removed.
        """
        await remove_child_operation(self, operation)

    async def start_child_operations(self):
        """
        Start all child operations.
        """
        await start_child_operations(self)

    async def pause_child_operations(self):
        """
        Pause all child operations.
        """
        await pause_child_operations(self)

    async def resume_child_operations(self):
        """
        Resume all child operations.
        """
        await resume_child_operations(self)

    async def stop_child_operations(self):
        """
        Stop all child operations.
        """
        await stop_child_operations(self)

    async def reset_child_operations(self):
        """
        Reset all child operations.
        """
        await reset_child_operations(self)

    async def execute_child_operations(self):
        """
        Execute all child operations.
        """
        await execute_inherited_operations(self)

    @final
    async def add_memory_input_slot(self, memory_slot):
        """Add a memory input slot."""
        self.memory_inputs.add_slot(memory_slot)

    @final
    async def remove_memory_input_slot(self, memory_id):
        """Remove a memory input slot by its ID."""
        await self.memory_inputs.remove_slot(memory_id)

    @final
    def get_memory_input_slot(self, memory_id):
        """Get a memory input slot by its ID."""
        return self.memory_inputs.get_slot(memory_id)

    @final
    def get_memory_input_slot_data(self, memory_id):
        """Get the data of a memory input slot by its ID."""
        return self.memory_inputs.get_slot_data(memory_id)

    @final
    async def add_memory_output_slot(self, memory_slot):
        """Add a memory output slot."""
        self.memory_outputs.add_slot(memory_slot)

    @final
    async def remove_memory_output_slot(self, memory_id):
        """Remove a memory output slot by its ID."""
        await self.memory_outputs.remove_slot(memory_id)

    @final
    def get_memory_output_slot(self, memory_id):
        """Get a memory output slot by its ID."""
        return self.memory_outputs.get_slot(memory_id)

    @final
    def get_memory_output_slot_data(self, memory_id):
        """Get the data of a memory output slot by its ID."""
        return self.memory_outputs.get_slot_data(memory_id)

    async def validate_memory_inputs(self):
        """Validate all memory inputs."""
        if self.memory_inputs is not None:
            await self.memory_inputs.validate_inputs()

    async def validate_memory_outputs(self):
        """Validate all memory outputs."""
        if self.memory_outputs is not None:
            await self.memory_outputs.validate_results()

    @final
    async def get_results_from_memory(self) -> dict:
        """
        Retrieve the results of the operation from the workspace.

        Returns:
            dict[name, value]: The name of the variable and its value.
        """
        return await self.memory_outputs.aggregate_results()

    async def clear_memory_inputs(self):
        """Clear all memory inputs."""
        await self.memory_inputs.clear_slots()

    async def clear_memory_outputs(self):
        """Clear all memory outputs."""
        await self.memory_outputs.clear_slots()

    async def save_operation_in_workspace(self, overwrite: bool = False):
        """
        Save the BaseOperation object to disk.

        Args:
            overwrite (bool, optional): Whether to overwrite the existing operation file. Defaults to False.
        """
        await save_operation_in_workspace(self, overwrite)

    @staticmethod
    async def load_from_disk(file_path: str, operation_group: dict[str, 'BaseOperation']) -> 'BaseOperation':
        """
        Load a BaseOperation object from disk.

        Args:
            file_path (str): The path to the file to load.
            operation_group (dict[str, BaseOperation]): The group of operations to which the loaded operation belongs.

        Returns:
            BaseOperation: The loaded operation.
        """
        return await load_from_disk(file_path, operation_group)

    @staticmethod
    async def load_operation_group(file_path: str,
                                   operation_group: dict = None,
                                   iterate_child_operations: bool = True) -> dict:
        """
        Load a group of operations from disk.

        Args:
            file_path (str): The path to the file to load.
            operation_group (dict, optional): The group of operations to which the loaded operations belong.
                                               Defaults to None.
            iterate_child_operations (bool, optional): Whether to iterate through child operations. Defaults to True.

        Returns:
            dict: The loaded operation group.
        """
        return await load_operation_group(file_path, operation_group, iterate_child_operations)

    @staticmethod
    async def from_dict(data: dict, file_dir, parent_operation: 'BaseOperation' = None) -> 'BaseOperation':
        """
        Create a BaseOperation instance from a dictionary.

        Args:
            data (dict): The dictionary containing the operation data.
            file_dir: The directory where the operation file is located.
            parent_operation (BaseOperation, optional): The parent operation. Defaults to None.

        Returns:
            BaseOperation: The created operation instance.
        """
        return await from_dict(data, file_dir, parent_operation)

    @property
    def config(self):
        """Gets the configuration instance."""
        return self._config

    @property
    def pause_event(self):
        """Gets the pause event."""
        return self._pause_event

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
        return f"{self._GENERATED_ID}"

    @property
    def name(self) -> str:
        """Gets the name of the operation."""
        return self._name

    @name.setter
    def name(self, value: str):
        """Sets the name of the operation."""
        if not isinstance(value, str):
            self.handle_error("\'name\' property must be a string")
        self._name = value

    @property
    def version(self) -> str:
        """Gets the version of the operation."""
        return self._version

    @version.setter
    def version(self, value: str):
        """Sets the version of the operation."""
        if not isinstance(value, str):
            self.handle_error("\'version\' property must be a string")
        self._version = value

    @property
    def description(self) -> str:
        """Gets the description of the operation."""
        return self._description

    @description.setter
    def description(self, value: str):
        """Sets the description of the operation."""
        if not isinstance(value, str):
            self.handle_error("\'description\' property must be a string")
        self._description = value

    @property
    def category_id(self) -> int:
        """Gets the category ID of the operation."""
        return self._category_id

    @property
    def author(self) -> str:
        """Gets the author of the operation."""
        return self._author

    @author.setter
    def author(self, value: str):
        """Sets the author of the operation."""
        if not isinstance(value, str):
            self.handle_error("\'author\' property must be a string")
        self._author = value

    @property
    def github(self) -> str:
        """Gets the GitHub username of the operation author."""
        return self._github

    @github.setter
    def github(self, value: str):
        """Sets the GitHub username of the operation author."""
        if not isinstance(value, str):
            self.handle_error("\'github\' property must be a string")

        if value.startswith("@"):
            value = value[1:]

        self._github = value

    @property
    def email(self) -> str:
        """Gets the email of the operation author."""
        return self._email

    @email.setter
    def email(self, value: str):
        """Sets the email of the operation author."""
        if not isinstance(value, str):
            self.handle_error("\'email\' property must be a string")

        # Ensure email is in the correct format
        if "@" not in value or "." not in value or len(value) < 5:
            self.handle_error("\'email\' property must be in the format")
            self._email = "[unknown_email]"
        else:
            self._email = value

    @property
    def action(self):
        """Gets the action to be executed by the operation."""
        return self._action

    @action.setter
    def action(self, value):
        """Sets the action to be executed by the operation."""
        self._action = value
        self._action_callable = None

    @property
    def action_callable(self) -> callable:
        """Gets the callable action to be executed by the operation."""
        return self._action_callable()

    @action_callable.setter
    def action_callable(self, value: callable):
        """Sets the callable action to be executed by the operation."""
        self._action_callable = value

    @property
    def task(self):
        """Gets the task associated with the operation."""
        return self._task

    @task.setter
    def task(self, value: asyncio.Task):
        """Sets the task associated with the operation."""
        if not isinstance(value, asyncio.Task):
            self.handle_error("\'task\' property must be an asyncio.Task")
            return
        self._task = value

    @property
    def required_inputs(self) -> dict[str, type]:
        """Gets the input requirements of the operation."""
        return self._required_inputs

    @required_inputs.setter
    def required_inputs(self, value: tuple[str, type]):
        """Adds an input requirement to the operation."""
        if not isinstance(value, tuple):
            self.handle_error("\'required_inputs\' property must be a tuple[str, type]")
            return

        self._required_inputs[value[0]] = value[1]

    @property
    def parent_operation(self) -> 'BaseOperation':
        """Gets the parent operation."""
        return self._parent_operation

    @parent_operation.setter
    def parent_operation(self, value):
        """Sets the parent operation."""
        if value is not None and not isinstance(value, BaseOperation):
            self.handle_error("\'parent_operation\' must be an instance of Operation")
        self._parent_operation = value

    @property
    def inheritance(self) -> dict[runtime_id, 'BaseOperation']:
        """Gets the list of child operations."""
        return self._inheritance

    @property
    def is_loop(self) -> bool:
        """Gets whether the operation should run in a loop."""
        return self._is_loop

    @is_loop.setter
    def is_loop(self, value: bool):
        """Sets whether the operation should run in a loop."""
        if not isinstance(value, bool):
            self.handle_error("\'is_loop\' property must be a boolean")
        self._is_loop = value

    @property
    def is_cpu_bound(self) -> bool:
        """Gets whether the operation is CPU-bound."""
        return self._is_cpu_bound

    @is_cpu_bound.setter
    def is_cpu_bound(self, value: bool):
        """Sets whether the operation is CPU-bound."""
        if not isinstance(value, bool):
            self.handle_error("\'is_cpu_bound\' property must be a boolean")
        self._is_cpu_bound = value

    @property
    def parallel(self) -> bool:
        """Gets whether inherited operations should run in parallel or sequentially."""
        return self._parallel

    @parallel.setter
    def parallel(self, value: bool):
        """Sets whether inherited operations should run in parallel or sequentially."""
        if not isinstance(value, bool):
            self.handle_error("\'parallel\' property must be a boolean")
        self._parallel = value

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
            self.handle_error("\'is_ready\' property must be a boolean")
        if not value:
            self._is_ready = False
            return

        for child in self._inheritance.values():
            if not child.is_complete and not child.parallel:
                self._is_ready = False
                return

        self._is_ready = True

    @property
    def status(self) -> str:
        """Gets the status of the operation."""
        return self._status

    @status.setter
    def status(self, value: str):
        """Sets the status of the operation."""
        valid_statuses = ["idle", "started", "waiting", "running", "paused", "stopped", "completed", "error"]
        if value not in valid_statuses:
            self.handle_error(f"Invalid status: {value}")
            return
        self._status = value

    @property
    def progress(self) -> Tuple[int, str]:
        """Gets the progress of the operation."""
        return self._progress, self._status

    @progress.setter
    def progress(self, value: int):
        """Sets the progress of the operation."""
        if not isinstance(value, int):
            self.handle_error("\'progress\' property must be an integer")
        self._progress = value

    @property
    def gui_module(self):
        """Gets the GUI module attached to the operation."""
        return self._gui_module

    @gui_module.setter
    def gui_module(self, value):
        """Sets the GUI module attached to the operation."""
        self._gui_module = value

    @property
    def is_running(self) -> bool:
        """
        Check if the operation is currently running.
        """
        return self._status == "running"

    @property
    def is_complete(self) -> bool:
        """
        Check if the operation is complete.
        """
        return self._status == "completed"

    @property
    def is_paused(self) -> bool:
        """
        Check if the operation is currently paused.
        """
        return self._status == "paused"

    @property
    def is_stopped(self) -> bool:
        """
        Check if the operation is currently stopped.
        """
        return self._status == "stopped"

    @final
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
            self.handle_error(e)

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
            self._logger.debug(f"[{self._name}] {message}")

    def handle_error(self, e):
        """
        Handle an error that occurred during the operation.

        Args:
            e: The exception that occurred.
        """
        self._status = "error"
        # self.add_log_entry(e)

    def cleanup_operation(self):
        """
        Clean up any resources or perform any necessary teardown after the operation has completed or been stopped.
        """
        self._progress = 0
        self._status = "idle"
        self._task = None

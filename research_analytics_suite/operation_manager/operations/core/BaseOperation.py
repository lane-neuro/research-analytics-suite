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

from __future__ import annotations
import asyncio
import os.path
import uuid
from abc import ABC
from typing import Tuple, List, Dict, Optional, Union, final

from research_analytics_suite.commands import command, link_class_commands
from .control import start_operation, pause_operation, resume_operation, stop_operation, reset_operation
from .execution import execute_operation, execute_inherited_operations
from .progress import update_progress
from .inheritance import (add_child_operation, link_child_operation, remove_child_operation,
                          start_child_operations, pause_child_operations, resume_child_operations,
                          stop_child_operations, reset_child_operations)
from .workspace.WorkspaceInteraction import save_operation_in_workspace
from .workspace.FileDiskOperations import load_from_disk, load_operation_group, from_dict


@link_class_commands
class BaseOperation(ABC):
    """
    BaseOperation defines a common interface for all operations in the Research Analytics Suite (RAS). This class
    provides properties and methods that all operations must implement. Operations are the building blocks of the RAS
    and can perform tasks on data either independently or as part of complex workflows by chaining multiple operations
    together. This class also includes functionality for managing child operations, dependencies, and logging.

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

    Attributes:
        name (str): The name of the operation.
        version (str): The version of the operation.
        description (str): The description of the operation.
        category_id (int): The category ID of the operation.
        author (str): The author of the operation.
        github (str): The GitHub username of the operation author.
        email (str): The email of the operation author.
        unique_id (str): The unique ID of the operation.
        action (Callable): The action to be executed by the operation.
        task (Optional[asyncio.Task]): The task associated with the operation.
        required_inputs (Dict[str, type]): The input requirements of the operation (e.g., memory slots required).
        memory_inputs (set): Memory input slots associated with the operation.
        memory_outputs (set): Memory output slots associated with the operation.
        parent_operation (Optional[BaseOperation]): The parent operation.
        inheritance (List[BaseOperation]): The child operations.
        is_loop (bool): Whether the operation manages its own internal loop. Operations with this flag set to True
            must implement their own loop logic (e.g., while self.is_loop: ...) and will remain in 'running'
            status until explicitly stopped. Setting is_loop to False (via cleanup or stop) breaks the loop.
        is_cpu_bound (bool): Whether the operation is CPU-bound.
        is_gpu_bound (bool): Whether the operation is GPU-bound.
        parallel (bool): Whether child operations should run in parallel or sequentially.
        is_ready (bool): Whether the operation is ready to be executed.
        status (str): The status of the operation.
        progress (int): The progress of the operation.
        operation_logs (List[str]): The logs of the operation.
    """
    _GENERATED_ID = None

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        for attr, value in cls.__dict__.items():
            if not attr.startswith("__") and not callable(value):
                # Check if the attribute is a property with a setter
                if isinstance(getattr(cls, attr, None), property) and getattr(cls, attr).fset is not None:
                    try:
                        setattr(instance, attr, value)
                    except AttributeError:
                        pass
                elif not isinstance(getattr(cls, attr, None), property):
                    try:
                        setattr(instance, attr, value)
                    except AttributeError:
                        pass
        return instance

    def __init__(self, *args, **kwargs):
        """Initialize the operation instance."""
        if not hasattr(self, '_initialized'):
            from research_analytics_suite.data_engine.Workspace import Workspace
            from research_analytics_suite.utils.CustomLogger import CustomLogger
            from research_analytics_suite.utils.Config import Config
            from research_analytics_suite.operation_manager.control.OperationControl import OperationControl

            self._workspace = Workspace()
            self._logger = CustomLogger()
            self._config = Config()
            self._operation_control = OperationControl()
            self._pause_event = asyncio.Event()
            self._pause_event.set()

            self._gui_module = None

            self._GENERATED_ID = uuid.uuid4()
            self._action_callable = None
            self._task = None
            self._status = "idle"
            self._progress = 0
            self._is_ready = False

            self.operation_logs = []

            from research_analytics_suite.operation_manager.operations.core.OperationAttributes import \
                OperationAttributes

            # If args is empty or not passed, initialize OperationAttributes with kwargs
            if not args or len(args) == 0:
                if kwargs.get('action', None) is None:
                    self._logger.warning(
                        f"Operation [{kwargs.get('name', '[Unnamed Operation]')}] must have an action to execute.")
                    kwargs['action'] = self.execute
                self.attributes = OperationAttributes(*args, **kwargs)

            # If the first argument is an instance of OperationAttributes, use it directly
            elif isinstance(args[0], OperationAttributes) and hasattr(args[0], 'unique_id'):
                self.attributes = args[0]

            # Otherwise, pass both args and kwargs to OperationAttributes
            else:
                self.attributes = OperationAttributes(*args, **kwargs)

            # Initialize the attributes asynchronously
            if asyncio.get_event_loop().is_running():
                asyncio.create_task(self.attributes.initialize())
            else:
                asyncio.run(self.attributes.initialize())

            self._initialized = False

    async def initialize_operation(self):
        """Initialize any resources or setup required for the operation before it starts."""
        if self._initialized:
            return

        await self._initialize_child_operations()

        self.is_ready = False
        self.status = "idle"
        self.add_log_entry(f"[INIT] {self.name}")
        self._initialized = True

    async def _initialize_child_operations(self):
        """Initialize child operations."""
        _file_dir = os.path.normpath(os.path.join(
            self._config.BASE_DIR, 'workspaces', self._config.WORKSPACE_NAME,
            self._config.WORKSPACE_OPERATIONS_DIR))

        if self.inheritance:
            for u_id, child in enumerate(self.inheritance):
                if isinstance(child, dict):
                    await self.link_child_operation(
                        await BaseOperation.from_dict(data=child, file_dir=_file_dir, parent_operation=self))
                if self.inheritance[u_id].parent_operation is None:
                    self.inheritance[u_id].parent_operation = self

    @final
    def __setstate__(self, state):
        """Set the state of the operation.

        Args:
            state: The state of the operation.
        """
        self.__dict__.update(state)

    async def start_operation(self):
        """Start the operation and all child operations."""
        await start_operation(self)

    async def pause(self, child_operations: bool = False):
        """Pause the operation and all child operations, if applicable.

        Args:
            child_operations (bool, optional): Whether to pause child operations. Defaults to False.
        """
        await pause_operation(self, child_operations)

    async def resume(self, child_operations: bool = False):
        """Resume the operation and all child operations, if applicable.

        Args:
            child_operations (bool, optional): Whether to resume child operations. Defaults to False.
        """
        await resume_operation(self, child_operations)

    async def stop(self, child_operations: bool = False):
        """Stop the operation and all child operations, if applicable.

        Args:
            child_operations (bool, optional): Whether to stop child operations. Defaults to False.
        """
        await stop_operation(self, child_operations)

    async def restart(self, child_operations: bool = False):
        """Restart the operation and all child operations, if applicable.

        Args:
            child_operations (bool, optional): Whether to restart child operations. Defaults to False.
        """
        await self.reset(child_operations)
        self.is_ready = True
        await self.execute()

    async def reset(self, child_operations: bool = False):
        """Reset the operation and all child operations, if applicable.

        Args:
            child_operations (bool, optional): Whether to reset child operations. Defaults to False.
        """
        await reset_operation(self, child_operations)

    async def execute(self):
        """Execute the operation and all child operations."""
        await execute_operation(self)

    async def update_progress(self):
        """Update the progress of the operation."""
        await update_progress(self)

    @final
    async def add_child_operation(self, operation: BaseOperation):
        """Add a child operation to the current operation.

        Args:
            operation (BaseOperation): The child operation to be added.
        """
        await add_child_operation(self, operation)

    @final
    async def link_child_operation(self, child_operation: BaseOperation):
        """Link a child operation to the current operation.

        Args:
            child_operation (BaseOperation): The child operation to be linked.
        """
        await link_child_operation(self, child_operation)

    @final
    async def remove_child_operation(self, operation: BaseOperation):
        """Remove a child operation from the current operation.

        Args:
            operation (BaseOperation): The child operation to be removed.
        """
        await remove_child_operation(self, operation)

    async def start_child_operations(self):
        """Start all child operations."""
        await start_child_operations(self)

    async def pause_child_operations(self):
        """Pause all child operations."""
        await pause_child_operations(self)

    async def resume_child_operations(self):
        """Resume all child operations."""
        await resume_child_operations(self)

    async def stop_child_operations(self):
        """Stop all child operations."""
        await stop_child_operations(self)

    async def reset_child_operations(self):
        """Reset all child operations."""
        await reset_child_operations(self)

    async def execute_child_operations(self):
        """Execute all child operations."""
        await execute_inherited_operations(self)

    @command
    @final
    async def add_input(self, name: str, data: any = None) -> None:
        """Add a memory input slot.

        Args:
            name (str): The name of the memory slot.
            data (any, optional): The data to store in the memory slot. Defaults to None.

        """
        from research_analytics_suite.data_engine.memory.MemoryManager import MemoryManager
        memory_manager = MemoryManager()

        _new_input, _, _ = await memory_manager.create_slot(name=name, data=data, d_type=type(data))
        self.attributes.required_inputs[name] = _new_input
        self.add_log_entry(f"[MEMORY] Added input slot: {name} with data: {data}")

    @command
    @final
    async def add_output(self, name: str, data: any = None) -> None:
        """Add a memory output slot.

        Args:
            name (str): The name of the memory slot.
            data (any, optional): The data to store in the memory slot. Defaults to None.
        """
        from research_analytics_suite.data_engine.memory.MemoryManager import MemoryManager
        memory_manager = MemoryManager()

        self.attributes.outputs, _, _ = await memory_manager.create_slot(name=name, data=data, d_type=type(data))
        self.add_log_entry(f"[MEMORY] Added output slot: {name} with data: {data}")

    @final
    def _is_empty_data(self, data: any) -> bool:
        """
        Safely check if data is empty/None across all data types.

        Args:
            data: Data to check

        Returns:
            bool: True if data is considered empty, False otherwise
        """
        if data is None:
            return True

        # Check for pandas DataFrame
        if hasattr(data, 'empty'):
            return data.empty

        # Check for numpy arrays
        if hasattr(data, 'size'):
            return data.size == 0

        # Check for standard containers (list, dict, tuple, set, str)
        try:
            return len(data) == 0
        except TypeError:
            # If len() fails, it's likely a non-container type
            # Use standard truthiness for numbers, custom objects, etc.
            return not bool(data)

    @final
    def get_input(self, name: str, default: any = None) -> any:
        """
        Retrieve input data by the logical slot name.

        Args:
            name (str): The name of the required input slot (as defined in `required_inputs`).
            default (any, optional): Default value if the slot does not exist or has no data.

        Returns:
            any: The data from the memory slot or the default.
        """
        try:
            data = self.attributes.required_inputs.get(name)
            if self._is_empty_data(data):
                self._logger.warning(f"Slot name '{name}' not found in required_inputs.")
                return default

            return data if data is not None else default
        except Exception as e:
            self.handle_error(e)
            return default

    @final
    def get_inputs(self) -> dict:
        """
        Retrieve all required input values as a dictionary.

        Returns:
            dict: A mapping from logical names to memory slot data.
        """
        return self.attributes.required_inputs

    @command
    @final
    async def remove_slot(self, memory_id: str) -> None:
        """Remove a memory slot by its ID.

        Args:
            memory_id (str): The ID of the memory slot to remove.
        """
        from research_analytics_suite.data_engine.memory.MemoryManager import MemoryManager
        memory_manager = MemoryManager()

        for slot_id in self.attributes.required_inputs and self.attributes.outputs:
            if slot_id.lower() == memory_id.lower():
                if memory_id in self.attributes.required_inputs:
                    self.attributes.required_inputs.pop(memory_id)
                if memory_id in self.attributes.outputs:
                    self.attributes.outputs.pop(memory_id)
                await memory_manager.delete_slot(memory_id)
                self.add_log_entry(f"[MEMORY] Removed slot: {memory_id}")
                return

    @final
    async def get_slot_data(self, memory_id: str) -> any:
        """Get the data from a memory slot by its ID.

        Args:
            memory_id (str): The ID of the memory slot.

        Returns:
            any: The data stored in the memory slot.
        """
        from research_analytics_suite.data_engine.memory.MemoryManager import MemoryManager
        memory_manager = MemoryManager()

        for slot_id in self.attributes.required_inputs and self.attributes.outputs:
            if slot_id.lower() == memory_id.lower():
                try:
                    _data = memory_manager.slot_data(memory_id)
                    self.add_log_entry(f"[MEMORY] Retrieved data from slot: {memory_id}")
                    return _data
                except Exception as e:
                    self._logger.error(e)
                    return None
        else:
            self._logger.warning(f"No memory slot found with ID {memory_id}")
            return None

    @command
    async def validate_inputs(self) -> None:
        """Passes all memory inputs through a data check/validation."""
        from research_analytics_suite.data_engine.memory.MemoryManager import MemoryManager
        memory_manager = MemoryManager()

        _valid, _invalid = memory_manager.validate_slots(memory_ids=list(self.attributes.required_inputs.values()),
                                                         require_values=True)
        self._logger.debug(f"Valid memory slots: {_valid}; Invalid memory slots: {_invalid}")
        if _invalid and len(_invalid) > 0:
            for _id in _invalid:
                _name = memory_manager.slot_name(_id)
                _data = memory_manager.slot_data(_id)
                self._logger.warning(f"Invalid memory slot: {_name} ({_id}) with data: {_data}")
            raise ValueError("Invalid memory slots found")

    @command
    @final
    async def get_results(self) -> dict:
        """Retrieve the results of the operation from the workspace.

        Returns:
            dict: The name of the variable and its value.
        """
        return self.attributes.outputs

    @command
    async def clear_inputs(self):
        """Clear all memory inputs."""
        from research_analytics_suite.data_engine.memory.MemoryManager import MemoryManager
        memory_manager = MemoryManager()

        for memory_slot in self.attributes.required_inputs:
            _slot = memory_manager.get_slot(memory_slot)
            if _slot:
                await _slot.set_data(None)
                self.add_log_entry(f"[MEMORY] Cleared input slot: {memory_slot}")

    @command
    async def clear_outputs(self):
        """Clear all memory outputs."""
        for memory_slot in self.attributes.outputs:
            memory_slot.data = None

    async def save_in_workspace(self, overwrite: bool = False):
        """Save the BaseOperation object to disk.

        Args:
            overwrite (bool, optional): Whether to overwrite the existing operation file. Defaults to False.
        """
        await save_operation_in_workspace(self.attributes, overwrite)

    @staticmethod
    async def load_from_disk(file_path: str, operation_group: dict[str, BaseOperation]) -> BaseOperation:
        """Load a BaseOperation object from disk.

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
        """Load a group of operations from disk.

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
    async def from_dict(data: dict, file_dir, parent_operation: BaseOperation = None) -> BaseOperation:
        """Create a BaseOperation instance from a dictionary.

        Args:
            data (dict): The dictionary containing the operation data.
            file_dir: The directory where the operation file is located.
            parent_operation (BaseOperation, optional): The parent operation. Defaults to None.

        Returns:
            BaseOperation: The created operation instance.
        """
        return await from_dict(data, file_dir, parent_operation)

    @property
    def pause_event(self):
        """Gets the pause event."""
        return self._pause_event

    @property
    def initialized(self) -> bool:
        """Gets whether the operation has been initialized."""
        return self._initialized

    @property
    def attributes(self):
        """Gets the operation attributes."""
        if not hasattr(self, '_attributes'):
            from research_analytics_suite.operation_manager.operations.core.OperationAttributes import (
                OperationAttributes)
            self._attributes = OperationAttributes()

        return self._attributes

    @attributes.setter
    def attributes(self, value):
        """Sets the operation attributes."""
        self._attributes = value

    @property
    def unique_id(self) -> str:
        """Gets the unique ID of the operation."""
        return self.attributes.unique_id

    @property
    def short_id(self) -> str:
        """Gets the short unique ID of the operation."""
        return self.attributes.unique_id[:4]

    @property
    def runtime_id(self) -> str:
        """Gets the runtime ID of the operation."""
        return f"{self._GENERATED_ID}"

    @property
    def name(self) -> str:
        """Gets the name of the operation."""
        return self.attributes.name

    @name.setter
    def name(self, value: str):
        """Sets the name of the operation."""
        self.attributes.name = value

    @property
    def version(self) -> str:
        """Gets the version of the operation."""
        return self.attributes.version

    @version.setter
    def version(self, value: str):
        """Sets the version of the operation."""
        self.attributes.version = value

    @property
    def description(self) -> str:
        """Gets the description of the operation."""
        return self.attributes.description

    @description.setter
    def description(self, value: str):
        """Sets the description of the operation."""
        self.attributes.description = value

    @property
    def category_id(self) -> int:
        """Gets the category ID of the operation."""
        return self.attributes.category_id

    @category_id.setter
    def category_id(self, value: int):
        """Sets the category ID of the operation."""
        self.attributes.category_id = value

    @property
    def author(self) -> str:
        """Gets the author of the operation."""
        return self.attributes.author

    @author.setter
    def author(self, value: str):
        """Sets the author of the operation."""
        self.attributes.author = value

    @property
    def github(self) -> str:
        """Gets the GitHub username of the operation author."""
        return self.attributes.github

    @github.setter
    def github(self, value: str):
        """Sets the GitHub username of the operation author."""
        self.attributes.github = value

    @property
    def email(self) -> str:
        """Gets the email of the operation author."""
        return self.attributes.email

    @email.setter
    def email(self, value):
        """Sets the email of the operation author."""
        self.attributes.email = value

    @property
    def action(self):
        """Gets the action to be executed by the operation."""
        return self.attributes.action

    @action.setter
    def action(self, value):
        """Sets the action to be executed by the operation."""
        self.attributes.action = value
        self._action_callable = None

    @property
    def action_callable(self):
        """Gets the callable action to be executed by the operation."""
        return self._action_callable

    @action_callable.setter
    def action_callable(self, value):
        """Sets the callable action to be executed by the operation."""
        self._action_callable = value

    @property
    def task(self) -> Optional[asyncio.Task]:
        """Gets the task associated with the operation."""
        return self._task

    @task.setter
    def task(self, value: asyncio.Task):
        """Sets the task associated with the operation."""
        if not isinstance(value, asyncio.Task):
            self.handle_error(TypeError("\'task\' property must be an asyncio.Task"))
            return
        self._task = value

    @property
    def parent_operation(self):
        """Gets the parent operation."""
        return self.attributes.parent_operation

    @parent_operation.setter
    def parent_operation(self, value):
        """Sets the parent operation."""
        self.attributes.parent_operation = value

    @property
    def inheritance(self) -> list:
        """Gets the list of child operations."""
        return self.attributes.inheritance

    @inheritance.setter
    def inheritance(self, value):
        """Sets the list of child operations."""
        self.attributes.inheritance = value

    @property
    def is_loop(self) -> bool:
        """Gets whether the operation should run in a loop."""
        return self.attributes.is_loop

    @is_loop.setter
    def is_loop(self, value: bool):
        """Sets whether the operation should run in a loop."""
        self.attributes.is_loop = value

    @property
    def is_cpu_bound(self) -> bool:
        """Gets whether the operation is CPU-bound."""
        return self.attributes.is_cpu_bound

    @is_cpu_bound.setter
    def is_cpu_bound(self, value: bool):
        """Sets whether the operation is CPU-bound."""
        self.attributes.is_cpu_bound = value

    @property
    def is_gpu_bound(self) -> bool:
        """Gets whether the operation is GPU-bound."""
        return self.attributes.is_gpu_bound

    @is_gpu_bound.setter
    def is_gpu_bound(self, value: bool):
        """Sets whether the operation is GPU-bound."""
        self.attributes.is_gpu_bound = value

    @property
    def parallel(self) -> bool:
        """Gets whether inherited operations should run in parallel or sequentially."""
        return self.attributes.parallel

    @parallel.setter
    def parallel(self, value: bool):
        """Sets whether inherited operations should run in parallel or sequentially."""
        self.attributes.parallel = value

    @property
    def is_ready(self) -> bool:
        """Check if the operation is ready to be executed."""
        return self._is_ready

    @is_ready.setter
    def is_ready(self, value: bool):
        """Sets whether the operation is ready to be executed."""
        if not isinstance(value, bool):
            self.handle_error(TypeError("\'is_ready\' property must be a boolean"))
        if not value:
            self._is_ready = False
            return

        for child in self.inheritance:
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
            self.handle_error(ValueError(f"Invalid status: {value}"))
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
            self.handle_error(TypeError("\'progress\' property must be an integer"))
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
        """Check if the operation is currently running."""
        return self._status == "running"

    @property
    def is_complete(self) -> bool:
        """Check if the operation is complete."""
        return self._status == "completed"

    @property
    def is_paused(self) -> bool:
        """Check if the operation is currently paused."""
        return self._status == "paused"

    @property
    def is_stopped(self) -> bool:
        """Check if the operation is currently stopped."""
        return self._status == "stopped"

    @property
    def memory_inputs(self) -> set:
        """Get the memory input slot IDs as a set."""
        if hasattr(self, 'attributes') and self.attributes and hasattr(self.attributes, 'input_ids'):
            return set(self.attributes.input_ids.values()) if self.attributes.input_ids else set()
        return set()

    @property
    def memory_outputs(self) -> set:
        """Get the memory output slot IDs as a set."""
        if hasattr(self, 'attributes') and self.attributes and hasattr(self.attributes, 'output_ids'):
            return set(self.attributes.output_ids.values()) if self.attributes.output_ids else set()
        return set()

    @final
    def attach_gui_module(self, gui_module):
        """Attach a GUI module to the operation.

        Args:
            gui_module: The GUI module to be attached.
        """
        try:
            self._gui_module = gui_module
            self.add_log_entry(f"[GUI] Hooked module")
        except Exception as e:
            self.handle_error(e)

    def add_log_entry(self, message: Union[str, Exception]):
        """Log a message to the GUI.

        Args:
            message (Union[str, Exception]): The message to log.
        """
        self.operation_logs.insert(0, message)

        from research_analytics_suite.utils import CustomLogger
        CustomLogger().debug(f"[{self.name}] {message}")

    def handle_error(self, e: Exception):
        """Handle an error that occurred during the operation.

        Args:
            e (Exception): The exception that occurred.
        """
        from research_analytics_suite.utils import CustomLogger
        CustomLogger().error(e, self.name)

        self.add_log_entry(f"Error: {str(e)}")
        self._status = "error"

        try:
            from research_analytics_suite.gui.modules import notification_bus
            notification_bus.publish("operation_error", {
                "operation_id": self.runtime_id,
                "operation_name": self.name,
                "error_message": str(e),
                "error_type": type(e).__name__
            })
        except Exception:
            pass

    def cleanup_operation(self):
        """
        Clean up any resources or perform any necessary teardown after the operation has completed
        or been stopped.
        """
        self.is_loop = False
        self._progress = 0
        self._status = "idle"
        self._task = None

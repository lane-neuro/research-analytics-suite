"""
OperationAttributes

This module contains the OperationAttributes class, which stores and manages the attributes of an operation.

The OperationAttributes class handles:
- Operation metadata (name, version, author, etc.)
- Input/output specifications and memory slot management
- Execution settings (loop behavior, CPU/GPU binding, parallelization)
- Type resolution for complex type annotations
- Serialization of operation attributes for persistence

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
from typing import Union, List, Dict, Tuple, Set, Optional, Any, get_origin, get_args
import typing

from research_analytics_suite.commands import command, link_class_commands


@link_class_commands
class OperationAttributes:
    """
    Stores and manages all attributes associated with an operation.

    This class handles the configuration, metadata, and execution settings for operations in the
    Research Analytics Suite. It manages memory slots for inputs and outputs, resolves type
    specifications, and provides serialization capabilities.

    Attributes:
        name (str): The name of the operation. Defaults to '[no-name]'.
        version (str): The version of the operation. Defaults to '0.0.1'.
        description (str): A description of what the operation does. Defaults to '[no-description]'.
        category_id (int): The category ID for organizing operations. Defaults to -1.
        author (str): The author of the operation. Defaults to '[no-author]'.
        github (str): The GitHub username of the operation author. Defaults to '[no-github]'.
        email (str): The contact email of the operation author. Defaults to '[no-email]'.
        unique_id (str): Auto-generated unique identifier combining github, name, and version.
        action (Callable): The callable action to be executed by the operation.
        active (bool): Whether the operation is active and memory slots should be created. Defaults to False.
        required_inputs (Dict[str, type]): Dictionary mapping input names to their type specifications.
            When active, these are converted to memory slot IDs.
        outputs (Dict[str, Any]): Dictionary mapping output names to their values or memory slot IDs.
        parent_operation (Optional[OperationAttributes]): Reference to the parent operation if this is a child.
        inheritance (List[OperationAttributes]): List of child operations that inherit from this operation.
        is_loop (bool): Whether the operation manages its own internal loop. Operations with this set to True
            must implement loop logic (e.g., while self.is_loop: ...) and remain in 'running' status
            until explicitly stopped. Defaults to False.
        is_cpu_bound (bool): Whether the operation is CPU-intensive and should be run in a process pool.
            Defaults to False.
        is_gpu_bound (bool): Whether the operation requires GPU resources and should be offloaded to GPU.
            Defaults to False.
        parallel (bool): Whether child operations should run in parallel (True) or sequentially (False).
            Defaults to False.

    Class Attributes:
        TYPES_DICT (Dict[str, type]): Mapping of type names to actual type objects for type resolution.
        _lock (asyncio.Lock): Async lock for thread-safe initialization.
    """
    _lock = asyncio.Lock()
    TYPES_DICT = {
        # Basic built-in types
        'str': str,
        'int': int,
        'float': float,
        'list': list,
        'dict': dict,
        'tuple': tuple,
        'set': set,
        'bool': bool,
        # Typing module types
        'Union': Union,
        'List': List,
        'Dict': Dict,
        'Tuple': Tuple,
        'Set': Set,
        'Optional': Optional,
        'Any': Any,
        # Python 3.9+ generics support
        'typing.Union': Union,
        'typing.List': List,
        'typing.Dict': Dict,
        'typing.Tuple': Tuple,
        'typing.Set': Set,
        'typing.Optional': Optional,
        'typing.Any': Any,
    }

    def __init__(self, *args, **kwargs):
        self._required_inputs = {}
        self._outputs = {}
        self.temp_kwargs = {}

        if args and isinstance(args[0], dict):
            self.temp_kwargs.update(args[0])
        self.temp_kwargs.update(kwargs)

        from research_analytics_suite.utils import CustomLogger
        self._logger = CustomLogger()

        # Use kwargs to directly initialize attributes, with defaults
        self.name = self.temp_kwargs.get('name', '[no-name]')
        self.version = self.temp_kwargs.get('version', '0.0.1')
        self.description = self.temp_kwargs.get('description', '[no-description]')
        self.category_id = self.temp_kwargs.get('category_id', -1)
        self.author = self.temp_kwargs.get('author', '[no-author]')
        self.github = self.temp_kwargs.get('github', '[no-github]')
        self.email = self.temp_kwargs.get('email', '[no-email]')
        self.action = self.temp_kwargs.get('action', None)
        self.active = self.temp_kwargs.get('active', False)
        self.required_inputs = self.temp_kwargs.get('required_inputs', {})
        self.outputs = self.temp_kwargs.get('outputs', {})
        self.parent_operation = self.temp_kwargs.get('parent_operation', None)
        self.inheritance = self.temp_kwargs.get('inheritance', [])
        self.is_loop = self.temp_kwargs.get('is_loop', False)
        self.is_cpu_bound = self.temp_kwargs.get('is_cpu_bound', False)
        self.is_gpu_bound = self.temp_kwargs.get('is_gpu_bound', False)
        self.parallel = self.temp_kwargs.get('parallel', False)

        # Handle any extra attributes not predefined
        for key, value in self.temp_kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)

        self._initialized = False

    async def initialize(self):
        if not self._initialized:
            async with self._lock:
                if not self._initialized:
                    self.name = self.temp_kwargs.get('name', self.name or '[no-name]')
                    self.version = self.temp_kwargs.get('version', self.version or '0.0.1')
                    self.description = self.temp_kwargs.get('description', self.description or '[no-description]')
                    self.category_id = self.temp_kwargs.get('category_id', self.category_id or -1)
                    self.author = self.temp_kwargs.get('author', self.author or '[no-author]')
                    self.github = self.temp_kwargs.get('github', self.github or '[no-github]')
                    self.email = self.temp_kwargs.get('email', self.email or '[no-email]')
                    self.action = self.temp_kwargs.get('action', self.action or None)
                    self.active = self.temp_kwargs.get('active', self.active or False)
                    self.required_inputs = self.temp_kwargs.get('required_inputs', {})
                    self.outputs = self.temp_kwargs.get('outputs', {})
                    self.parent_operation = self.temp_kwargs.get('parent_operation', self.parent_operation)
                    self.inheritance = self.temp_kwargs.get('inheritance', self.inheritance)
                    self.is_loop = self.temp_kwargs.get('is_loop', self.is_loop)
                    self.is_cpu_bound = self.temp_kwargs.get('is_cpu_bound', self.is_cpu_bound)
                    self.is_gpu_bound = self.temp_kwargs.get('is_gpu_bound', self.is_gpu_bound)
                    self.parallel = self.temp_kwargs.get('parallel', self.parallel)

                    self._initialized = True

                    del self.temp_kwargs

    def _resolve_type(self, type_spec):
        """
        Resolve a type specification to an actual type object.

        Args:
            type_spec: Can be a type object, string name, or complex type annotation

        Returns:
            The resolved type object, or None if resolution fails
        """
        try:
            # If it's already a type or typing construct, return as-is
            if hasattr(type_spec, '__origin__') or isinstance(type_spec, type):
                return type_spec

            # Handle string type specifications
            if isinstance(type_spec, str):
                # Check if it's in our basic types dictionary
                if type_spec in self.TYPES_DICT:
                    return self.TYPES_DICT[type_spec]

                # Handle complex type expressions like "Union[int, str]" or "List[float]"
                if '[' in type_spec and ']' in type_spec:
                    try:
                        # Safely evaluate the type expression
                        # Create a safe namespace with typing constructs
                        safe_namespace = {
                            'Union': Union, 'List': List, 'Dict': Dict, 'Tuple': Tuple,
                            'Set': Set, 'Optional': Optional, 'Any': Any,
                            'str': str, 'int': int, 'float': float, 'bool': bool,
                            'list': list, 'dict': dict, 'tuple': tuple, 'set': set
                        }

                        # Use eval with restricted namespace for safety
                        resolved_type = eval(type_spec, {"__builtins__": {}}, safe_namespace)
                        return resolved_type
                    except (SyntaxError, NameError, TypeError) as e:
                        self._logger.warning(f"Failed to parse complex type '{type_spec}': {e}")
                        return None

                # Try to resolve from typing module directly
                if hasattr(typing, type_spec):
                    return getattr(typing, type_spec)

                # Try to resolve from builtins
                if hasattr(__builtins__, type_spec):
                    return getattr(__builtins__, type_spec)

                # Log unknown type and return None
                self._logger.warning(f"Unknown type specification: '{type_spec}'")
                return None

            # If we can't resolve it, return None
            self._logger.warning(f"Unable to resolve type specification: {type_spec}")
            return None

        except Exception as e:
            self._logger.error(e, f"{self.name}")
            return None

    def _is_valid_type(self, type_obj):
        """
        Check if a type object is valid for operation use.

        Args:
            type_obj: The type object to validate

        Returns:
            bool: True if the type is valid, False otherwise
        """
        if type_obj is None:
            return False

        # Built-in types are always valid
        if isinstance(type_obj, type):
            return True

        # Typing constructs are valid if they have __origin__
        if hasattr(type_obj, '__origin__'):
            return True

        # Special handling for typing module constructs
        if hasattr(type_obj, '__module__') and type_obj.__module__ == 'typing':
            return True

        return False

    @command
    def export_attributes(self) -> dict:
        """Export the attributes of the operation. This is used for saving the operation to disk."""
        from research_analytics_suite.operation_manager.operations.core.workspace.WorkspaceInteraction import \
            pack_as_local_reference
        from research_analytics_suite.data_engine.memory.MemoryManager import MemoryManager
        _memory_manager = MemoryManager()

        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'category_id': self.category_id,
            'author': self.author,
            'github': self.github,
            'email': self.email,
            'unique_id': self.unique_id,
            'action': self.action,
            'required_inputs': self.required_inputs,
            'outputs': self.outputs,
            'parent_operation': pack_as_local_reference(self.parent_operation) if self.parent_operation else None,
            'inheritance': [pack_as_local_reference(child) for child in self.inheritance if self.inheritance is not []],
            'is_loop': self.is_loop,
            'is_cpu_bound': self.is_cpu_bound,
            'is_gpu_bound': self.is_gpu_bound,
            'parallel': self.parallel,
        }

    @property
    def name(self) -> str:
        return self._name if self._name else "[no-name]"

    @name.setter
    def name(self, value):
        self._name = value if (value and isinstance(value, str)) else "[no-name]"

    @property
    def version(self) -> str:
        return self._version if self._version else "0.0.1"

    @version.setter
    def version(self, value):
        self._version = value if (value and isinstance(value, str)) else "0.0.1"

    @property
    def description(self) -> str:
        return self._description if self._description else "[no-description]"

    @description.setter
    def description(self, value):
        self._description = value if (value and isinstance(value, str)) else "[no-description]"

    @property
    def category_id(self) -> int:
        return self._category_id if hasattr(self, '_category_id') else -1

    @category_id.setter
    def category_id(self, value: int):
        if value is not None and isinstance(value, int):
            self._category_id = value
        else:
            self._category_id = -1

    @property
    def author(self) -> str:
        return self._author if self._author else "[no-author]"

    @author.setter
    def author(self, value):
        self._author = value if (value and isinstance(value, str)) else "[no-author]"

    @property
    def github(self) -> str:
        return self._github if self._github else "[no-github]"

    @github.setter
    def github(self, value):
        if isinstance(value, str) and value.startswith("@"):
            value = value[1:]
        self._github = value if (value and isinstance(value, str)) else "[no-github]"

    @property
    def email(self) -> str:
        return self._email if self._email else "[no-email]"

    @email.setter
    def email(self, value):
        self._email = value if (value and isinstance(value, str)) else "[no-email]"

    @property
    def unique_id(self) -> str:
        return f"{self.github}_{self.name}_{self.version}"

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, value):
        self._action = value if value else None

    @property
    def required_inputs(self) -> dict:
        _inputs = {}

        if hasattr(self, '_active') and self._active:
            from research_analytics_suite.data_engine.memory.MemoryManager import MemoryManager
            _memory_manager = MemoryManager()

            for _name, _value in self._required_inputs.items():
                if isinstance(_value, str):
                    _slot_id = _value
                    _slot = _memory_manager.get_slot(_slot_id)
                    if _slot is None:
                        _inputs[_name] = None
                        continue
                    _slot_id = _slot.memory_id
                    _slot_name = _slot.name
                    _slot_type = _slot.data_type
                    _slot_data = _slot.data

                    _inputs[_name] = _slot_data if _slot_data is not None else self._get_default_value(_slot_type)
                elif isinstance(_value, type):
                    _inputs[_name] = _value
        else:
            for _name, d_type in self._required_inputs.items():
                _inputs[_name] = d_type

        return _inputs

    @required_inputs.setter
    def required_inputs(self, value: dict):
        """
        Set the required inputs for the operation.

        Args:
            value (dict): The required inputs for the operation.
        """
        from research_analytics_suite.data_engine.memory.MemoryManager import MemoryManager
        _memory_manager = MemoryManager()

        if not isinstance(value, dict):
            self._logger.warning(f"Required inputs must be a dictionary, got {type(value)}")
            return

        processed_inputs = {}
        for name, d_type in value.items():
            # Resolve the type using our enhanced type resolution
            resolved_type = self._resolve_type(d_type)

            if resolved_type is not None and self._is_valid_type(resolved_type):
                processed_inputs[name] = resolved_type

                # Create memory slots for valid types
                if asyncio.get_event_loop().is_running():
                    asyncio.ensure_future(self._create_input_slot(name, resolved_type))
                else:
                    asyncio.run(self._create_input_slot(name, resolved_type))

                self._logger.debug(f"Processed input '{name}': {d_type} -> {resolved_type}")
            else:
                # For failed type resolution, log but don't completely discard
                self._logger.warning(f"Could not resolve type '{d_type}' for input '{name}', storing as-is")
                processed_inputs[name] = d_type

                # Still try to create a slot with the original type spec
                try:
                    if asyncio.get_event_loop().is_running():
                        asyncio.ensure_future(self._create_input_slot(name, d_type))
                    else:
                        asyncio.run(self._create_input_slot(name, d_type))
                except Exception as e:
                    self._logger.error(e, f"{self.name}")

        self._logger.debug(f"Required inputs set for {self.name}: {list(processed_inputs.keys())}")

    @property
    def input_ids(self) -> dict:
        """
        Get the input IDs for the operation.

        Returns:
            dict: The input IDs for the operation.
        """
        _inputs = {}
        if hasattr(self, '_active') and self._active:
            for _name, _value in self._required_inputs.items():
                if self._is_valid_type(_value):
                    _inputs[_name] = _value
                else:
                    _slot_id = _value
                    _inputs[_name] = _slot_id
        else:
            for _name, d_type in self._required_inputs.items():
                if self._is_valid_type(d_type):
                    _inputs[_name] = d_type
                else:
                    # For unresolved types, still include them
                    _inputs[_name] = d_type

        return _inputs

    def _get_default_value(self, data_type):
        """
        Get appropriate default value for a given data type.

        Args:
            data_type: The data type to get default value for

        Returns:
            Default value for the type
        """
        if data_type == int:
            return 0
        elif data_type == float:
            return 0.0
        elif data_type == str:
            return ""
        elif data_type == list:
            return []
        elif data_type == dict:
            return {}
        elif data_type == bool:
            return False
        elif data_type == tuple:
            return ()
        elif data_type == set:
            return set()
        else:
            # For complex types or unknown types, return None
            return None

    async def _create_input_slot(self, name: str, d_type):
        """
        Create an input memory slot for the operation.

        Args:
            name (str): The name of the memory slot.
            d_type: The data type of the memory slot (can be complex type annotation).
        """
        if hasattr(self, '_active') and self._active:
            from research_analytics_suite.data_engine.memory.MemoryManager import MemoryManager
            _memory_manager = MemoryManager()

            try:
                # For memory slot creation, we may need to simplify complex types
                slot_type = d_type
                if hasattr(d_type, '__origin__'):
                    # For Union types, use the origin or first arg as the slot type
                    origin = get_origin(d_type)
                    if origin is Union:
                        args = get_args(d_type)
                        if args:
                            slot_type = args[0]  # Use first type in Union
                    else:
                        slot_type = origin or d_type

                _slot_id, _, _ = await _memory_manager.create_slot(name=name, d_type=slot_type)
                self._required_inputs[name] = _slot_id
                self._logger.debug(f"Created input memory slot for {self.name}: [{_slot_id}] {name} ({d_type})")
            except Exception as e:
                self._logger.warning(f"Failed to create memory slot for {name} with type {d_type}: {e}")
                # Fall back to storing the type directly
                self._required_inputs[name] = d_type
        else:
            self._required_inputs[name] = d_type

    @property
    def outputs(self) -> dict:
        """
        Get the outputs for the operation.

        Returns:
            dict: The outputs for the operation.
        """
        _outputs = {}
        if hasattr(self, '_active') and self._active:
            from research_analytics_suite.data_engine.memory.MemoryManager import MemoryManager
            _memory_manager = MemoryManager()

            for _name, _value in self._outputs.items():
                if isinstance(_value, type):
                    _outputs[_name] = _value
                else:
                    _slot_id = _value
                    _slot = _memory_manager.get_slot(_slot_id)
                    if _slot is None:
                        _outputs[_name] = None
                        continue
                    _slot_id = _slot.memory_id
                    _slot_name = _slot.name
                    _slot_type = _slot.data_type
                    _slot_data = _slot.data

                    _outputs[_name] = _slot_data if _slot_data is not None else self._get_default_value(_slot_type)
        else:
            for name, d_type in self._outputs.items():
                if isinstance(d_type, type):
                    _outputs[name] = d_type

        return _outputs

    @outputs.setter
    def outputs(self, value: dict):
        """
        Set the outputs for the operation.

        Args:
            value (dict): The outputs for the operation.
        """
        if self._outputs is None:
            self._outputs = {}

        # Check if value is a memory slot ID
        if isinstance(value, str):
            from research_analytics_suite.data_engine.memory.MemoryManager import MemoryManager
            _memory_manager = MemoryManager()

            _slot = _memory_manager.get_slot(value)
            _name = _slot.name
            _slot_id = _slot.memory_id
            self._outputs[_slot.name] = _slot.memory_id
            return

        for name, data in value.items():
            if asyncio.get_event_loop().is_running():
                asyncio.ensure_future(self._create_output_slot(name, data))
            else:
                asyncio.run(self._create_output_slot(name, data))

    @property
    def output_ids(self) -> dict:
        """
        Get the output IDs for the operation.

        Returns:
            dict: The output IDs for the operation.
        """
        _outputs = {}
        if hasattr(self, '_active') and self._active:
            for _name, _value in self._outputs.items():
                if self._is_valid_type(_value):
                    _outputs[_name] = _value
                else:
                    _slot_id = _value
                    _outputs[_name] = _slot_id
        else:
            for name, d_type in self._outputs.items():
                if self._is_valid_type(d_type):
                    _outputs[name] = d_type
                else:
                    # For unresolved types, still include them
                    _outputs[name] = d_type

        return _outputs

    async def _create_output_slot(self, name: str, data: any = None):
        """
        Create an output memory slot for the operation.

        Args:
            name (str): The name of the memory slot.
            data (any, optional): The data for the memory slot. Defaults to None.
        """
        if hasattr(self, '_active') and self._active:
            from research_analytics_suite.data_engine.memory.MemoryManager import MemoryManager
            _memory_manager = MemoryManager()

            _slot_id, _, _ = await _memory_manager.create_slot(name=name, d_type=type(data), data=data)
            self._outputs[name] = _slot_id
            self._logger.debug(f"Created output memory slot for {self.name}: [{_slot_id}] {name} ({data})")
        else:
            self._outputs[name] = data

    @property
    def parent_operation(self):
        return self._parent_operation if self._parent_operation else None

    @parent_operation.setter
    def parent_operation(self, value):
        if isinstance(value, dict):
            value = OperationAttributes(**value)
            if asyncio.get_event_loop().is_running():
                asyncio.ensure_future(value.initialize())
            else:
                asyncio.run(value.initialize())
        elif isinstance(value, OperationAttributes):
            if not value._initialized:
                if asyncio.get_event_loop().is_running():
                    asyncio.ensure_future(value.initialize())
                else:
                    asyncio.run(value.initialize())
        else:
            value = None

        self._parent_operation = value

    @property
    def inheritance(self) -> list:
        return self._inheritance

    @inheritance.setter
    def inheritance(self, value):
        self._inheritance = value if (value and isinstance(value, list)) else []

    @property
    def is_loop(self) -> bool:
        return self._is_loop if self._is_loop else False

    @is_loop.setter
    def is_loop(self, value):
        self._is_loop = value if (value and isinstance(value, bool)) else False

    @property
    def is_cpu_bound(self) -> bool:
        return self._is_cpu_bound if self._is_cpu_bound else False

    @is_cpu_bound.setter
    def is_cpu_bound(self, value):
        self._is_cpu_bound = value if (value and isinstance(value, bool)) else False

    @property
    def is_gpu_bound(self) -> bool:
        return self._is_gpu_bound if self._is_gpu_bound else False

    @is_gpu_bound.setter
    def is_gpu_bound(self, value):
        self._is_gpu_bound = value if (value and isinstance(value, bool)) else False

    @property
    def parallel(self) -> bool:
        return self._parallel if self._parallel else False

    @parallel.setter
    def parallel(self, value):
        self._parallel = value if (value and isinstance(value, bool)) else False

    @property
    def active(self) -> bool:
        return self._active if self._active else False

    @active.setter
    def active(self, value):
        if value and isinstance(value, bool):
            # req_inputs = self.required_inputs if self.required_inputs else {}
            self._active = value
            # self.required_inputs = req_inputs
        else:
            self._active = False

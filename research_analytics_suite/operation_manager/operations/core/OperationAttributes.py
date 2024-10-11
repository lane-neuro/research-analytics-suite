"""
OperationAttributes

This module contains the OperationAttributes class, which is used to store the attributes of an operation.

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

from research_analytics_suite.commands import command, link_class_commands


@link_class_commands
class OperationAttributes:
    _lock = asyncio.Lock()
    TYPES_DICT = {
        'str': str,
        'int': int,
        'float': float,
        'list': list,
        'dict': dict,
        'tuple': tuple,
        'set': set,
        'bool': bool
    }

    def __init__(self, *args, **kwargs):
        self._required_inputs = {}
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
                    self.parent_operation = self.temp_kwargs.get('parent_operation', self.parent_operation)
                    self.inheritance = self.temp_kwargs.get('inheritance', self.inheritance)
                    self.is_loop = self.temp_kwargs.get('is_loop', self.is_loop)
                    self.is_cpu_bound = self.temp_kwargs.get('is_cpu_bound', self.is_cpu_bound)
                    self.is_gpu_bound = self.temp_kwargs.get('is_gpu_bound', self.is_gpu_bound)
                    self.parallel = self.temp_kwargs.get('parallel', self.parallel)

                    self._initialized = True

                    del self.temp_kwargs

    @command
    async def export_attributes(self) -> dict:
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
            'parent_operation': pack_as_local_reference(self.parent_operation) if self.parent_operation else None,
            'inheritance': [
                pack_as_local_reference(child) for child in self.inheritance if self.inheritance is not []],
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
                if isinstance(_value, type):
                    _inputs[_name] = _value
                else:
                    _slot_id = _value
                    _slot = _memory_manager.get_slot(_slot_id)
                    if _slot is None:
                        _inputs[_name] = None
                        continue
                    _slot_id = _slot.memory_id
                    _slot_name = _slot.name
                    _slot_type = _slot.data_type
                    _slot_data = _slot.data

                    _inputs[_slot_name] = _slot_data if _slot_data is not None else _slot_type
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
            return

        for name, d_type in value.items():
            if isinstance(d_type, str):
                d_type = self.TYPES_DICT.get(d_type, str)
            if isinstance(d_type, type):
                if asyncio.get_event_loop().is_running():
                    asyncio.ensure_future(self._create_memory_slot(name, d_type))
                else:
                    asyncio.run(self._create_memory_slot(name, d_type))

        self._logger.debug(f"Required inputs set for {self.name}")

    async def _create_memory_slot(self, name: str, d_type: type):
        """
        Create a memory slot for the operation.

        Args:
            name (str): The name of the memory slot.
            d_type (type): The data type of the memory slot.
        """
        if self.active:
            from research_analytics_suite.data_engine.memory.MemoryManager import MemoryManager
            _memory_manager = MemoryManager()
            _slot_id, _, _ = await _memory_manager.create_slot(name=name, d_type=d_type)
            self._required_inputs[name] = _slot_id
            self._logger.debug(f"Created memory slot for {self.name}: [{_slot_id}] {name} ({d_type})")
        else:
            self._required_inputs[name] = d_type

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
            req_inputs = self.required_inputs if self.required_inputs else {}
            self._active = value
            self.required_inputs = req_inputs
        else:
            self._active = False

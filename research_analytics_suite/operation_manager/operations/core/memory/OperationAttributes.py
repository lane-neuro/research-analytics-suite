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

from research_analytics_suite.commands import command, register_commands
from research_analytics_suite.operation_manager import BaseOperation


@register_commands
class OperationAttributes:
    _lock = asyncio.Lock()
    _TYPES_DICT = {
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
        self.temp_kwargs = {}

        if not hasattr(self, '_initialized'):
            if args and isinstance(args[0], dict):
                self.temp_kwargs.update(args[0])
            self.temp_kwargs.update(kwargs)

            from research_analytics_suite.utils import CustomLogger
            self._logger = CustomLogger()

            self.name = None
            self.version = None
            self.description = None
            self.category_id = None
            self.author = None
            self.github = None
            self.email = None
            self.action = None
            self.required_inputs = {}
            self.parent_operation = None
            self.inheritance = []
            self.is_loop = False
            self.is_cpu_bound = False
            self.parallel = False

            self._initialized = False

    def _process_required_inputs(self, inputs: dict) -> dict:
        """Process required inputs by converting string values using a predefined dictionary.

        Args:
            inputs (dict): A dictionary of inputs to be processed.

        Returns:
            dict: A dictionary with processed inputs.
        """
        if not isinstance(inputs, dict):
            raise ValueError("Expected a dictionary as input")

        processed_dict = {}
        for k, v in inputs.items():
            if isinstance(v, str):
                processed_dict[k] = self._TYPES_DICT.get(v.lower(), getattr(v, '__name__', v))
            else:
                processed_dict[k] = getattr(v, '__name__', v)

        return processed_dict

    async def initialize(self):
        if not self._initialized:
            async with self._lock:
                if not self._initialized:
                    self.name = self.temp_kwargs.get('name', '[no-name]')
                    self.version = self.temp_kwargs.get('version', '0.0.1')
                    self.description = self.temp_kwargs.get('description', '[no-description]')
                    self.category_id = self.temp_kwargs.get('category_id', -1)
                    self.author = self.temp_kwargs.get('author', '[no-author]')
                    self.github = self.temp_kwargs.get('github', '[no-github]')
                    self.email = self.temp_kwargs.get('email', '[no-email]')
                    self.action = self.temp_kwargs.get('action', None)
                    self.required_inputs = self.temp_kwargs.get('required_inputs', {})
                    self.parent_operation = self.temp_kwargs.get('parent_operation', None)
                    self.inheritance = self.temp_kwargs.get('inheritance', [])
                    self.is_loop = self.temp_kwargs.get('is_loop', False)
                    self.is_cpu_bound = self.temp_kwargs.get('is_cpu_bound', False)
                    self.parallel = self.temp_kwargs.get('parallel', False)

                    self._initialized = True

                    del self.temp_kwargs

    @command
    def export_attributes(self) -> dict:
        return {
            'name': self._name,
            'version': self._version,
            'description': self._description,
            'category_id': self._category_id,
            'author': self._author,
            'github': self._github,
            'email': self._email,
            'unique_id': self.unique_id,
            'action': self._action,
            'required_inputs': self._required_inputs,
            'parent_operation': self._parent_operation,
            'inheritance': self._inheritance,
            'is_loop': self._is_loop,
            'is_cpu_bound': self._is_cpu_bound,
            'parallel': self._parallel,
        }

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value):
        self._name = value if value and isinstance(value, str) else "[no-name]"

    @property
    def version(self) -> str:
        return self._version

    @version.setter
    def version(self, value):
        self._version = value if value and isinstance(value, str) else "0.0.1"

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value):
        self._description = value if value and isinstance(value, str) else "[no-description]"

    @property
    def category_id(self) -> int:
        return self._category_id

    @category_id.setter
    def category_id(self, value: int):
        self._category_id = value if value and isinstance(value, int) else -1

    @property
    def author(self) -> str:
        return self._author

    @author.setter
    def author(self, value):
        self._author = value if value and isinstance(value, str) else "[no-author]"

    @property
    def github(self) -> str:
        return self._github

    @github.setter
    def github(self, value):
        if isinstance(value, str) and value.startswith("@"):
            value = value[1:]
        self._github = value if value and isinstance(value, str) else "[no-github]"

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value):
        self._email = value if value and isinstance(value, str) else "[no-email]"

    @property
    def unique_id(self) -> str:
        return f"{self.github}_{self.name}_{self.version}"

    @property
    def action(self) -> any:
        return self._action

    @action.setter
    def action(self, value):
        self._action = value if value else None

    @property
    def required_inputs(self) -> dict:
        if not self._required_inputs:
            return {}
        return self._required_inputs

    @required_inputs.setter
    def required_inputs(self, value: dict):
        self._required_inputs = self._process_required_inputs(value) if value and isinstance(value, dict) else {}

    @property
    def parent_operation(self) -> OperationAttributes or BaseOperation or None:
        return self._parent_operation

    @parent_operation.setter
    def parent_operation(self, value):
        self._parent_operation = value if value and isinstance(value, type(OperationAttributes) or type(BaseOperation)) else None

    @property
    def inheritance(self) -> list:
        return self._inheritance

    @inheritance.setter
    def inheritance(self, value):
        self._inheritance = value if value and isinstance(value, list) else []

    @property
    def is_loop(self) -> bool:
        return self._is_loop

    @is_loop.setter
    def is_loop(self, value):
        self._is_loop = value if value and isinstance(value, bool) else False

    @property
    def is_cpu_bound(self) -> bool:
        return self._is_cpu_bound

    @is_cpu_bound.setter
    def is_cpu_bound(self, value):
        self._is_cpu_bound = value if value and isinstance(value, bool) else False

    @property
    def parallel(self) -> bool:
        return self._parallel

    @parallel.setter
    def parallel(self, value):
        self._parallel = value if value and isinstance(value, bool) else False

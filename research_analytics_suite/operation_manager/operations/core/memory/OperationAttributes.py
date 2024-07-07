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
import asyncio
from typing import Any

from research_analytics_suite.operation_manager import BaseOperation


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
        if not hasattr(self, '_initialized'):
            from research_analytics_suite.utils import CustomLogger
            self._logger = CustomLogger()

            self._name = kwargs.get('name') or "[no-name]"
            self._version = kwargs.get('version') or "0.0.1"
            self._description = kwargs.get('description') or "[no-description]"
            self._category_id = kwargs.get('category_id') or 1
            self._author = kwargs.get('author') or "[no-author]"
            self._github = kwargs.get('github') or "[no-github]"
            self._email = kwargs.get('email') or "[no-email]"
            self._action = kwargs.get('action') or None
            self._required_inputs = self._process_required_inputs(kwargs.get('required_inputs', {}))
            self._parent_operation = kwargs.get('parent_operation') or None
            self._inheritance = kwargs.get('inheritance') or []
            self._is_loop = kwargs.get('is_loop') or False
            self._is_cpu_bound = kwargs.get('is_cpu_bound') or False
            self._parallel = kwargs.get('parallel') or False

            self._initialized = False

    def _process_required_inputs(self, inputs):
        if isinstance(inputs, dict):
            processed_dict = {}
            for k, v in inputs.items():
                if isinstance(v, str):
                    try:
                        processed_dict[k] = self._TYPES_DICT[v.lower()]
                    except KeyError:
                        processed_dict[k] = None
                else:
                    processed_dict[k] = v
            return processed_dict
        return {}

    async def initialize(self):
        if not self._initialized:
            async with self._lock:
                if not self._initialized:
                    self.name = self._name
                    self.version = self._version
                    self.description = self._description
                    self.category_id = self._category_id
                    self.author = self._author
                    self.github = self._github
                    self.email = self._email
                    self.action = self._action
                    self.required_inputs = self._required_inputs
                    self.parent_operation = self._parent_operation
                    self.inheritance = self._inheritance
                    self.is_loop = self._is_loop
                    self.is_cpu_bound = self._is_cpu_bound
                    self.parallel = self._parallel

                    self._initialized = True

    def export_attributes(self) -> dict:
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
            'parent_operation': self.parent_operation,
            'inheritance': self.inheritance,
            'is_loop': self.is_loop,
            'is_cpu_bound': self.is_cpu_bound,
            'parallel': self.parallel,
        }

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value):
        self._name = value if isinstance(value, str) else "[no-name]"

    @property
    def version(self) -> str:
        return self._version

    @version.setter
    def version(self, value):
        self._version = value if isinstance(value, str) else "0.0.1"

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value):
        self._description = value if isinstance(value, str) else "[no-description]"

    @property
    def category_id(self) -> int:
        return self._category_id

    @category_id.setter
    def category_id(self, value):
        self._category_id = value if isinstance(value, int) else 1

    @property
    def author(self) -> str:
        return self._author

    @author.setter
    def author(self, value):
        self._author = value if isinstance(value, str) else "[no-author]"

    @property
    def github(self) -> str:
        return self._github

    @github.setter
    def github(self, value):
        if isinstance(value, str) and value.startswith("@"):
            value = value[1:]
        self._github = value if isinstance(value, str) else "[no-github]"

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value):
        self._email = value if isinstance(value, str) else "[no-email]"

    @property
    def unique_id(self) -> str:
        return f"{self.github}_{self.name}_{self.version}"

    @property
    def action(self) -> Any:
        return self._action

    @action.setter
    def action(self, value):
        self._action = value

    @property
    def required_inputs(self) -> dict:
        return self._required_inputs

    @required_inputs.setter
    def required_inputs(self, value):
        self._required_inputs = self._process_required_inputs(value)

    @property
    def parent_operation(self) -> 'OperationAttributes' or 'BaseOperation' or None:
        return self._parent_operation

    @parent_operation.setter
    def parent_operation(self, value):
        self._parent_operation = value if isinstance(value, type(OperationAttributes) or type(BaseOperation)) else None

    @property
    def inheritance(self) -> list:
        return self._inheritance

    @inheritance.setter
    def inheritance(self, value):
        self._inheritance = value if isinstance(value, list) else []

    @property
    def is_loop(self) -> bool:
        return self._is_loop

    @is_loop.setter
    def is_loop(self, value):
        self._is_loop = value if isinstance(value, bool) else False

    @property
    def is_cpu_bound(self) -> bool:
        return self._is_cpu_bound

    @is_cpu_bound.setter
    def is_cpu_bound(self, value):
        self._is_cpu_bound = value if isinstance(value, bool) else False

    @property
    def parallel(self) -> bool:
        return self._parallel

    @parallel.setter
    def parallel(self, value):
        self._parallel = value if isinstance(value, bool) else False



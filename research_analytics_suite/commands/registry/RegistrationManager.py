"""
RegistrationManager Module

This module defines the RegistrationManager class, which manages the discovery and registration of commands within the
Research Analytics Suite. It provides methods to initialize commands and register instances.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

import importlib
import inspect
import pkgutil
from typing import get_type_hints, List, Dict, Union, ForwardRef, Tuple

from research_analytics_suite.commands.utils import dynamic_import, parse_typing_alias
from research_analytics_suite.commands.CommandDecorators import clean_description


class RegistrationManager:
    """Class that manages the discovery and registration of commands."""

    def __init__(self):
        """Initialize the RegistrationManager with default values."""
        self._logger = None
        self._config = None
        self._operation_control = None
        self._library_manifest = None
        self._workspace = None

        self._registry = {}
        self._instances = {}
        self._categories = {}

        self._initialized = False

    async def initialize(self):
        """Initialize the RegistrationManager and its components asynchronously."""
        if not self._initialized:
            try:
                from research_analytics_suite.utils import CustomLogger
                self._logger = CustomLogger()

                from research_analytics_suite.utils import Config
                self._config = Config()

                from research_analytics_suite.operation_manager.control.OperationControl import OperationControl
                self._operation_control = OperationControl()

                from research_analytics_suite.library_manifest import LibraryManifest
                self._library_manifest = LibraryManifest()

                from research_analytics_suite.data_engine import Workspace
                self._workspace = Workspace()

                self.discover_commands('research_analytics_suite')

                self._initialized = True
            except Exception as e:
                if self._logger:
                    self._logger.error(Exception(f"Initialization failed: {e}"), self.__class__.__name__)
                else:
                    raise Exception(f"Initialization failed: {e}")

    def _initialize_command(self, cmd_meta):
        """Initialize a command with its metadata.

        Args:
            cmd_meta (dict): The command metadata.
        """
        _args = cmd_meta.get('args', [])
        for _arg in _args:
            if _arg['type'] is not type(any) and not isinstance(_arg['type'], type):
                _arg['type'] = _arg.get('type', type(any))
                if _arg['type'] is not any and not isinstance(_arg['type'], type):
                    try:
                        _arg['type'] = dynamic_import(_arg['type'])
                    except Exception as e:
                        self._logger.error(ValueError(f"Error resolving forward reference for {_arg['name']} in "
                                                      f"{cmd_meta['name']}: {e}"), self.__class__.__name__)
                        return

        _return_type = cmd_meta.get('return_type')
        if isinstance(_return_type, list):
            resolved_return_types = []
            for _rt in _return_type:
                if not isinstance(_rt, type):
                    try:
                        _rt = dynamic_import(_rt)
                    except Exception as e:
                        self._logger.error(ValueError(f"Error resolving forward reference for return type in "
                                                      f"{cmd_meta['name']}: {e}"), self.__class__.__name__)
                        return
                resolved_return_types.append(self._get_type_name(_rt))
            cmd_meta['return_type'] = resolved_return_types
        else:
            try:
                if _return_type is not type(any) and not isinstance(_return_type, type) and isinstance(_return_type, str):
                    _return_type = parse_typing_alias(_return_type, _return_type)
                _return_type = [self._get_type_name(_return_type)]
            except Exception as e:
                self._logger.error(ValueError(f"Error resolving forward reference for return type in "
                                              f"{cmd_meta['name']}: {e}"), self.__class__.__name__)
                return

        self._registry[cmd_meta['name']] = {
            'func': cmd_meta.get('func', None),
            'name': cmd_meta.get('name', None),
            'description': cmd_meta.get('description', None),
            'class_name': cmd_meta.get('class_name', None),
            'args': _args,
            'return_type': cmd_meta.get('return_type', any),
            'is_method': cmd_meta.get('is_method', False),
            '_is_command': True,
            'category': cmd_meta.get('category', 'Uncategorized'),
            'tags': cmd_meta.get('tags', []),
        }

    def _get_type_name(self, type_hint):
        """Resolve the name of a type hint.

        Args:
            type_hint: The type hint to resolve.

        Returns:
            The resolved type name.
        """
        if isinstance(type_hint, ForwardRef):
            return type_hint.__forward_arg__
        elif hasattr(type_hint, '__origin__'):
            origin = type_hint.__origin__
            if origin is list or origin is List:
                return f'List[{self._get_type_name(type_hint.__args__[0])}]'
            elif origin is dict or origin is Dict:
                key_type = self._get_type_name(type_hint.__args__[0])
                value_type = self._get_type_name(type_hint.__args__[1])
                return f'Dict[{key_type}, {value_type}]'
            elif origin is tuple or origin is Tuple:
                return f'Tuple[{", ".join(self._get_type_name(arg) for arg in type_hint.__args__)}]'
            elif origin is Union:
                return f'Union[{", ".join(self._get_type_name(arg) for arg in type_hint.__args__)}]'
            else:
                return str(origin)
        else:
            if isinstance(type_hint, type):
                return type_hint.__name__
            return str(type_hint)

    def discover_commands(self, package: str):
        """Discover commands in the specified package.

        Args:
            package (str): The package to search for commands.
        """
        package = importlib.import_module(package)
        for loader, name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
            module = importlib.import_module(name)
            for _, obj in inspect.getmembers(module):
                if inspect.isfunction(obj) and hasattr(obj, '_is_command'):
                    _description = obj.__doc__ if obj.__doc__ else None
                    _description = clean_description(_description) if _description else None

                    self._initialize_command({
                        'func': obj,
                        'name': obj.__name__,
                        'description': _description,
                        'class_name': None,
                        'args': [{'name': param, 'type': get_type_hints(obj).get(param, any)} for param in inspect.signature(obj).parameters],
                        'return_type': get_type_hints(obj).get('return', any),
                        'is_method': False,
                        'category': getattr(obj, 'category', 'Uncategorized'),
                        'tags': getattr(obj, 'tags', []),
                    })
                elif inspect.isclass(obj):
                    for method_name, method in inspect.getmembers(obj, predicate=inspect.isfunction):
                        if hasattr(method, '_is_command'):
                            _description = method.__doc__ if method.__doc__ else None
                            _description = clean_description(_description) if _description else None

                            self._initialize_command({
                                'func': method,
                                'name': method.__name__,
                                'description': _description,
                                'class_name': obj.__name__,
                                'args': [{'name': param, 'type': get_type_hints(method).get(param, any)} for param in inspect.signature(method).parameters if param != 'self'],
                                'return_type': get_type_hints(method).get('return', any),
                                'is_method': True,
                                'class': obj,
                                'category': getattr(method, 'category', 'Uncategorized'),
                                'tags': getattr(method, 'tags', []),
                            })

    def register_instance(self, instance, runtime_id):
        """Register an instance with a runtime ID.

        Args:
            instance: The instance to register.
            runtime_id: The runtime ID of the instance.
        """
        if not self._instances:
            self._instances = {}
        if not runtime_id:
            runtime_id = id(instance)

        if runtime_id in self._instances:
            self._logger.error(ValueError(f"Instance with runtime ID '{runtime_id}' already exists."),
                               self.__class__.__name__)
            return

        self._instances[runtime_id] = instance

    def get_instance(self, runtime_id):
        """Get an instance by runtime ID.

        Args:
            runtime_id: The runtime ID of the instance.

        Returns:
            The instance associated with the runtime ID, or None if not found.
        """
        return self._instances.get(runtime_id, None)

    @property
    def registry(self) -> dict:
        """Get the command registry."""
        return self._registry

    @registry.setter
    def registry(self, registry):
        """Set the command registry."""
        self._registry = registry

    @property
    def categories(self) -> dict:
        """Get the available categories."""
        return self._categories

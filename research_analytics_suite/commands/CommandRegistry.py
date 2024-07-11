"""
CommandRegistry Module

This module defines the CommandRegistry class, which manages the registration and discovery of commands within the
Research Analytics Suite. It provides methods to register commands and discover them dynamically in a given package.

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
from asyncio import iscoroutinefunction
from typing import get_type_hints

from research_analytics_suite.commands.utils import dynamic_import


class CommandRegistry:
    """
    A class to manage the registration and discovery of commands.

    This class provides methods to register commands and discover them dynamically in a given package.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CommandRegistry, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._registry = {}
            self._instances = {}  # Dictionary to hold instances by runtime ID
            self._logger = None
            self._config = None
            self._operation_control = None
            self._library_manifest = None
            self._workspace = None

            self._initialized = False

    async def initialize(self):
        """
        Initializes the command registry with the necessary components.
        """
        if not self._initialized:
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

            self._initialize_collected_commands()

            self._initialized = True

    def _initialize_collected_commands(self):
        """
        Register all collected commands from the temporary registry after initialization.
        """
        from research_analytics_suite.commands.CommandDecorators import temp_command_registry
        for cmd_meta in temp_command_registry:
            self._initialize_command(cmd_meta)

        temp_command_registry.clear()  # Clear the temporary registry

    def _initialize_command(self, cmd_meta):
        """
        Initializes a command function with the given metadata.

        Args:
            cmd_meta (dict): The command metadata to register.
        """
        _args = cmd_meta.get('args', [])
        for _arg in _args or []:
            if _arg['type'] is not any and not isinstance(_arg['type'], type):
                _arg['type'] = _arg.get('type', any)
                if _arg['type'] is not any and not isinstance(_arg['type'], type):
                    # attempt to resolve forward references
                    try:
                        # Extract module path and class name
                        _arg['type'] = dynamic_import(_arg['type'])
                    except (NameError, ImportError, AttributeError) as e:
                        self._logger.error(ValueError(f"Error resolving forward reference for {_arg['name']} in "
                                                      f"{cmd_meta['name']}: {e}"), self.__class__.__name__)
                        return

        self._registry[cmd_meta['name']] = {
            'func': cmd_meta.get('func', None),
            'name': cmd_meta.get('name', None),
            'class_name': cmd_meta.get('class_name', None),
            'args': _args,
            'return_type': cmd_meta.get('return_type', None),
            'is_method': cmd_meta.get('is_method', False),  # Ensure 'is_method' is always included
            '_is_command': True
        }

    def discover_commands(self, package):
        """
        Discover and register all commands in the specified package.

        Args:
            package (str): The package name to discover commands in.
        """

        package = importlib.import_module(package)
        for loader, name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
            module = importlib.import_module(name)
            for _, obj in inspect.getmembers(module):
                if inspect.isfunction(obj) and hasattr(obj, '_is_command'):
                    self._initialize_command({
                        'func': obj,
                        'name': obj.__name__,
                        'class_name': None,  # No class context for functions
                        'args': [{'name': param, 'type': get_type_hints(obj).get(param, str)} for param in
                                 inspect.signature(obj).parameters],
                        'return_type': get_type_hints(obj).get('return', None),
                        'is_method': False
                    })
                elif inspect.isclass(obj):
                    for method_name, method in inspect.getmembers(obj, predicate=inspect.isfunction):
                        if hasattr(method, '_is_command'):
                            self._initialize_command({
                                'func': method,
                                'name': method.__name__,
                                'class_name': obj.__name__,
                                'args': [{'name': param, 'type': get_type_hints(method).get(param, str)} for param in
                                         inspect.signature(method).parameters if param != 'self'],
                                'return_type': get_type_hints(method).get('return', None),
                                'is_method': True,
                                'class': obj  # Include the class context for methods
                            })

    def register_instance(self, instance, runtime_id):
        """
        Register an instance with a runtime ID.

        Args:
            instance: The instance to register.
            runtime_id: The runtime ID associated with the instance.
        """
        self._instances[runtime_id] = instance

    async def execute_command(self, name, runtime_id=None, *args, **kwargs):
        """
        Execute a registered command.

        Args:
            name (str): The name of the command to execute.
            runtime_id: The runtime ID for instance-specific methods.
            *args: Positional arguments for the command.
            **kwargs: Keyword arguments for the command.

        Returns:
            The result of the command execution.
        """
        cmd_meta = self._registry.get(name)
        if cmd_meta is None:
            self._logger.error(ValueError(f"Command '{name}' not found in the registry."), self.__class__.__name__)
            self._logger.info(f"Command registry: {self._registry}")
            return None

        if cmd_meta['is_method'] and runtime_id is not None:
            instance = self._instances.get(runtime_id)
            if instance is None:
                self._logger.error(ValueError(f"Instance with runtime ID '{runtime_id}' not found."),
                                   self.__class__.__name__)
                return None
            return cmd_meta['func'](instance, *args, **kwargs)
        else:
            # Check whether the command requires arguments
            if len(cmd_meta['args']) != len(args):
                self._logger.error(ValueError(f"Command '{name}' requires {len(cmd_meta['args'])} arguments, "
                                              f"but received {len(args)}."), self.__class__.__name__)
                return None
            if not cmd_meta['args']:
                if iscoroutinefunction(cmd_meta['func']):
                    return await cmd_meta['func']()
                return cmd_meta['func']()
            else:
                if iscoroutinefunction(cmd_meta['func']):
                    return await cmd_meta['func'](*args, **kwargs)
                return cmd_meta['func'](*args, **kwargs)

    @property
    def registry(self):
        """Returns the command registry."""
        return self._registry

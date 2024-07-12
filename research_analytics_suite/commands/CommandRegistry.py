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
from typing import get_type_hints, Optional, List, Dict

import aioconsole
from prettytable import PrettyTable

from research_analytics_suite.commands.utils import dynamic_import, wrap_text


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
            self._categories = {}
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
                if (_arg['type'] is not any) and not isinstance(_arg['type'], type):
                    # Attempt to resolve forward references
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
            'is_method': cmd_meta.get('is_method', False),
            '_is_command': True,
            'category': cmd_meta.get('category', 'Uncategorized'),
            'description': cmd_meta.get('description', 'No description provided.')
        }

    def discover_commands(self, package: str):
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
                        'is_method': False,
                        'category': getattr(obj, 'category', 'Uncategorized'),
                        'description': getattr(obj, 'description', 'No description provided.')
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
                                'class': obj,
                                'category': getattr(method, 'category', 'Uncategorized'),
                                'description': getattr(method, 'description', 'No description provided.')
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

    def categorize_commands(self):
        # Ensure commands are categorized
        self._categories = {}
        for cmd_name, cmd_meta in self._registry.items():
            category = cmd_meta.get('category', 'Uncategorized')
            if category not in self._categories:
                self._categories[category] = []
            self._categories[category].append((cmd_name, cmd_meta))

    def search_commands(self, keyword: str) -> List[str]:
        """
        Search commands by keyword.

        Args:
            keyword (str): The keyword to search for.

        Returns:
            List[str]: A list of command names that match the keyword.
        """
        results = []
        for cmd_name, cmd_meta in self._registry.items():
            if keyword.lower() in cmd_name.lower() or keyword.lower() in cmd_meta['description'].lower():
                results.append(cmd_name)
        return results

    def get_commands_by_category(self, category: str) -> Dict[str, dict]:
        """
        Get commands by category.

        Args:
            category (str): The category name.

        Returns:
            Dict[str, dict]: A dictionary of command names and their metadata in the specified category.
        """
        return dict(self._categories.get(category, []))

    def get_command_details(self, command_name: str) -> Optional[dict]:
        """
        Get detailed information about a command.

        Args:
            command_name (str): The name of the command.

        Returns:
            Optional[dict]: The command metadata if found, else None.
        """
        return self._registry.get(command_name)

    async def display_commands(self, page_size: int = 10):
        """
        Display available commands, their categories, and details with pagination.

        Args:
            page_size (int): Number of commands to display per page.
        """
        self.categorize_commands()  # Ensure commands are categorized before displaying
        categories = self._categories.keys()

        for category in categories:
            self._logger.info(f"\n{'-' * 40}\nCategory: {category}\n{'-' * 40}")
            commands = list(self.get_commands_by_category(category).items())
            total_commands = len(commands)
            total_pages = (total_commands + page_size - 1) // page_size

            for page in range(total_pages):
                start = page * page_size
                end = start + page_size
                self._logger.info(
                    f"\nShowing commands {start + 1} to {min(end, total_commands)} of {total_commands} in category '{category}':")

                table = PrettyTable()
                table.field_names = ["Command", "Description", "Arguments", "Return Type", "Is Method"]
                table.align["Command"] = "l"
                table.align["Description"] = "l"
                table.align["Arguments"] = "l"
                table.align["Return Type"] = "l"
                table.align["Is Method"] = "l"

                for cmd_name, cmd_meta in commands[start:end]:
                    args = cmd_meta.get('args', [])
                    formatted_args = "\n".join(
                        [f"{arg['name']}: {arg['type'].__name__}" for arg in args]) if args else "None"
                    description = cmd_meta.get('description', 'No description provided.')

                    wrapped_description = wrap_text(description, 50)
                    wrapped_args = wrap_text(formatted_args, 50)

                    if cmd_meta.get('return_type') is not None:
                        if isinstance(cmd_meta.get('return_type'), type):
                            cmd_meta['return_type'] = cmd_meta.get('return_type').__name__

                    table.add_row([
                        cmd_name,
                        wrapped_description,
                        wrapped_args,
                        cmd_meta.get('return_type', 'None'),
                        str(cmd_meta.get('is_method', 'False'))
                    ])

                self._logger.info(f'\n{table}\n')
                self._logger.info(f"Page {page + 1} of {total_pages}")
                self._logger.info("Press Enter to see the next page...")

                if page < total_pages - 1:
                    await aioconsole.ainput()

    @property
    def registry(self):
        """Returns the command registry."""
        return self._registry

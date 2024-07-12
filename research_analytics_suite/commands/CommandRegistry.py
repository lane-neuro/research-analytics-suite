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
from collections import Counter
from typing import get_type_hints, Optional, List, Dict

import aioconsole
from prettytable import PrettyTable

from research_analytics_suite.commands.utils import dynamic_import, wrap_text
from research_analytics_suite.commands.utils.text_utils import add_tags_to_commands


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
            self._current_page = 1
            self._page_size = 10
            self._current_category = None
            self._search_keyword = None
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
            'description': cmd_meta.get('description', 'No description provided.'),
            'tags': cmd_meta.get('tags', []),
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
                        'description': getattr(obj, 'description', 'No description provided.'),
                        'tags': getattr(obj, 'tags', [])
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
                                'description': getattr(method, 'description', 'No description provided.'),
                                'tags': getattr(method, 'tags', [])
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
        if name == '_help':
            return self.display_commands()

        elif name == '[':
            self.previous_page()
            return

        elif name == ']':
            self.next_page()
            return

        elif name.startswith('search'):
            if len(name.split(' ')) < 2:
                self._logger.error(ValueError("No search keyword provided. Try 'search' followed by a keyword; i.e., "
                                              "'search load' to search for commands containing the keyword 'load'."),
                                   self.__class__.__name__)
                return
            keyword = args[0]
            self.display_commands(keyword=keyword)
            return

        elif name.startswith('category'):
            if len(name.split(' ')) < 2:
                self._logger.error(ValueError("No category provided. Try 'category' followed by a category name; i.e., "
                                              "'category data' to display commands in the 'data' category."),
                                   self.__class__.__name__)
                return
            category = name.split(' ')[1]
            self.display_commands(category=category)
            return

        elif name.startswith('page'):
            if len(name.split(' ')) < 2:
                self.display_commands(self._current_category, self._search_keyword, self._current_page)
                return
            elif not name.split(' ')[1].isdigit():
                self._logger.error(ValueError("Invalid page number provided. Try 'page' followed by a number; i.e., "
                                              "'page 2' to display the second page of commands."),
                                   self.__class__.__name__)
                return
            page = int(name.split(' ')[1])
            self.display_commands(self._current_category, self._search_keyword, page)
            return

        elif name == 'categories':
            if not self._categories:
                self.categorize_commands()

            self._logger.info(f"Available categories: {', '.join(self._categories.keys())}")
            return

        cmd_meta = self._registry.get(name)
        if cmd_meta is None:
            self._logger.error(ValueError(f"Command '{name}' not found in the registry."), self.__class__.__name__)
            self._logger.info(f"Primary Command Screen:\n{self.display_commands(category=None, page=1)}")
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
        add_tags_to_commands(self._registry)

        tag_counter = Counter()
        for cmd_name, cmd_meta in self._registry.items():
            tag_counter.update(cmd_meta['tags'])
            for tag in cmd_meta['tags']:
                if tag not in self._categories:
                    self._categories[tag] = {}
                self._categories[tag][cmd_name] = cmd_meta

        for cmd_name, cmd_meta in self._registry.items():
            if cmd_meta['tags']:
                most_common_tag = tag_counter.most_common(1)[0][0]
                cmd_meta['category'] = most_common_tag
            else:
                cmd_meta['category'] = 'Uncategorized'

    def search_commands(self, keyword: str) -> List[str]:
        """
        Search commands by keyword.

        Args:
            keyword (str): The keyword to search for.

        Returns:
            List[str]: A list of command names that match the keyword.
        """
        self._search_keyword = keyword
        results = []
        for cmd_name, cmd_meta in self._registry.items():
            if keyword.lower() in cmd_name.lower() or keyword.lower() in cmd_meta['description'].lower()\
                    or keyword.lower() in cmd_meta['category'].lower() or keyword.lower() in cmd_meta['tags']\
                    or keyword.lower() in [arg['name'].lower() for arg in cmd_meta['args']]\
                    or keyword.lower() in [arg['type'].__name__.lower() for arg in cmd_meta['args']]:
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

    def display_commands(self, category: str = None, keyword: str = None, page: int = 1, column_width: int = 50):
        """
        Display available commands, their categories, and details with pagination.

        Args:
            category (str): The category of commands to display.
            keyword (str): The keyword to filter commands.
            page (int): The page number to display.
            column_width (int): The width of the columns in the table.
        """
        self._current_page = page
        self._current_category = category
        self._search_keyword = keyword

        self.categorize_commands()  # Ensure commands are categorized before displaying

        if keyword:
            commands = [(cmd_name, self._registry[cmd_name]) for cmd_name in self.search_commands(keyword)]
        elif category:
            commands = list(self.get_commands_by_category(category).items())
        else:
            commands = list(self._registry.items())

        total_commands = len(commands)
        total_pages = (total_commands + self._page_size - 1) // self._page_size

        start = (page - 1) * self._page_size
        end = start + self._page_size
        commands_to_display = commands[start:end]

        self._logger.info(f"\nShowing commands {start + 1} to {min(end, total_commands)} of {total_commands}:")

        table = PrettyTable()
        table.field_names = ["Command", "Description", "Arguments", "Return Type", "Tags", "Is Method"]
        table.align["Command"] = "l"
        table.align["Description"] = "l"
        table.align["Arguments"] = "l"
        table.align["Return Type"] = "l"
        table.align["Tags"] = "l"
        table.align["Is Method"] = "l"

        for cmd_name, cmd_meta in commands_to_display:
            args = cmd_meta.get('args', [])
            formatted_args = "\n".join(
                [f"{arg['name']}: {arg['type'].__name__}" for arg in args]) if args else "None"
            description = cmd_meta.get('description', 'No description provided.')

            wrapped_name = wrap_text(cmd_name, column_width)
            wrapped_description = wrap_text(description, column_width)
            wrapped_args = wrap_text(formatted_args, column_width)
            wrapped_tags = wrap_text(str(cmd_meta.get('tags', [])), column_width)

            if cmd_meta.get('return_type') is not None:
                if isinstance(cmd_meta.get('return_type'), type):
                    cmd_meta['return_type'] = cmd_meta.get('return_type').__name__

            table.add_row([
                wrapped_name,
                wrapped_description,
                wrapped_args,
                cmd_meta.get('return_type', 'None'),
                wrapped_tags,
                str(cmd_meta.get('is_method', 'False'))
            ])

        self._logger.info(f'\n{table}\n')
        self._logger.info(f"Page {page} of {total_pages}")
        self._logger.info("Prev Page '['\t|"
                          "\t']' Next Page\t|"
                          "\t'search <keyword>'\t|"
                          "\t'category <category>'\t|"
                          "\t'_exit' (Save & Exit)")

    def next_page(self):
        """Go to the next page of commands."""
        self._current_page += 1
        self.display_commands(self._current_category, self._search_keyword, self._current_page)

    def previous_page(self):
        """Go to the previous page of commands."""
        if self._current_page > 1:
            self._current_page -= 1
        self.display_commands(self._current_category, self._search_keyword, self._current_page)

    def clear_search(self):
        """Clears the search keyword."""
        self._search_keyword = None
        self.display_commands(self._current_category)

    def clear_category(self):
        """Clears the current category."""
        self._current_category = None
        self.display_commands(self._search_keyword)

    @property
    def registry(self):
        """Returns the command registry."""
        return self._registry

    @property
    def search(self):
        """Returns the current search keyword."""
        return self._search_keyword

    @search.setter
    def search(self, keyword):
        """Sets the current search keyword."""
        self._search_keyword = keyword
        self.display_commands(keyword=keyword)

    @property
    def categories(self):
        """Returns the command categories."""
        return self._categories

    @property
    def current_page(self):
        """Returns the current page number."""
        return self._current_page

    @property
    def page_size(self):
        """Returns the page size."""
        return self._page_size

    @page_size.setter
    def page_size(self, size):
        """Sets the page size."""
        self._page_size = size
        self.display_commands(self._current_category, self._search_keyword, self._current_page)

    @property
    def current_category(self):
        """Returns the current category."""
        return self._current_category

    @current_category.setter
    def current_category(self, category):
        """Sets the current category."""
        self._current_category = category
        self.display_commands(category=category)

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
from typing import get_type_hints, Optional, List, Dict, Tuple, Union, Iterable, ForwardRef
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
        for _arg in _args:
            if _arg['type'] is not type(any) and not isinstance(_arg['type'], type):
                _arg['type'] = _arg.get('type', type(any))
                if _arg['type'] is not any and not isinstance(_arg['type'], type):
                    # Attempt to resolve forward references
                    try:
                        _arg['type'] = dynamic_import(_arg['type'])
                    except (NameError, ImportError, AttributeError, Exception) as e:
                        self._logger.error(ValueError(f"Error resolving forward reference for {_arg['name']} in "
                                                      f"{cmd_meta['name']}: {e}"), self.__class__.__name__)
                        return

        _return_type = cmd_meta.get('return_type', [])
        if isinstance(_return_type, list):
            resolved_return_types = []
            for _rt in _return_type:
                if _rt is not any and not isinstance(_rt, type):
                    # Attempt to resolve forward references
                    try:
                        _rt = dynamic_import(_rt)
                    except (NameError, ImportError, AttributeError, Exception) as e:
                        self._logger.error(ValueError(f"Error resolving forward reference for return type in "
                                                      f"{cmd_meta['name']}: {e}"), self.__class__.__name__)
                        return
                resolved_return_types.append(self._get_type_name(_rt))
            cmd_meta['return_type'] = resolved_return_types
        else:
            try:
                if _return_type is not any and not isinstance(_return_type, type) and isinstance(_return_type, str):
                    _return_type = dynamic_import(_return_type)
                cmd_meta['return_type'] = self._get_type_name(_return_type)
            except (NameError, ImportError, AttributeError, Exception) as e:
                self._logger.error(ValueError(f"Error resolving forward reference for return type in "
                                              f"{cmd_meta['name']}: {e}"), self.__class__.__name__)
                return

        self._registry[cmd_meta['name']] = {
            'func': cmd_meta.get('func', None),
            'name': cmd_meta.get('name', None),
            'class_name': cmd_meta.get('class_name', None),
            'args': _args,
            'return_type': cmd_meta.get('return_type', []),
            'is_method': cmd_meta.get('is_method', False),
            '_is_command': True,
            'category': cmd_meta.get('category', 'Uncategorized'),
            'description': cmd_meta.get('description', 'No description provided.'),
            'tags': cmd_meta.get('tags', []),
        }

    def _get_type_name(self, type_hint):
        """
        Returns the string representation of a type hint.

        Args:
            type_hint: The type hint to convert to string.

        Returns:
            str: The string representation of the type hint.
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
                        'args': [{'name': param, 'type': get_type_hints(obj).get(param, any)} for param in
                                 inspect.signature(obj).parameters],
                        'return_type': get_type_hints(obj).get('return_type', []),
                        'is_method': False,
                        'category': getattr(obj, 'category', 'Uncategorized'),
                        'description': getattr(obj, 'description', 'No description provided.'),
                        'tags': getattr(obj, 'tags', []),
                    })
                elif inspect.isclass(obj):
                    for method_name, method in inspect.getmembers(obj, predicate=inspect.isfunction):
                        if hasattr(method, '_is_command'):
                            self._initialize_command({
                                'func': method,
                                'name': method.__name__,
                                'class_name': obj.__name__,
                                'args': [{'name': param, 'type': get_type_hints(method).get(param, any)} for param in
                                         inspect.signature(method).parameters if param != 'self'],
                                'return_type': get_type_hints(method).get('return_type', []),
                                'is_method': True,
                                'class': obj,
                                'category': getattr(method, 'category', 'Uncategorized'),
                                'description': getattr(method, 'description', 'No description provided.'),
                                'tags': getattr(method, 'tags', []),
                            })

    def register_instance(self, instance, runtime_id):
        """
        Register an instance with a runtime ID.

        Args:
            instance: The instance to register.
            runtime_id: The runtime ID associated with the instance.
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
        if name == '_help' or name == '_':
            return self.display_commands()

        elif name == '[':
            self.previous_page()
            return

        elif name == ']':
            self.next_page()
            return

        elif name.startswith('search'):
            if len(name.split(' ')) < 2 and args is None and kwargs is None:
                self._logger.error(ValueError("No search keyword provided. Try 'search' followed by a keyword; i.e., "
                                              "'search load' to search for commands containing the keyword 'load'."),
                                   self.__class__.__name__)
                return
            elif len(name.split(' ')) > 1:
                keyword = name.split(' ', 1)[1]
            else:
                keyword = args[0]

            self.display_commands(keyword=keyword)
            return

        elif name.startswith('category'):
            if len(name.split(' ')) < 2 and args is None and kwargs is None:
                self._logger.error(ValueError("No category provided. Try 'category' followed by a category name; i.e., "
                                              "'category data' to display commands in the 'data' category."),
                                   self.__class__.__name__)
                return
            elif len(name.split(' ')) > 1:
                category = name.split(' ', 1)[1]
            else:
                category = args[0]

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
            if not self._categories or self._categories == {}:
                self.categorize_commands()

            self._logger.info(f"Available categories: {', '.join(self._categories.keys())}")
            return

        elif name.startswith('details'):
            if len(name.split(' ')) < 2 and args is None and kwargs is None:
                self._logger.error(ValueError("No command name provided. Try 'details' followed by a command name;"
                                              " i.e., 'details load_data' to display details for the 'load_data' "
                                              "command."),
                                   self.__class__.__name__)
                return
            elif len(name.split(' ')) > 1:
                _name = name.split(' ', 1)[1]
            else:
                _name = args[0]

            self.display_command_details(_name)
            return

        cmd_meta = self._registry.get(name)
        if cmd_meta is None:
            self._logger.error(ValueError(f"Command '{name}' not found in the registry."), self.__class__.__name__)
            self.display_commands(category=None, page=1)
            return None

        if cmd_meta['is_method'] and runtime_id is not None:
            instance = self._instances.get(runtime_id)
            if instance is None:
                self._logger.error(ValueError(f"Instance with runtime ID '{runtime_id}' not found."),
                                   self.__class__.__name__)
                return None
            if iscoroutinefunction(cmd_meta['func']):
                _returns = await cmd_meta['func'](instance, *args, **kwargs)
                if _returns is not None:
                    return _returns
                return
            else:
                _returns = cmd_meta['func'](instance, *args, **kwargs)
                if _returns is not None:
                    return _returns
                return
        else:
            # Check whether the command requires arguments
            if len(cmd_meta['args']) != len(args):
                self._logger.error(ValueError(f"Command '{name}' requires {len(cmd_meta['args'])} arguments, "
                                              f"but received {len(args)}."), self.__class__.__name__)
                return None
            if not cmd_meta['args']:
                if iscoroutinefunction(cmd_meta['func']):
                    _returns = await cmd_meta['func']()
                    if _returns is not None:
                        return _returns
                    return
                else:
                    _returns = cmd_meta['func']()
                    if _returns is not None:
                        return _returns
                    return
            else:
                if iscoroutinefunction(cmd_meta['func']):
                    _returns = await cmd_meta['func'](*args, **kwargs)
                    if _returns is not None:
                        return _returns
                    return
                else:
                    _returns = cmd_meta['func'](*args, **kwargs)
                    if _returns is not None:
                        return _returns
                    return

    def categorize_commands(self):
        # Ensure commands are categorized
        self._categories = {}
        self._registry = add_tags_to_commands(self._registry)

        tag_counter = Counter()
        for cmd_name, cmd_meta in self._registry.items():
            tag_counter.update(cmd_meta['tags'])
            for tag in cmd_meta['tags']:
                if tag not in self._categories:
                    self._categories[tag] = {}
                self._categories[tag][cmd_name] = cmd_meta

        for cmd_name, cmd_meta in self._registry.items():
            if cmd_meta['tags'] is not None and len(cmd_meta['tags']) > 0:
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
                    or keyword.lower() in [arg['type'].__name__.lower() for arg in cmd_meta['args']]\
                    or keyword.lower() in [rt.lower() for rt in cmd_meta['return_type']]:
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

    def display_commands(self, category: str = None, keyword: str = None, page: int = 1, column_width: int = 60):
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

        table = PrettyTable()
        table.field_names = ["Command", "Description", "Arguments", "Return Types", "Tags", "Is Method"]
        table.align["Command"] = "l"
        table.align["Description"] = "l"
        table.align["Arguments"] = "l"
        table.align["Return Types"] = "l"
        table.align["Tags"] = "l"
        table.align["Is Method"] = "l"

        for cmd_name, cmd_meta in commands_to_display:

            # Format arguments
            args = cmd_meta.get('args', [])
            formatted_args = f""
            for arg in args if args else []:
                _name = arg['name']
                _type = arg['type'].__name__
                if _type.lower() == 'any':
                    formatted_args += f" - {_name}\n"
                else:
                    formatted_args += f" - {_name} ({_type})\n"

            description = cmd_meta.get('description', 'No description provided.')

            # Format return types
            return_types = cmd_meta.get('return_type', [])
            formatted_return_types = f""
            if return_types is not []:
                if len(return_types) > 1 and isinstance(return_types, list):
                    for rt in return_types:
                        formatted_return_types += f" - {rt}\n"
                elif return_types:
                    formatted_return_types += f" - {return_types}\n"

            # Wrap text to fit in the table
            wrapped_name = wrap_text(cmd_name, column_width)
            wrapped_description = wrap_text(description, column_width)
            wrapped_args = wrap_text(formatted_args, column_width)
            wrapped_return_types = wrap_text(formatted_return_types, column_width)
            wrapped_tags = wrap_text(str(cmd_meta.get('tags', [])), column_width)

            table.add_row([
                wrapped_name,
                wrapped_description,
                wrapped_args,
                wrapped_return_types,
                wrapped_tags,
                str(cmd_meta.get('is_method', 'False'))
            ])

        self._logger.info(f'\n{table}\n')
        self._logger.info(f"Page ({page} of {total_pages}):\tcommands [{start + 1} - {min(end, total_commands)}] of ({total_commands})")
        self._logger.info("Prev Page '['\t|"
                          "\t']' Next Page\t|"
                          "\t'search <keyword>'\t|"
                          "\t'category <category>'\t|"
                          "\t'_exit' (Save & Exit)")

    def display_command_details(self, command_name: str):
        """
        Display detailed information about a command.

        Args:
            command_name (str): The name of the command to display details for.
        """
        cmd_meta = self.get_command_details(command_name)
        if cmd_meta is None:
            self._logger.error(ValueError(f"Command '{command_name}' not found in the registry."), self.__class__.__name__)
            return

        self._logger.info(f"\nCommand: {command_name}")
        self._logger.info(f"  Category:\t{cmd_meta.get('category', 'Uncategorized')}")
        self._logger.info(f"  Description:\t{cmd_meta.get('description', 'No description provided.')}")
        self._logger.info(f"  tags:\t{cmd_meta.get('tags', [])}")
        self._logger.info(f"  is_method:\t{cmd_meta.get('is_method', False)}")
        if cmd_meta.get('is_method', True):
            self._logger.info(f"  Class:\t{cmd_meta.get('class_name', 'None')}")
            self._logger.info(f"  Method:\t{cmd_meta.get('name', 'None')}")
        else:
            self._logger.info(f"  Function:\t{cmd_meta.get('name', 'None')}")
        self._logger.info('--------------------------------------------------------------------')
        if cmd_meta.get('args', []) is not [] or None:
            self._logger.info(
            f"** [NOTE] An argument of type 'any' means the argument type was not specified by the developer, it does\n"
            f"  ... not mean you can pass any argument type. Please refer to the source code or contact the command's\n"
            f"  ... developer for more information.")
            self._logger.info(f"  Arguments:")
            for arg in cmd_meta.get('args', []):
                self._logger.info(f"\t-\t{arg['name']} ({arg['type'].__name__})")

        _return_types = cmd_meta.get('return_type', [])
        if _return_types is not None:
            if len(_return_types) > 1 and isinstance(_return_types, Iterable):
                self._logger.info(f"   Return Types:")
                for _return_type in _return_types:
                    self._logger.info(f"\t-\t({_return_type})")
            else:
                self._logger.info(f"   Return Type: ({_return_types[0]})")

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

    @registry.setter
    def registry(self, registry):
        """Sets the command registry."""
        self._registry = registry

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

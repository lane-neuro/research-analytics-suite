"""
DisplayManager Module

This module defines the DisplayManager class, which manages the display of commands within the Research Analytics Suite.
It provides methods to display commands, search commands, and display command details.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from prettytable import PrettyTable
from research_analytics_suite.commands.utils import wrap_text
from research_analytics_suite.commands.utils.text_utils import add_tags_to_commands, get_function_body


class DisplayManager:
    """Class that manages the display of commands."""

    def __init__(self, registration_manager):
        """Initialize the DisplayManager with the registration manager.

        Args:
            registration_manager: The RegistrationManager instance.
        """
        from research_analytics_suite.utils import CustomLogger
        self._logger = CustomLogger()
        self._registration_manager = registration_manager
        self._current_page = 1
        self._page_size = 10
        self._current_category = None
        self._search_keyword = None

    def display_commands(self, category: str = None, keyword: str = None, page: int = 1, column_width: int = 30):
        """Display commands with optional filtering by category, keyword, and pagination.

        Args:
            category (str, optional): Filter commands by category.
            keyword (str, optional): Filter commands by keyword.
            page (int, optional): Page number for pagination.
            column_width (int, optional): Column width for display formatting.
        """
        self._current_page = page
        self._current_category = category
        self._search_keyword = keyword

        self.categorize_commands()

        commands = dict[str, dict](self._registration_manager.registry)

        if keyword:
            commands = {k: v for k, v in self._registration_manager.registry.items() if keyword.lower() in k.lower()}
        elif category:
            commands = self._get_commands_by_category(category)

        total_commands = len(commands)
        total_pages = (total_commands + self._page_size - 1) // self._page_size

        start = (page - 1) * self._page_size
        end = start + self._page_size
        commands_to_display = dict[str, dict]()

        for i, (cmd_name, cmd_meta) in enumerate(commands.items()):
            if start <= i < end:
                commands_to_display[cmd_name] = cmd_meta

        table = PrettyTable()
        table.field_names = ["class", "command", "description", "input arguments", "return types", "search tags"]
        table.align = "l"

        for cmd_name, cmd_meta in commands_to_display.items():
            args = cmd_meta['args']
            formatted_args = ""
            for arg in args if args else []:
                _name = arg['name']
                _type = arg['type'].__name__
                formatted_args += f"- {_name} ({_type})\n" if _type.lower() != 'any' else f"- {_name}\n"

            description = cmd_meta['description']

            return_types = cmd_meta['return_type']
            formatted_return_types = f""
            if return_types:
                if isinstance(return_types, list) and len(return_types) > 1:
                    for rt in return_types:
                        if isinstance(rt, type) and rt != 'NoneType':
                            formatted_return_types += f"- {rt}\n"
                else:
                    if isinstance(return_types, type) and return_types != 'NoneType':
                        formatted_return_types += f"- {return_types.__name__}\n"
            else:
                formatted_return_types = f"- None"

            table.add_row([
                cmd_meta.get('class_name', None),
                wrap_text(cmd_name, column_width),
                wrap_text(description, column_width),
                wrap_text(formatted_args, column_width),
                wrap_text(formatted_return_types, column_width),
                wrap_text(str(cmd_meta['tags']), column_width),
            ])

        self._logger.info(f'\n{table}\n')
        self._logger.info(
            f"Page ({page} of {total_pages}):\tcommands [{start + 1} - {min(end, total_commands)}] of ({total_commands})")
        self._logger.info("Prev Page '['\t|"
                          "\t']' Next Page\t|"
                          "\t'search <keyword>'\t|"
                          "\t'category <category>'\t|"
                          "\t'_exit' (Save & Exit)")

    def display_command_details(self, command_name: str):
        """Display details of a specific command.

        Args:
            command_name (str): The name of the command to display details for.
        """
        cmd_meta = self._registration_manager.registry.get(command_name)
        if cmd_meta is None:
            self._logger.error(ValueError(f"Command '{command_name}' not found in the registry."))
            return

        _command_name = f"{cmd_meta.get('name', None)}"
        if cmd_meta.get('class_name', None) is not None:
            _command_name += f"\t({cmd_meta.get('class_name')})"

        _args = cmd_meta.get('args', [dict(name='None', type='None')])
        _formatted_args = f"  "
        if _args:
            if len(_args) > 1 and isinstance(_args, list):
                if _args[0].get('type', None) is not None:
                    _formatted_args += f"input arguments:"
                    for _arg in _args:
                        _formatted_args += f"\n\t-\t{_arg['name']} ({_arg['type'].__name__})"
                else:
                    _formatted_args += f"input arguments:"
                    for _arg in _args:
                        _formatted_args += f"\n\t-\t{_arg}"
            else:
                if _args[0].get('type', None) is not None:
                    _formatted_args += f"input argument:\t\t{_args[0]['name']} ({_args[0]['type'].__name__})"
                else:
                    _formatted_args += f"input argument:\t\t{_args[0]}"
        else:
            _formatted_args += f"input arguments:\t\tNone"

        _returns = cmd_meta.get('return_type', None)
        _return_types = f"  "
        if _returns:
            if len(_return_types) > 1 and isinstance(_return_types, list):
                _return_types += f"return types:"
                for _return_type in _return_types:
                    _return_types += f"\n\t-\t({_return_type})"
            elif isinstance(_returns, type):
                _return_types += f"return type:\t\t\t{_returns.__name__}"
            else:
                _return_types += f"return type:\t\t\tNone"
        else:
            _return_types += f"return type:\t\t\tNone"

        _formatted_func = f"  --- function ---"
        _func = cmd_meta.get('func', None)
        if _func:
            _lines = get_function_body(_func)
            _formatted_func += f"\n{_lines.strip()}"
        else:
            _formatted_func = f"  function:\t\t\tNone"
        _formatted_func += f"\n   ------------------"

        self._logger.info('==================================================================================')
        self._logger.info(f"  command:\t\t\t\t{_command_name}")
        self._logger.info(f"  category:\t\t\t\t{cmd_meta.get('category', 'Uncategorized')}")
        self._logger.info(f"  description:\t\t\t{cmd_meta.get('description', None)}")
        self._logger.info(f"  search tags:\t\t\t{cmd_meta.get('tags', [])}")
        self._logger.info(_formatted_args)
        self._logger.info(_return_types)
        self._logger.info(_formatted_func)
        self._logger.info(f"  ** [NOTE] An argument of type 'any' means the argument type was not specified "
                          f"\n  ... by the developer, it does not mean you can pass any argument type. Please refer "
                          f"\n  ... to the source code or contact the command's developer for more information.")
        self._logger.info('==================================================================================')

    def categorize_commands(self):
        """Categorize commands based on their metadata."""
        add_tags_to_commands(self._registration_manager.registry)
        for cmd_name, cmd_meta in self._registration_manager.registry.items():
            category = cmd_meta.get('category', 'Uncategorized')
            if category not in self._registration_manager.categories:
                self._registration_manager.categories[category] = {}
            self._registration_manager.categories[category][cmd_name] = cmd_meta

    def _search_commands(self, keyword: str):
        """Search commands by keyword.

        Args:
            keyword (str): The keyword to search for.

        Returns:
            List of command names that match the keyword.
        """
        self._search_keyword = keyword
        results = []
        for cmd_name, cmd_meta in self._registration_manager.registry.items():
            if keyword.lower() in cmd_name.lower() or \
                    keyword.lower() in cmd_meta.get('description', '').lower() or \
                    keyword.lower() in cmd_meta.get('category', '').lower() or \
                    keyword.lower() in cmd_meta.get('tags', '') or \
                    keyword.lower() in [arg['name'].lower() for arg in cmd_meta.get('args', None)] or \
                    keyword.lower() in [arg['type'].__name__.lower() for arg in cmd_meta.get('args', None)] or \
                    keyword.lower() in [rt.lower() for rt in cmd_meta.get('return_type', None)]:
                results.append(cmd_name)
        return results

    def _get_commands_by_category(self, category: str):
        """Get commands by category.

        Args:
            category (str): The category to filter commands by.

        Returns:
            Dictionary of commands in the specified category.
        """
        return dict(self._registration_manager.categories.get(category, []))

    def clear_search(self):
        """Clear the current search."""
        self._search_keyword = None
        self.display_commands(self._current_category)

    def clear_category(self):
        """Clear the current category."""
        self._current_category = None
        self.display_commands(self._search_keyword)

    @property
    def search(self):
        """Get the current search keyword."""
        return self._search_keyword

    @search.setter
    def search(self, keyword):
        """Set the current search keyword.

        Args:
            keyword (str): The keyword to search for.
        """
        self._search_keyword = keyword
        self.display_commands(keyword=keyword)

    @property
    def current_category(self):
        """Get the current category."""
        return self._current_category

    @current_category.setter
    def current_category(self, category):
        """Set the current category.

        Args:
            category (str): The category to filter commands by.
        """
        self._current_category = category
        self.display_commands(category=category)

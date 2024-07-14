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
from research_analytics_suite.commands.utils.text_utils import add_tags_to_commands


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

    def display_commands(self, category: str = None, keyword: str = None, page: int = 1, column_width: int = 60):
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

        if keyword:
            commands = [(cmd_name, self._registration_manager.registry[cmd_name]) for cmd_name in
                        self._search_commands(keyword)]
        elif category:
            commands = list(self._get_commands_by_category(category).items())
        else:
            commands = list(self._registration_manager.registry.items())

        total_commands = len(commands)
        total_pages = (total_commands + self._page_size - 1) // self._page_size

        start = (page - 1) * self._page_size
        end = start + self._page_size
        commands_to_display = commands[start:end]

        table = PrettyTable()
        table.field_names = ["Command", "Description", "Arguments", "Return Types", "Tags", "Is Method"]
        table.align = "l"

        for cmd_name, cmd_meta in commands_to_display:
            args = cmd_meta.get('args', [])
            formatted_args = f""
            for arg in args if args else []:
                _name = arg['name']
                _type = arg['type'].__name__
                formatted_args += f" - {_name} ({_type})\n" if _type.lower() != 'any' else f" - {_name}\n"

            description = cmd_meta.get('description', 'No description provided.')

            return_types = cmd_meta.get('return_type', [])
            formatted_return_types = f""
            if return_types:
                if len(return_types) > 1 and isinstance(return_types, list):
                    for rt in return_types:
                        formatted_return_types += f" - {rt}\n"
                else:
                    formatted_return_types += f" - {return_types}\n"

            table.add_row([
                wrap_text(cmd_name, column_width),
                wrap_text(description, column_width),
                wrap_text(formatted_args, column_width),
                wrap_text(formatted_return_types, column_width),
                wrap_text(str(cmd_meta.get('tags', [])), column_width),
                str(cmd_meta.get('is_method', 'False'))
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
            self._logger.info(f"** [NOTE] An argument of type 'any' means the argument type was not specified by the "
                              f"developer, it does\n"
                              f"  ... not mean you can pass any argument type. Please refer to the source code or "
                              f"contact the command's\n ... developer for more information.")
            self._logger.info(f"  Arguments:")
            for arg in cmd_meta.get('args', []):
                self._logger.info(f"\t-\t{arg['name']} ({arg['type'].__name__})")

        _return_types = cmd_meta.get('return_type', [])
        if _return_types is not None:
            if len(_return_types) > 1 and isinstance(_return_types, list):
                self._logger.info(f"   Return Types:")
                for _return_type in _return_types:
                    self._logger.info(f"\t-\t({_return_type})")
            else:
                self._logger.info(f"   Return Type: ({_return_types[0]})")

    def categorize_commands(self):
        """Categorize commands based on their metadata."""
        add_tags_to_commands(self._registration_manager.registry)
        self._registration_manager._categories = {}
        for cmd_name, cmd_meta in self._registration_manager.registry.items():
            category = cmd_meta.get('category', 'Uncategorized')
            if category not in self._registration_manager._categories:
                self._registration_manager._categories[category] = {}
            self._registration_manager._categories[category][cmd_name] = cmd_meta

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
                    keyword.lower() in [arg['name'].lower() for arg in cmd_meta.get('args', [])] or \
                    keyword.lower() in [arg['type'].__name__.lower() for arg in cmd_meta.get('args', [])] or \
                    keyword.lower() in [rt.lower() for rt in cmd_meta.get('return_type', [])]:
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

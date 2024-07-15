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

import asyncio

from research_analytics_suite.commands.registry.RegistrationManager import RegistrationManager
from research_analytics_suite.commands.registry.CommandExecutor import CommandExecutor
from research_analytics_suite.commands.registry.DisplayManager import DisplayManager
from research_analytics_suite.commands.registry.PaginationManager import PaginationManager


class CommandRegistry:
    """Singleton class that manages the registration and execution of commands."""
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls):
        """Ensure only one instance of CommandRegistry exists."""
        if cls._instance is None:
            cls._instance = super(CommandRegistry, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the CommandRegistry with default values."""
        if not hasattr(self, '_initialized'):
            self._logger = None
            self._config = None
            self._operation_control = None
            self._library_manifest = None
            self._workspace = None

            self._registration_manager = None
            self._command_executor = None
            self._display_manager = None
            self._pagination_manager = None

            self._initialized = False

    async def initialize(self):
        """Initialize the CommandRegistry and its components asynchronously."""
        if not self._initialized:
            async with self._lock:
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

                    self._registration_manager = RegistrationManager()
                    await self._registration_manager.initialize()

                    self._command_executor = CommandExecutor(self._registration_manager)
                    await self._command_executor.initialize()

                    self._display_manager = DisplayManager(self._registration_manager)
                    self._pagination_manager = PaginationManager(self._display_manager)

                    self._initialized = True

    def discover_commands(self, package: str):
        """Discover commands in the specified package.

        Args:
            package (str): The package to search for commands.
        """
        self._registration_manager.discover_commands(package)

    def register_instance(self, instance, runtime_id):
        """Register an instance with a runtime ID.

        Args:
            instance: The instance to register.
            runtime_id: The runtime ID of the instance.
        """
        self._registration_manager.register_instance(instance, runtime_id)

    async def execute_command(self, name, runtime_id=None, *args, **kwargs):
        """Execute a command by name.

        Args:
            name (str): The name of the command.
            runtime_id: The runtime ID for instance-specific methods.
            *args: Positional arguments for the command.
            **kwargs: Keyword arguments for the command.

        Returns:
            The result of the command execution.
        """
        if name == '_help' or name == '_':
            self._display_manager.display_commands()
            return

        elif name == '[':
            self._pagination_manager.previous_page()
            return

        elif name == ']':
            self._pagination_manager.next_page()
            return

        elif name.startswith('search'):
            keyword = name.split(' ', 1)[1] if len(name.split(' ')) > 1 else \
                (args[0] if args else kwargs.get('keyword', None))
            self._display_manager.display_commands(keyword=keyword)
            return

        elif name.startswith('category'):
            category = name.split(' ', 1)[1] if len(name.split(' ')) > 1 else \
                (args[0] if args else kwargs.get('category', None))
            self._display_manager.display_commands(category=category)
            return

        elif name.startswith('page'):
            page = int(name.split(' ')[1]) if len(name.split(' ')) > 1 and name.split(' ')[1].isdigit() else 1
            self._display_manager.display_commands(self._display_manager.current_category,
                                                   self._display_manager.search, page)
            return

        elif name == 'categories':
            self._display_manager.categorize_commands()
            self._logger.info(f"Available categories: {', '.join(self._registration_manager.categories.keys())}")
            return

        elif name.startswith('details'):
            command_name = name.split(' ', 1)[1] if len(name.split(' ')) > 1 else \
                (args[0] if args else kwargs.get('command_name', None))
            if command_name:
                self._display_manager.display_command_details(command_name)
            else:
                self._logger.error(ValueError("No command name provided. Try 'details' followed by a command name; "
                                              "i.e., 'details load_data' to display details for the 'load_data' "
                                              "command."), self.__class__.__name__)
            return

        return await self._command_executor.execute_command(name, runtime_id, *args, **kwargs)

    def next_page(self):
        """Navigate to the next page."""
        self._pagination_manager.next_page()

    def previous_page(self):
        """Navigate to the previous page."""
        self._pagination_manager.previous_page()

    def clear_search(self):
        """Clear the current search."""
        self._display_manager.clear_search()

    def clear_category(self):
        """Clear the current category."""
        self._display_manager.clear_category()

    def display_commands(self, category: str = None, keyword: str = None, page: int = 1, column_width: int = 60):
        """Display commands with optional filtering by category, keyword, and pagination.

        Args:
            category (str, optional): Filter commands by category.
            keyword (str, optional): Filter commands by keyword.
            page (int, optional): Page number for pagination.
            column_width (int, optional): Column width for display formatting.
        """
        self._display_manager.display_commands(category, keyword, page, column_width)

    def display_command_details(self, command_name: str):
        """Display details of a specific command.

        Args:
            command_name (str): The name of the command to display details for.
        """
        self._display_manager.display_command_details(command_name)

    @property
    def registry(self):
        """Get the command registry."""
        return self._registration_manager.registry

    @registry.setter
    def registry(self, registry):
        """Set the command registry."""
        self._registration_manager.registry = registry

    @property
    def search(self):
        """Get the current search keyword."""
        return self._display_manager.search

    @search.setter
    def search(self, keyword):
        """Set the current search keyword."""
        self._display_manager.search = keyword

    @property
    def categories(self):
        """Get the available categories."""
        return self._registration_manager.categories

    @property
    def current_page(self):
        """Get the current page number."""
        return self._pagination_manager.current_page

    @property
    def page_size(self):
        """Get the page size."""
        return self._pagination_manager.page_size

    @page_size.setter
    def page_size(self, size):
        """Set the page size."""
        self._pagination_manager.page_size = size

    @property
    def current_category(self):
        """Get the current category."""
        return self._display_manager.current_category

    @current_category.setter
    def current_category(self, category):
        """Set the current category."""
        self._display_manager.current_category = category

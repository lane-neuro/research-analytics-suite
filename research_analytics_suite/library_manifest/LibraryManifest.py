import asyncio
import os
import importlib
import pkgutil

from research_analytics_suite.commands import command, register_commands
from research_analytics_suite.library_manifest.Category import Category
from research_analytics_suite.library_manifest.CategoryID import CategoryID
from research_analytics_suite.library_manifest.utils import check_verified


@register_commands
class LibraryManifest:
    """
    The LibraryManifest class is responsible for managing the library of operations available to the user.
    """
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LibraryManifest, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initialize the LibraryManifest class.
        """
        if not hasattr(self, '_initialized'):
            from research_analytics_suite.utils import Config
            self._config = Config()

            from research_analytics_suite.utils import CustomLogger
            self._logger = CustomLogger()

            self._categories = {}
            self._library = {}

            self._initialized = False

    async def initialize(self):
        """
        Initialize the library manifest by building the base library.
        """
        if not self._initialized:
            async with LibraryManifest._lock:
                if not self._initialized:
                    await self.build_base_library()
                    self._initialized = True

    @command
    def get_library(self):
        return self._library

    @command
    def add_category(self, category_id, name):
        category = Category(category_id, name)
        self._categories[category_id] = category

    @command
    def add_operation_from_attributes(self, operation_attributes):
        category_id = operation_attributes.category_id
        if category_id in self._categories:
            self._categories[category_id].register_operation(operation_attributes)

    async def build_base_library(self):
        def add_categories(parent_id, parent_name, subcategories):
            for sub_key, sub_data in subcategories.items():
                sub_id, sub_name, sub_subcategories = sub_data
                _category_id = sub_id
                category_name = f"{sub_name}"
                subcategory = Category(_category_id, category_name)
                self._categories[_category_id] = subcategory
                self._categories[parent_id].add_subcategory(subcategory)
                if isinstance(sub_subcategories, dict):
                    add_categories(_category_id, category_name, sub_subcategories)

        for main_cat in CategoryID:
            self._logger.debug(f"Initializing main category: {main_cat.name}")
            main_category = Category(main_cat.id, main_cat.name)
            self._categories[main_cat.id] = main_category
            if isinstance(main_cat.subcategories, dict):
                add_categories(main_cat.id, main_cat.name, main_cat.subcategories)

        for category in self._categories.values():
            self._logger.debug(f"Initializing category: {category.name}")
            await category.initialize()

        await self._populate_verified_operations()

        for category_id, category in self._categories.items():
            operations = []
            for operation in category.operations or []:
                if operation == {}:
                    continue

                from research_analytics_suite.operation_manager.operations.core.memory.OperationAttributes import OperationAttributes
                if isinstance(operation, OperationAttributes):
                    operations.append(operation.export_attributes())
                elif isinstance(operation, dict) and operation != {}:
                    operations.append(operation)
                else:
                    self._logger.error(Exception(f"Invalid operation type: {type(operation)}"))

            self._library[category_id] = operations
        self._logger.debug("Completed build_base_library")

    async def _populate_verified_operations(self):
        self._logger.debug("Starting _populate_verified_operations")
        try:
            package = importlib.import_module('operation_library')
            for _, module_name, _ in pkgutil.iter_modules(package.__path__):
                if module_name == '__init__':
                    continue

                self._logger.debug(f"Importing module: {module_name}")
                module = importlib.import_module(f'operation_library.{module_name}').__dict__.get(module_name)

                from research_analytics_suite.operation_manager.operations.core.memory import get_attributes_from_module
                self.add_operation_from_attributes(await get_attributes_from_module(module))
        except ModuleNotFoundError:
            self._logger.error(Exception("operation_library module not found"))
        self._logger.debug("Completed _populate_verified_operations")

    @command
    async def load_user_library(self):
        self._logger.debug("Starting load_user_library")
        _user_dir = os.path.normpath(os.path.join(self._config.BASE_DIR, 'operations'))
        _local_operation_dir = os.path.normpath(os.path.join(
            self._config.BASE_DIR, 'workspaces', self._config.WORKSPACE_NAME,
            self._config.WORKSPACE_OPERATIONS_DIR))
        if not os.path.exists(_local_operation_dir) or not os.path.exists(_user_dir):
            self._logger.warning("Operation directories do not exist")
            return []

        operation_files = [os.path.join(_local_operation_dir, f) for f in os.listdir(_local_operation_dir)
                           if f.endswith('.json')]
        operation_files += [os.path.join(_user_dir, f) for f in os.listdir(_user_dir) if f.endswith('.json')]

        for _op in operation_files:
            self._logger.debug(f"Loading operation from file: {_op}")
            from research_analytics_suite.operation_manager.operations.core.memory import get_attributes_from_disk
            self.add_operation_from_attributes(await get_attributes_from_disk(_op))
        self._logger.debug("Completed load_user_library")

    @command
    def get_categories(self):
        return self._categories.items()

    async def _update_user_manifest(self):  # pragma: no cover
        ...


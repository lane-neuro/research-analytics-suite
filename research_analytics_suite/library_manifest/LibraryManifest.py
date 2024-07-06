"""
LibraryManifest Module

The LibraryManifest class module is used to manage the library manifest. It handles
initialization, adding categories and operations, verifying categories, and loading user libraries.

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
import os
import importlib
import pkgutil
from research_analytics_suite.library_manifest.Category import Category
from research_analytics_suite.library_manifest.CategoryID import CategoryID
from research_analytics_suite.library_manifest.utils import check_verified
from research_analytics_suite.operation_manager.operations.core.memory.OperationAttributes import \
    get_attributes_from_disk


class LibraryManifest:
    """
    LibraryManifest class is used to manage the library manifest.

    Attributes:
        _categories (dict): A dictionary to store categories.
        _library (dict): A dictionary to store the library operations.
        _initialized (bool): A flag indicating if the manifest is initialized.
    """

    def __init__(self):
        from research_analytics_suite.utils import Config
        self._config = Config()

        from research_analytics_suite.utils import CustomLogger
        self._logger = CustomLogger()

        self._categories = {}
        self._library = {}
        self._initialized = False

    async def initialize(self):
        """
        Initializes the LibraryManifest by building the base library.
        """
        await self.build_base_library()
        self._initialized = True

    def get_library(self):
        """
        Returns the library dictionary.
        """
        return self._library

    def add_category(self, category_id, name):
        """
        Adds a new category to the manifest.

        Args:
            category_id (int): The unique identifier of the category.
            name (str): The name of the category.
        """
        category = Category(category_id, name)
        self._categories[category_id] = category

    def add_operation_from_attributes(self, operation_attributes):
        """
        Adds an operation from its attributes to the corresponding category.

        Args:
            operation_attributes (OperationAttributes): The operation attributes.
        """
        category_id = operation_attributes.category_id
        if category_id in self._categories:
            self._categories[category_id].register_operation(operation_attributes)

    def is_verified(self, category_id):
        """
        Checks if a category is verified.

        Args:
            category_id (int): The unique identifier of the category.

        Returns:
            bool: True if the category is verified, False otherwise.
        """
        if category_id in self._categories:
            return check_verified(category_id)
        return False

    async def build_base_library(self):
        """
        Builds the base library by adding categories and initializing them.
        """
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
            main_category = Category(main_cat.id, main_cat.name)
            self._categories[main_cat.id] = main_category
            if isinstance(main_cat.subcategories, dict):
                add_categories(main_cat.id, main_cat.name, main_cat.subcategories)

        for category in self._categories.values():
            await category.initialize()

        self._populate_verified_operations()

        for category_id, category in self._categories.items():
            operations = []
            for operation in category.operations:
                if hasattr(operation, 'export_attributes'):
                    operations.append(operation.export_attributes())
                else:
                    operations.append(operation)
            self._library[category_id] = operations

    def _populate_verified_operations(self):
        """
        Populates the library with verified operations from the operation library.
        """
        try:
            package = importlib.import_module('operation_library')
            for _, module_name, _ in pkgutil.iter_modules(package.__path__):
                module = importlib.import_module(f'operation_library.{module_name}')
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if hasattr(attr, 'is_verified_operation') and attr.is_verified_operation:
                        self._library[attr.operation_id] = attr
        except ModuleNotFoundError:
            pass

    async def load_user_library(self):
        """
        Loads the user library by reading operation files from disk.
        """
        _user_dir = os.path.normpath(os.path.join(self._config.BASE_DIR, 'operations'))
        _local_operation_dir = os.path.normpath(os.path.join(
            self._config.BASE_DIR, 'workspaces', self._config.WORKSPACE_NAME,
            self._config.WORKSPACE_OPERATIONS_DIR))
        if not os.path.exists(_local_operation_dir) or not os.path.exists(_user_dir):
            return []

        operation_files = [os.path.join(_local_operation_dir, f) for f in os.listdir(_local_operation_dir)
                           if f.endswith('.json')]
        operation_files += [os.path.join(_user_dir, f) for f in os.listdir(_user_dir) if f.endswith('.json')]

        for _op in operation_files:
            self.add_operation_from_attributes(await get_attributes_from_disk(_op))

    def get_categories(self):
        """
        Returns the categories dictionary.
        """
        return self._categories.items()

    async def _update_user_manifest(self):
        """
        Updates the user manifest with some asynchronous operation.
        """
        await asyncio.sleep(1)  # Simulate some async operation
        self._initialized = True

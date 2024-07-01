"""
LibraryManifest

This class is responsible for managing the operation library manifest. It is responsible for keeping track of all the
_categories and their verified status.

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
import pkgutil
import importlib
from .utils import check_verified


class LibraryManifest:
    """
    LibraryManifest class is responsible for managing the operation library manifest. It is responsible for keeping
    track of all the categories and their verified status.

    Attributes:
        _categories (dict): A dictionary to store all the categories.

    """
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """
        Initializes the LibraryManifest with an empty dictionary to store categories.
        """
        if not hasattr(self, '_initialized'):
            self._categories = {}
            self._initialized = False

    async def initialize(self):
        """
        Initializes the LibraryManifest.

        This method is called asynchronously to initialize the LibraryManifest.
        """
        if not self._initialized:
            async with LibraryManifest._lock:
                if not self._initialized:
                    self.build_operation_library()
                    self._initialized = True

    def add_category(self, category):
        self._categories[category.id] = category

    def is_verified(self, category_id):
        category = self._categories.get(category_id, None)
        if category:
            return category.verified
        return False

    def build_operation_library(self):
        library = {}

        # Discover verified operations in the current package
        self.discover_verified_operations()

        # Discover user-created operations in the filesystem
        operation_files = self.discover_user_operations()

        for operation_file in operation_files:
            operation_name = os.path.splitext(os.path.basename(operation_file))[0]
            category_id, category_name = self.get_category_from_operation(operation_name)

            if category_id not in self._categories:
                from research_analytics_suite.operation_library import Category
                self._categories[category_id] = Category(category_id, category_name)

            # TODO: Add logic to check if operation is verified
            # operation = Operation(operation_name, f"Description for {operation_name}")
            # self._categories[category_id].add_operation(operation)

        for category_id, category in self._categories.items():
            library[category_id] = {
                'name': category.name,
                'verified': category.verified,
                'operations': []
            }
            for operation in category.operations:
                operation_info = {
                    'name': operation.name,
                    'description': operation.description,
                    'verified': check_verified(operation.name)
                }
                library[category_id]['operations'].append(operation_info)

        return library

    async def maintain_library(self):
        # Logic to maintain the library by checking for new operations
        # and updating the library accordingly
        pass

    def discover_verified_operations(self):
        package = importlib.import_module('operation_library')
        for _, module_name, _ in pkgutil.iter_modules(package.__path__):
            if module_name not in self._categories:
                category_id, category_name = self.get_category_from_operation(module_name)

                from research_analytics_suite.operation_library import Category
                category = Category(category_id, category_name)

                category.verified = True
                self._categories[category_id] = category
                # TODO: Add logic to check if operation is verified
                # operation = Operation(module_name, f"Description for {module_name}")
                # category.add_operation(operation)

    def discover_user_operations(self):
        # Logic to discover user-created operations in the filesystem
        # Assuming operations are stored in 'user_operations' directory for this example
        operation_dir = 'user_operations'
        if not os.path.exists(operation_dir):
            return []

        operation_files = [os.path.join(operation_dir, f) for f in os.listdir(operation_dir) if f.endswith('.py')]
        return operation_files

    def get_category_from_operation(self, operation_name):
        # Logic to determine category from operation name
        # For simplicity, let's assume category ID and name are derived from operation name
        category_id = operation_name.split('_')[0]
        category_name = f"Category {category_id.capitalize()}"
        return category_id, category_name

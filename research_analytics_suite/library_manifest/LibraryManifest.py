"""
LibraryManifest

This class is responsible for managing the operation library manifest. It is responsible for keeping track of all the
categories and their verified status.

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
from research_analytics_suite.library_manifest.utils import check_verified
from research_analytics_suite.library_manifest.Category import Category


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
            from research_analytics_suite.utils import Config
            self._config = Config()

            from research_analytics_suite.utils import CustomLogger
            self._logger = CustomLogger()

            from research_analytics_suite.operation_manager.control.OperationControl import OperationControl
            self._operation_control = OperationControl()

            self._update_operation = None

            self._categories = {}
            self._library = {}
            self._initialized = False

    async def initialize(self):
        """
        Initializes the LibraryManifest.

        This method is called asynchronously to initialize the LibraryManifest.
        """
        if not self._initialized:
            async with LibraryManifest._lock:
                if not self._initialized:
                    await self.build_base_library()

                    from research_analytics_suite.operation_manager import BaseOperation
                    self._update_operation = await self._operation_control.operation_manager.add_operation_with_parameters(
                        operation_type=BaseOperation, name="sys_LibraryUpdateTask",
                        action=self._update_user_manifest, persistent=True, concurrent=True)
                    self._update_operation.is_ready = True

                    self._initialized = True

    def get_library(self) -> dict:
        return self._library

    def add_category(self, category_id, category_name):
        if category_id in self._categories.keys():
            return

        self._categories[category_id] = Category(category_id, category_name)

    def add_operation_from_attributes(self, op_attributes):
        category_id = op_attributes.category_id

        if category_id in self._categories.keys():
            if op_attributes.unique_id not in self._categories[category_id].operations:
                self._library[category_id]['operations'].append(op_attributes)
                self._categories[category_id].register_operation(op_attributes)
        else:
            category = Category(category_id, "Uncategorized Operations")
            self._categories[category_id] = category
            self._library[category_id]['operations'].append(op_attributes)
            category.register_operation(op_attributes)

    def is_verified(self, category_id):
        category = self._categories.get(category_id, None)
        if category:
            return check_verified(category.name)
        return False

    async def build_base_library(self):
        self._categories = {
            1: Category(1, 'Category 1'),
            2: Category(2, 'Category 2'),
            3: Category(3, 'Category 3'),
        }
        for category in self._categories.values():
            await category.initialize()

        # Discover verified operations in the current package
        self._populate_verified_operations()

        for category_id, category in self._categories.items():
            operations = []
            for operation in category.operations:
                if isinstance(operation, dict):
                    operations.append(operation)

            self._library[category_id] = {
                'category_id': category_id,
                'name': category.name,
                'operations': operations
            }

        user_dir = os.path.normpath(os.path.join(self._config.BASE_DIR, 'operations'))
        if os.path.exists(user_dir):
            files = [f for f in os.listdir(user_dir) if f.endswith('.json')]
            for file in files:
                from research_analytics_suite.operation_manager.operations.core.memory.OperationAttributes import \
                    OperationAttributes
                op_attributes = OperationAttributes()
                await op_attributes.initialize()
                await op_attributes.from_disk(os.path.join(user_dir, file))
                self.add_operation_from_attributes(op_attributes)

    async def load_user_library(self):
        # Called when a workspace is loaded, rebuilds the user library
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
            from research_analytics_suite.operation_manager.operations.core.memory.OperationAttributes import \
                OperationAttributes
            _op_attributes = OperationAttributes()
            await _op_attributes.initialize()
            await _op_attributes.from_disk(_op)
            self.add_operation_from_attributes(_op_attributes)

    def get_categories(self):
        """
        Returns the categories of the library.

        Returns:
            dict: A dictionary containing the categories of the library.
        """
        return self._categories.items()

    async def _update_user_manifest(self):
        """
        Updates the user manifest.
        """
        while not self._initialized:
            await asyncio.sleep(0.1)

        while True:
            # TODO: Improve this method to update the user manifest, rather than just reloading it every time.
            await self.load_user_library()
            await asyncio.sleep(0.1)

    @staticmethod
    def __load_module_attributes(module_name):
        module = importlib.import_module(f'research_analytics_suite.operation_library.{module_name}')
        _cls = getattr(module, module_name)

        return {
            'unique_id': _cls.unique_id,
            'category_id': _cls.category_id,
            'version': _cls.version,
            'name': _cls.name,
            'author': _cls.author,
            'github': _cls.github,
            'email': _cls.email,
            'description': _cls.description,
            'action': _cls.action,
            'persistent': _cls.persistent,
            'concurrent': _cls.concurrent,
            'is_cpu_bound': _cls.is_cpu_bound,
            'dependencies': _cls.dependencies,
            'parent_operation': _cls.parent_operation,
            'child_operations': _cls.child_operations,
        }

    def _populate_verified_operations(self):
        package = importlib.import_module('operation_library')
        for _, module_name, _ in pkgutil.iter_modules(package.__path__):
            if module_name not in self._categories:
                module_attributes = self.__load_module_attributes(module_name)
                category_id = module_attributes['category_id']
                category = self._categories.get(category_id, None)
                if category:
                    category.register_operation(module_attributes)
                else:
                    category = Category(category_id, f"Category {category_id}")
                    category.register_operation(module_attributes)

                self._categories[category_id] = category

    def get_category_from_operation(self, operation_name):
        category_id = operation_name.split('_')[0]
        category_name = f"Category {category_id.capitalize()}"
        return category_id, category_name

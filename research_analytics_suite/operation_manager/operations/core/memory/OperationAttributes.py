"""
OperationAttributes

This module contains the OperationAttributes class, which is used to store the attributes of an operation.

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


class OperationAttributes:
    """
    OperationAttributes class is used to temporarily store the attributes of an operation, allowing for operations
    to be processed without the need for the operation class to be loaded. This is useful for building the library
    manifest and reduces the need to load all operations into memory.
    """
    _lock = asyncio.Lock()

    def __init__(self, *args, **kwargs):
        """
        Initializes the OperationAttributes with the given parameters.

        Args:
            unique_id (str): The unique identifier of the operation.
            category_id (str): The unique identifier of the category.
            version (str): The version of the operation.
            name (str): The name of the operation.
            author (str): The author of the operation.
            github (str): The GitHub repository of the operation.
            email (str): The email of the author of the operation.
            description (str): The description of the operation.
            action (str): The action of the operation.
            persistent (bool): The persistent status of the operation.
            concurrent (bool): The concurrent status of the operation.
            is_cpu_bound (bool): The CPU bound status of the operation.
            dependencies (list): The dependencies of the operation.
            parent_operation (OperationAttributes): The parent operation of the operation.
            child_operations (list): The child operations of the operation.
        """
        if not hasattr(self, '_initialized'):
            self._temp_kwargs = kwargs

            self._unique_id = None
            self._category_id = None
            self._version = None
            self._name = None
            self._author = None
            self._github = None
            self._email = None
            self._description = None
            self._action = None
            self._persistent = None
            self._concurrent = None
            self._is_cpu_bound = None
            self._dependencies = None
            self._parent_operation = None
            self._child_operations = None

            self._initialized = False

    async def initialize(self):
        """
        Initializes the OperationAttributes.

        This method is called asynchronously to initialize the OperationAttributes.
        """
        if not self._initialized:
            async with OperationAttributes._lock:
                if not self._initialized:

                    self._unique_id = self._temp_kwargs.get('unique_id', None)
                    self._category_id = self._temp_kwargs.get('category_id', None)
                    self._version = self._temp_kwargs.get('version', None)
                    self._name = self._temp_kwargs.get('name', None)
                    self._author = self._temp_kwargs.get('author', None)
                    self._github = self._temp_kwargs.get('github', None)
                    self._email = self._temp_kwargs.get('email', None)
                    self._description = self._temp_kwargs.get('description', None)
                    self._action = self._temp_kwargs.get('action', None)
                    self._persistent = self._temp_kwargs.get('persistent', None)
                    self._concurrent = self._temp_kwargs.get('concurrent', None)
                    self._is_cpu_bound = self._temp_kwargs.get('is_cpu_bound', None)
                    self._dependencies = self._temp_kwargs.get('dependencies', None)
                    self._parent_operation = self._temp_kwargs.get('parent_operation', None)
                    self._child_operations = self._temp_kwargs.get('inheritance', None)

                    self._initialized = True

    async def from_disk(self, file_path: str):
        """
        Loads the OperationAttributes from disk.

        Args:
            file_path (str): The file path to load the OperationAttributes from.
        """
        async with OperationAttributes._lock:
            from research_analytics_suite.operation_manager.operations.core.workspace import load_from_disk
            attributes = await load_from_disk(file_path=file_path, operation_group=None, with_instance=False)
            if attributes is None:
                return

            self._unique_id = attributes.get('unique_id', None)
            self._category_id = attributes.get('category_id', None)
            self._version = attributes.get('version', None)
            self._name = attributes.get('name', None)
            self._author = attributes.get('author', None)
            self._github = attributes.get('github', None)
            self._email = attributes.get('email', None)
            self._description = attributes.get('description', None)
            self._action = attributes.get('action', None)
            self._persistent = attributes.get('persistent', None)
            self._concurrent = attributes.get('concurrent', None)
            self._is_cpu_bound = attributes.get('is_cpu_bound', None)
            self._dependencies = attributes.get('dependencies', None)
            self._parent_operation = attributes.get('parent_operation', None)
            self._child_operations = attributes.get('inheritance', None)

    def export_attributes(self) -> dict:
        return {
            'unique_id': self._unique_id,
            'category_id': self._category_id,
            'version': self._version,
            'name': self._name,
            'author': self._author,
            'github': self._github,
            'email': self._email,
            'description': self._description,
            'action': self._action,
            'persistent': self._persistent,
            'concurrent': self._concurrent,
            'is_cpu_bound': self._is_cpu_bound,
            'dependencies': self._dependencies,
            'parent_operation': self._parent_operation,
            'inheritance': self._child_operations,
        }

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def category_id(self):
        return self._category_id

    @property
    def version(self):
        return self._version

    @property
    def name(self):
        return self._name

    @property
    def author(self):
        return self._author

    @property
    def github(self):
        return self._github

    @property
    def email(self):
        return self._email

    @property
    def description(self):
        return self._description

    @property
    def action(self):
        return self._action

    @property
    def persistent(self):
        return self._persistent

    @property
    def concurrent(self):
        return self._concurrent

    @property
    def is_cpu_bound(self):
        return self._is_cpu_bound

    @property
    def dependencies(self):
        return self._dependencies

    @property
    def parent_operation(self):
        return self._parent_operation

    @property
    def child_operations(self):
        return self._child_operations

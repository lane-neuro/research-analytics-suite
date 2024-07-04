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
            name (str): The name of the operation.
            version (str): The version of the operation.
            description (str): The description of the operation.
            category_id (str): The unique identifier of the category.
            author (str): The author of the operation.
            github (str): The GitHub repository of the operation.
            email (str): The email of the author of the operation.
            unique_id (str): The unique identifier of the operation.
            action (str): The action of the operation.
            required_inputs (dict): The required inputs of the operation.
            parent_operation (OperationAttributes): The parent operation of the operation.
            inheritance (list): The child operations of the operation.
            is_loop (bool): The is_loop status of the operation.
            is_cpu_bound (bool): The CPU bound status of the operation.
            parallel (bool): The parallel status of the operation.
        """
        if not hasattr(self, '_initialized'):
            self._temp_kwargs = kwargs

            self._name = None
            self._version = None
            self._description = None
            self._category_id = None
            self._author = None
            self._github = None
            self._email = None
            self._unique_id = None
            self._action = None
            self._required_inputs = None
            self._parent_operation = None
            self._inheritance = None
            self._is_loop = None
            self._is_cpu_bound = None
            self._parallel = None

            self._initialized = False

    async def initialize(self):
        """
        Initializes the OperationAttributes.

        This method is called asynchronously to initialize the OperationAttributes.
        """
        if not self._initialized:
            async with OperationAttributes._lock:
                if not self._initialized:

                    self._name = self._temp_kwargs.get('name')
                    self._version = self._temp_kwargs.get('version')
                    self._description = self._temp_kwargs.get('description')
                    self._category_id = self._temp_kwargs.get('category_id')
                    self._author = self._temp_kwargs.get('author')
                    self._github = self._temp_kwargs.get('github')
                    self._email = self._temp_kwargs.get('email')
                    self._unique_id = self._temp_kwargs.get('unique_id')
                    self._action = self._temp_kwargs.get('action')
                    self._required_inputs = self._temp_kwargs.get('required_inputs')
                    self._parent_operation = self._temp_kwargs.get('parent_operation')
                    self._inheritance = self._temp_kwargs.get('inheritance')
                    self._is_loop = self._temp_kwargs.get('is_loop')
                    self._is_cpu_bound = self._temp_kwargs.get('is_cpu_bound')
                    self._parallel = self._temp_kwargs.get('parallel')

                    self._initialized = True

                    del self._temp_kwargs

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

            self._name = attributes.get('name')
            self._version = attributes.get('version')
            self._description = attributes.get('description')
            self._category_id = attributes.get('category_id')
            self._author = attributes.get('author')
            self._github = attributes.get('github')
            self._email = attributes.get('email')
            self._unique_id = attributes.get('unique_id')
            self._action = attributes.get('action')
            self._required_inputs = attributes.get('required_inputs')
            self._parent_operation = attributes.get('parent_operation')
            self._inheritance = attributes.get('inheritance')
            self._is_loop = attributes.get('is_loop')
            self._is_cpu_bound = attributes.get('is_cpu_bound')
            self._parallel = attributes.get('parallel')

    def export_attributes(self) -> dict:
        return {
            'name': self._name,
            'version': self._version,
            'description': self._description,
            'category_id': self._category_id,
            'author': self._author,
            'github': self._github,
            'email': self._email,
            'unique_id': self._unique_id,
            'action': self._action,
            'required_inputs': self._required_inputs,
            'parent_operation': self._parent_operation,
            'inheritance': self._inheritance,
            'is_loop': self._is_loop,
            'is_cpu_bound': self._is_cpu_bound,
            'parallel': self._parallel,
        }

    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version

    @property
    def description(self):
        return self._description

    @property
    def category_id(self):
        return self._category_id

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
    def unique_id(self):
        return self._unique_id

    @property
    def action(self):
        return self._action

    @property
    def required_inputs(self):
        return self._required_inputs

    @property
    def parent_operation(self):
        return self._parent_operation

    @property
    def inheritance(self):
        return self._inheritance

    @property
    def is_loop(self):
        return self._is_loop

    @property
    def is_cpu_bound(self):
        return self._is_cpu_bound

    @property
    def parallel(self):
        return self._parallel

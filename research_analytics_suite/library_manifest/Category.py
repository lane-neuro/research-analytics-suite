"""
Category Module

The Category class module is used to store the operations of a category. It also has a method to check if the category
is verified.

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


class Category:
    """
    Category class is used to store the operations of a category.

    Attributes:
        category_id (int): The unique identifier of the category.
        name (str): The name of the category.
        operations (list): A list to store the operations of the category.
    """
    _instances = dict()
    _lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        category_id = args[0]
        if category_id in cls._instances:
            return cls._instances[category_id]
        instance = super().__new__(cls)
        cls._instances[category_id] = instance
        return instance

    def __init__(self, category_id, name):
        """
        Initializes the Category with the given parameters.

        Args:
            category_id (int): The unique identifier of the category.
            name (str): The name of the category.
        """
        if not hasattr(self, '_initialized'):
            self._category_id = category_id
            self._name = name
            self._operations = []
            self._initialized = False

    def __repr__(self):
        _info = f"\n[ID:{self._category_id}]\t{self._name}"
        _ops = ""
        for operation in self._operations:
            _ops += f"\n{operation}"
        return f"{_info}\n{_ops}"

    async def initialize(self):
        """
        Initializes the Category.

        This method is called asynchronously to initialize the Category.
        """
        if not self._initialized:
            async with Category._lock:
                if not self._initialized:
                    self._initialized = True

    @property
    def category_id(self):
        return self._category_id

    @property
    def name(self):
        return self._name

    @property
    def operations(self):
        return self._operations

    def register_operation(self, operation):
        self._operations.append(operation)

    def get_operations(self):
        return self._operations

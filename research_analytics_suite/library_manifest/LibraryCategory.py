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
from __future__ import annotations
import asyncio

from research_analytics_suite.commands import command, register_commands
from research_analytics_suite.operation_manager.operations.core.memory.OperationAttributes import OperationAttributes


@register_commands
class Category:
    """
    Category class is used to store the operations of a category.

    Attributes:
        category_id (int): The unique identifier of the category.
        name (str): The name of the category.
        operations (list): A list to store the operations of the category.
        subcategories (dict): A dictionary to store subcategories.
    """
    _instances = {}
    _lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs) -> Category:
        category_id = args[0]
        if cls._instances is None:
            cls._instances = {}

        if category_id in cls._instances:
            return cls._instances[category_id]

        instance = super().__new__(cls)
        cls._instances[category_id] = instance
        return instance

    def __init__(self, category_id, name):
        """
        Initializes the category with the specified category identifier and name.

        Args:
            category_id (int): The unique identifier of the category.
            name (str): The name of the category.
        """
        if not hasattr(self, '_initialized'):
            self._category_id = category_id
            self._name = name
            self._operations = []
            self._subcategories = {}
            self._initialized = False

    def __repr__(self) -> str:
        """
        Returns the string representation of the category.

        Returns:
            str: The string representation of the category.
        """
        _info = f"\n[ID:{self._category_id}]\t{self._name}"
        _ops = ""
        for operation in self._operations:
            _ops += f"\n{operation}"
        return f"{_info}\n{_ops}"

    async def initialize(self):
        """
        Initializes the category if it has not been initialized.
        """
        if not self._initialized:
            async with Category._lock:
                if not self._initialized:
                    self._initialized = True

    @property
    def category_id(self) -> int:
        """
        Returns the unique identifier of the category.

        Returns:
            int: The unique identifier of the category.
        """
        return self._category_id if self._category_id is not None else -1

    @property
    def name(self) -> str:
        """
        Returns the name of the category.

        Returns:
            str: The name of the category.
        """
        return self._name if self._name is not None else f"Category {self.category_id}"

    @property
    def operations(self) -> list:
        """
        Returns the operations of the category.

        Returns:
            list: The operations of the category.
        """
        return self._operations if self._operations is not None else []

    @property
    def subcategories(self) -> dict:
        """
        Returns the subcategories of the category.

        Returns:
            dict: The subcategories of the category.
        """
        return self._subcategories if self._subcategories is not None else {}

    @command
    def register_operation(self, operation_attributes: OperationAttributes) -> None:
        """
        Registers an operation to the category.

        Args:
            operation_attributes (OperationAttributes): The attributes of the operation to be registered.
        """
        if self._operations is None:
            self._operations = []

        if operation_attributes not in self._operations:
            self._operations.append(operation_attributes)

    @command
    def add_subcategory(self, subcategory: Category) -> None:
        """
        Adds a subcategory to the category.

        Args:
            subcategory (Category): The subcategory to be added.
        """
        self._subcategories[subcategory.category_id] = subcategory

    @command
    def get_operations(self) -> list:
        """
        Returns the operations of the category.

        Returns:
            list: The operations of the category.
        """
        if self._operations is None:
            return []
        return self._operations

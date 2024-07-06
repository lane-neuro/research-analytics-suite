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
import ast
import asyncio
import inspect
from typing import Optional, Any
from research_analytics_suite.operation_manager.operations.core.workspace import load_from_disk


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
            from research_analytics_suite.utils import CustomLogger
            self._logger = CustomLogger()

            self._temp_kwargs = kwargs

            self._name = None
            self._version = None
            self._description = None
            self._category_id = 1
            self._author = None
            self._github = None
            self._email = None
            self._action = None
            self._required_inputs = {}
            self._parent_operation = None
            self._inheritance = []
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

                    self.name = self._temp_kwargs.get('name', "No name")
                    self.version = self._temp_kwargs.get('version', "0.0.1")
                    self.description = self._temp_kwargs.get('description', "None")
                    self.category_id = self._temp_kwargs.get('category_id', 1)
                    self.author = self._temp_kwargs.get('author', "No author")
                    self.github = self._temp_kwargs.get('github', "[no-github]")
                    self.email = self._temp_kwargs.get('email', "[no-email]")
                    self.action = self._temp_kwargs.get('action', "None")
                    self.required_inputs = self._temp_kwargs.get('required_inputs', {})
                    self.parent_operation = self._temp_kwargs.get('parent_operation', None)
                    self.inheritance = self._temp_kwargs.get('inheritance', [])
                    self.is_loop = self._temp_kwargs.get('is_loop', False)
                    self.is_cpu_bound = self._temp_kwargs.get('is_cpu_bound', False)
                    self.parallel = self._temp_kwargs.get('parallel', False)

                    self._initialized = True

                    del self._temp_kwargs

    def export_attributes(self) -> dict:
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'category_id': self.category_id,
            'author': self.author,
            'github': self.github,
            'email': self.email,
            'unique_id': self.unique_id,
            'action': self.action,
            'required_inputs': self.required_inputs,
            'parent_operation': self.parent_operation,
            'inheritance': self.inheritance,
            'is_loop': self.is_loop,
            'is_cpu_bound': self.is_cpu_bound,
            'parallel': self.parallel,
        }

    @property
    def name(self) -> str:
        return self._name or "No name"

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            value = "No name"

        self._name = value

    @property
    def version(self) -> str:
        return self._version or "0.0.1"

    @version.setter
    def version(self, value):
        if not isinstance(value, str):
            value = "0.0.1"

        self._version = value

    @property
    def description(self) -> str:
        return self._description or "None"

    @description.setter
    def description(self, value):
        if not isinstance(value, str):
            value = "None"

        self._description = value

    @property
    def category_id(self) -> int:
        return self._category_id or 1

    @category_id.setter
    def category_id(self, value):
        if not isinstance(value, int):
            value = 1

        self._category_id = value

    @property
    def author(self) -> str:
        return self._author or "No author"

    @author.setter
    def author(self, value):
        if not isinstance(value, str):
            value = "No author"

        self._author = value

    @property
    def github(self) -> str:
        return self._github or "[no-github]"

    @github.setter
    def github(self, value):
        if not isinstance(value, str):
            value = "[no-github]"
        if value.startswith("@"):
            value = value[1:]

        self._github = value

    @property
    def email(self) -> str:
        return self._email or "[no-email]"

    @email.setter
    def email(self, value):
        if not isinstance(value, str):
            value = "[no-email]"

        self._email = value

    @property
    def unique_id(self) -> str:
        return f"{self._github}_{self._name}_{self._version}" or "[no-unique-id]"

    @property
    def action(self) -> Any:
        return self._action or None

    @action.setter
    def action(self, value):
        if not value:
            value = None

        self._action = value

    @property
    def required_inputs(self) -> dict:
        return self._required_inputs or {}

    @required_inputs.setter
    def required_inputs(self, value):
        if not isinstance(value, dict):
            value = {}

        self._required_inputs = value

    @property
    def parent_operation(self) -> 'OperationAttributes' or None:
        return self._parent_operation or None

    @parent_operation.setter
    def parent_operation(self, value):
        if not isinstance(value, OperationAttributes) and value is not None:
            value = None
        if not value:
            value = None

        self._parent_operation = value

    @property
    def inheritance(self) -> list:
        return self._inheritance or []

    @inheritance.setter
    def inheritance(self, value):
        if not isinstance(value, list) and value is not None and value != []:
            value = []

        self._inheritance = value

    @property
    def is_loop(self) -> bool:
        return self._is_loop or False

    @is_loop.setter
    def is_loop(self, value):
        if not isinstance(value, bool):
            value = False

        self._is_loop = value

    @property
    def is_cpu_bound(self) -> bool:
        return self._is_cpu_bound or False

    @is_cpu_bound.setter
    def is_cpu_bound(self, value):
        if not isinstance(value, bool):
            value = False

        self._is_cpu_bound = value

    @property
    def parallel(self) -> bool:
        return self._parallel or False

    @parallel.setter
    def parallel(self, value):
        if not isinstance(value, bool):
            value = False

        self._parallel = value


async def get_attributes_from_disk(file_path: str) -> Optional['OperationAttributes']:
    """
    Gets the attributes from the disk.

    Args:
        file_path (str): The file path to load the attributes from.

    Returns:
        OperationAttributes: The operation attributes.
    """
    attributes = await load_from_disk(file_path=file_path, operation_group=None, with_instance=False)
    if attributes is None:
        return None

    _op = OperationAttributes(attributes)
    await _op.initialize()
    return _op


async def get_attributes_from_module(module) -> Optional['OperationAttributes']:
    """
    Gets the attributes from the module.

    Args:
        module: The module to load the attributes from.

    Returns:
        OperationAttributes: The operation attributes.
    """
    # Get the source code of the class
    source = inspect.getsource(module)

    # Parse the source code into an AST
    tree = ast.parse(source)

    # Initialize variables to hold the class body and properties
    class_body = None
    _op_props = OperationAttributes()
    await _op_props.initialize()

    # Traverse the AST to find the class definition
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == module.__name__:
            class_body = node.body
            break

    # If class body is found, process its nodes
    if class_body:
        for node in class_body:
            # Stop when encountering the __init__ method
            if isinstance(node, ast.FunctionDef) and node.name == '__init__':
                break

            # Collect properties (assignments) before the __init__ method
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        prop_name = target.id

                        if isinstance(node.value, ast.Constant or ast.Str or ast.Num or ast.NameConstant
                                      or ast.Name or ast.Attribute or ast.Subscript or ast.Tuple or ast.List
                                      or ast.Dict):
                            try:
                                _op_props.__setattr__(prop_name, node.value.value)
                            except AttributeError:
                                raise AttributeError(f"Invalid attribute: {prop_name}")

    return _op_props


async def get_attributes_from_operation(operation) -> Optional['OperationAttributes']:
    """
    Gets the attributes from the operation.

    Args:
        operation: The operation to load the attributes from.

    Returns:
        OperationAttributes: The operation attributes.
    """
    _op = OperationAttributes(**operation.__dict__)
    await _op.initialize()
    return _op


async def get_attributes_from_dict(attributes: dict) -> Optional['OperationAttributes']:
    """
    Gets the attributes from the dictionary.

    Args:
        attributes (dict): The attributes to load.

    Returns:
        OperationAttributes: The operation attributes.
    """
    _op = OperationAttributes(**attributes)
    await _op.initialize()
    return _op

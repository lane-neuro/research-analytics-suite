"""
utils.py

This module contains utility functions for extracting operation attributes from different sources such as disk,
module, operation, and dictionary. The attributes are used to initialize the OperationAttributes class.

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
from typing import Optional
from research_analytics_suite.operation_manager.operations.core.OperationAttributes import OperationAttributes
from research_analytics_suite.operation_manager.operations.core.workspace import load_from_disk
from research_analytics_suite.utils import CustomLogger


def translate_item(item):
    """
    Translates an AST item into a Python object.

    Args:
        item: The AST item to translate.

    Returns:
        object: The Python object.
    """
    if isinstance(item, ast.Constant):
        return item.value
    elif isinstance(item, ast.List):
        return [translate_item(e) for e in item.elts]
    elif isinstance(item, ast.Dict):
        return {translate_item(k): translate_item(v) for k, v in zip(item.keys, item.values)}
    elif isinstance(item, ast.Tuple):
        return tuple(translate_item(e) for e in item.elts)
    elif isinstance(item, ast.Name):
        return item.id
    elif isinstance(item, ast.Attribute):
        return item.attr
    elif isinstance(item, ast.Call):
        return item.func
    return None


async def get_attributes_from_disk(file_path: str) -> Optional[OperationAttributes]:
    """
    Gets the attributes from the disk.

    Args:
        file_path (str): The file path to load the attributes from.

    Returns:
        OperationAttributes: The operation attributes.
    """
    base_operation = await load_from_disk(file_path=file_path, operation_group=None)

    # Extract OperationAttributes from the BaseOperation
    if hasattr(base_operation, '_attributes') and isinstance(base_operation.attributes, OperationAttributes):
        return base_operation.attributes
    else:
        raise TypeError("Loaded object is not a valid BaseOperation with OperationAttributes")


async def get_attributes_from_module(module) -> OperationAttributes:
    """
    Gets the attributes from the module.
    """
    _op_props = OperationAttributes()
    await _op_props.initialize()

    try:
        cls = module
        for name, value in vars(cls).items():
            # skip dunders, callables (methods), and any explicit exclusions
            if name.startswith("__") or callable(value) or name == "unique_id":
                continue
            setattr(_op_props, name, value)

    except Exception as e:
        pass

    if _op_props.action is None:
        execute = getattr(module, "execute", None)
        if callable(execute):
            _op_props.action = execute
        else:
            _op_props.action = None
            CustomLogger().warning(f"{getattr(module, '__name__', module)} has no 'execute' method")

    # Store the operation class for later instantiation
    _op_props.operation_class = module

    return _op_props


async def get_attributes_from_operation(operation) -> OperationAttributes:
    """
    Gets the attributes from the operation.

    Args:
        operation: The operation to load the attributes from.

    Returns:
        OperationAttributes: The operation attributes.
    """
    _attributes = operation.export_attributes()

    _op = OperationAttributes(**_attributes)
    await _op.initialize()
    return _op


async def get_attributes_from_dict(attributes: dict) -> Optional[OperationAttributes]:
    """
    Gets the attributes from the dictionary.

    Args:
        attributes (dict): The attributes to load.

    Returns:
        OperationAttributes: The operation attributes.
    """
    attributes.pop('_initialized', None)  # Safely remove if it exists
    _op = OperationAttributes(**attributes)
    await _op.initialize()
    return _op

import ast
import inspect
from typing import Optional

from research_analytics_suite.operation_manager.operations.core.memory.OperationAttributes import OperationAttributes
from research_analytics_suite.operation_manager.operations.core.workspace import load_from_disk


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

                        try:
                            if isinstance(node.value, ast.Dict):
                                dict_items = {translate_item(k): translate_item(v) for k, v in zip(node.value.keys, node.value.values)}
                                _op_props.__setattr__(prop_name, dict_items)
                            elif isinstance(node.value, ast.List):
                                list_items = [translate_item(v) for v in node.value.elts]
                                _op_props.__setattr__(prop_name, list_items)
                            elif isinstance(node.value, ast.Tuple):
                                tuple_items = tuple(translate_item(v) for v in node.value.elts)
                                _op_props.__setattr__(prop_name, tuple_items)
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


def translate_item(_v):
    if isinstance(_v, (ast.Constant, ast.Num, ast.Str, ast.NameConstant)):
        return _v.value
    elif isinstance(_v, ast.Name):
        return _v.id
    elif isinstance(_v, ast.Attribute):
        return _v.attr
    elif isinstance(_v, ast.Subscript):
        # Handle subscript if needed, placeholder return for now
        return _v
    else:
        return f"{_v}"

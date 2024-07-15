import ast
import inspect
from types import ModuleType
from typing import Optional

from research_analytics_suite.operation_manager.operations.core.memory.OperationAttributes import OperationAttributes
from research_analytics_suite.operation_manager.operations.core.workspace import load_from_disk
from research_analytics_suite.utils import CustomLogger


def translate_item(item):
    if isinstance(item, ast.Str):
        return item.s
    elif isinstance(item, ast.Num):
        return item.n
    elif isinstance(item, ast.NameConstant):
        return item.value
    elif isinstance(item, ast.List):
        return [translate_item(e) for e in item.elts]
    elif isinstance(item, ast.Dict):
        return {translate_item(k): translate_item(v) for k, v in zip(item.keys, item.values)}
    elif isinstance(item, ast.Tuple):
        return tuple(translate_item(e) for e in item.elts)
    return None


async def get_attributes_from_disk(file_path: str) -> Optional[OperationAttributes]:
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


async def get_attributes_from_module(module: ModuleType) -> OperationAttributes:
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
        if isinstance(node, ast.ClassDef):
            # Assuming the first class definition matches the module's class
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
                    if isinstance(target, ast.Name) and target.id != 'unique_id':
                        prop_name = target.id

                        try:
                            if isinstance(node.value, ast.Dict):
                                dict_items = {translate_item(k): translate_item(v) for k, v in
                                              zip(node.value.keys, node.value.values)}
                                setattr(_op_props, prop_name, dict_items)
                            elif isinstance(node.value, ast.List):
                                list_items = [translate_item(v) for v in node.value.elts]
                                setattr(_op_props, prop_name, list_items)
                            elif isinstance(node.value, ast.Tuple):
                                tuple_items = tuple(translate_item(v) for v in node.value.elts)
                                setattr(_op_props, prop_name, tuple_items)
                            else:
                                # Direct value assignment for simple types
                                setattr(_op_props, prop_name, translate_item(node.value))
                        except AttributeError:
                            CustomLogger().error(AttributeError(f"Invalid attribute: {prop_name}"),
                                                 OperationAttributes.__name__)

    return _op_props


async def get_attributes_from_operation(operation) -> Optional[OperationAttributes]:
    """
    Gets the attributes from the operation.

    Args:
        operation: The operation to load the attributes from.

    Returns:
        OperationAttributes: The operation attributes.
    """
    _op = OperationAttributes(operation.__dict__)
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
    _op = OperationAttributes(attributes)
    await _op.initialize()
    return _op

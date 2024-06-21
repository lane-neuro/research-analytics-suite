"""
FileDiskOperations Module

Contains functionality for file and disk operations in an operation.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

import os
import json

import aiofiles


async def load_from_disk(file_path: str, operation_group: dict):
    """
    Load a BaseOperation object from disk.

    Args:
        file_path (str): The path to the file to load.
        operation_group (dict[str, BaseOperation]): The group of operations to which the loaded operation belongs.

    Returns:
        BaseOperation: The loaded operation.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    async with aiofiles.open(file_path, 'r') as file:
        try:
            data = await file.read()
            state = json.loads(data)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Failed to decode JSON from file: {file_path}", data, e.pos) from e
        except Exception as e:
            raise e

        if not isinstance(state, dict):
            raise TypeError("Loaded data must be a dictionary")

        from research_analytics_suite.operation_manager.operations.core import BaseOperation
        operation = await BaseOperation.from_dict(data=state, file_dir=os.path.dirname(file_path))

        if operation.runtime_id not in operation_group.keys():
            operation_group[operation.runtime_id] = operation
        return operation


async def load_operation_group(file_path: str,
                               operation_group: dict,
                               iterate_child_operations: bool = True) -> dict:
    """
    Load a group of operations from disk.

    Args:
        file_path (str): The path to the file to load.
        operation_group (dict, optional): The group of operations to which the loaded operations belong.
                                           Defaults to None.
        iterate_child_operations (bool, optional): Whether to iterate through child operations. Defaults to True.

    Returns:
        dict: The loaded operation group.
    """
    processed_operations = set()

    async def load_and_process_operation(path, group):
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

        operation = await load_from_disk(path, group)
        processed_operations.add(operation.runtime_id)

        parent = operation.parent_operation
        if isinstance(parent, dict):
            parent_id = parent['unique_id']
            if parent_id not in group.values().unique_id:
                parent_file_path = construct_file_path(file_dir, parent)
                if os.path.exists(parent_file_path):
                    parent_operation = await load_and_process_operation(parent_file_path, group)
                    operation._parent_operation = parent_operation
                    group[parent_operation.runtime_id] = parent_operation
                else:
                    raise FileNotFoundError(f"Parent operation file not found: {parent_file_path}")
            else:
                for op in group.values():
                    if op.unique_id == parent_id:
                        operation._parent_operation = op
                        break

        if operation.child_operations and iterate_child_operations:
            if isinstance(operation.child_operations, list):
                children = operation.child_operations
                for child in children:
                    if isinstance(child, dict):
                        child_id = child['unique_id']
                        if child_id not in group.values().unique_id:
                            child_file_path = construct_file_path(file_dir, child)
                            if os.path.exists(child_file_path):
                                child_operation = await load_and_process_operation(child_file_path, group)
                                await operation.add_child_operation(child_operation)
                                await operation.link_child_operation(child_operation)
                                group[child_operation.runtime_id] = child_operation
                            else:
                                raise FileNotFoundError(f"Child operation file not found: {child_file_path}")

        return operation

    file_dir = os.path.dirname(file_path)
    if not os.path.exists(file_dir):
        raise FileNotFoundError(f"Directory not found: {file_dir}")

    root_operation = await load_and_process_operation(file_path, operation_group)
    operation_group[root_operation.runtime_id] = root_operation

    return operation_group


def construct_file_path(base_dir, operation_ref):
    """
    Helper method to construct file path for an operation reference.

    Args:
        base_dir: The base directory.
        operation_ref: The operation reference.

    Returns:
        str: The constructed file path.
    """
    name = operation_ref['name']
    short_id = operation_ref['unique_id'][:4]
    version = operation_ref['version']
    file_name = f"{name}_{short_id}.json" if version == 0 else f"{name}_{short_id}-{version}.json"
    return os.path.join(base_dir, file_name)

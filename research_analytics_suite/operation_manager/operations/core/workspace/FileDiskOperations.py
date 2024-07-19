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
from typing import Optional
import aiofiles
from research_analytics_suite.commands import command
from research_analytics_suite.operation_manager.operations.core import BaseOperation
from research_analytics_suite.utils import CustomLogger


@command
async def load_from_disk(file_path: str, operation_group: Optional[dict]):
    """
    Load a BaseOperation object from disk.

    Args:
        file_path (str): The path to the file to load.
        operation_group (dict[str, BaseOperation]): The group of operations to which the loaded operation belongs.

    Returns:
        BaseOperation or OperationAttributes: The loaded operation.
    """
    if not os.path.exists(file_path):
        CustomLogger().error(FileNotFoundError(f"File not found: {file_path}"), 'FileDiskOperations')

    async with aiofiles.open(file_path, 'r') as file:
        try:
            data = await file.read()
            state = json.loads(data)
        except json.JSONDecodeError as e:
            CustomLogger().error(
                json.JSONDecodeError(f"Failed to decode JSON from file: {file_path}", data, e.pos),
                'FileDiskOperations')
            return None
        except Exception as e:
            CustomLogger().error(e, 'FileDiskOperations')
            return None

        if not isinstance(state, dict):
            CustomLogger().error(TypeError("Loaded data must be a dictionary"), 'FileDiskOperations')
            return None

        operation = await from_dict(data=state, file_dir=os.path.dirname(file_path))

        if operation_group is not None and operation.runtime_id not in operation_group.keys():
            operation_group[operation.runtime_id] = operation

        return operation


async def load_operation_group(file_path: str, operation_group: dict, iterate_child_operations: bool = True) -> dict:
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
            CustomLogger().error(FileNotFoundError(f"File not found: {path}"), 'FileDiskOperations')

        operation = await load_from_disk(path, group)
        processed_operations.add(operation.runtime_id)

        parent = operation.parent_operation
        if isinstance(parent, dict):
            parent_id = parent['unique_id']
            if parent_id not in group.values().unique_id:
                parent_file_path = construct_file_path(file_dir, parent)
                if os.path.exists(parent_file_path):
                    parent_operation = await load_and_process_operation(parent_file_path, group)
                    operation.parent_operation = parent_operation
                    group[parent_operation.runtime_id] = parent_operation
                else:
                    operation.parent_operation = None
                    CustomLogger().error(FileNotFoundError(f"Parent operation file not found: {parent_file_path}"))
            else:
                for op in group.values():
                    if op.unique_id == parent_id:
                        operation.parent_operation = op
                        break

        if operation.inheritance and iterate_child_operations:
            if isinstance(operation.inheritance, list):
                children = operation.inheritance
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
                                CustomLogger().error(
                                    FileNotFoundError(f"Child operation file not found: {child_file_path}"),
                                    'FileDiskOperations')

        return operation

    file_dir = os.path.dirname(file_path)
    if not os.path.exists(file_dir):
        CustomLogger().error(FileNotFoundError(f"Directory not found: {file_dir}"), 'FileDiskOperations')

    root_operation = await load_and_process_operation(file_path, operation_group)
    operation_group[root_operation.runtime_id] = root_operation

    return operation_group


@command
def construct_file_path(base_dir, operation_ref):
    """
    Helper method to construct file path for an operation reference.

    Args:
        base_dir: The base directory.
        operation_ref: The operation reference.

    Returns:
        str: The constructed file path.
    """
    github = operation_ref['github']
    name = operation_ref['name']
    version = operation_ref['version']
    file_name = f"{github}_{name}_{version}.json"
    return os.path.join(base_dir, file_name)


async def from_dict(data: dict, file_dir, parent_operation=None) -> BaseOperation:
    """
    Create a BaseOperation instance from a dictionary.

    Args:
        data (dict): The dictionary containing the operation data.
        file_dir: The directory where the operation file is located.
        parent_operation (BaseOperation, optional): The parent operation. Defaults to None.

    Returns:
        BaseOperation: The created operation instance.
    """
    data_metadata = await populate_operation_args(data=data, file_dir=file_dir, parent_operation=parent_operation)

    from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation
    return BaseOperation(**data_metadata)


@command
async def populate_operation_args(data, file_dir, parent_operation=None) -> dict:
    """
    Populate the arguments of an operation.

    Args:
        data (dict): The operation data.
        file_dir: The directory where the operation file is located.
        parent_operation (BaseOperation, optional): The parent operation
    """
    data_metadata = data.copy()

    if 'action' not in data_metadata.keys():
        operation_file = f"{data_metadata.get('github')}_{data_metadata.get('name')}_{data_metadata.get('version')}"
        operation_file += ".json"
        operation_file = os.path.join(file_dir, operation_file)

        if os.path.exists(operation_file):
            try:
                async with aiofiles.open(operation_file, mode='r') as f:
                    operation_data = await f.read()
                    op_file_data = json.loads(operation_data)

                    data_metadata['name'] = op_file_data.get('name', '[no-name]')
                    data_metadata['version'] = op_file_data.get('version', '0.0.1')
                    data_metadata['description'] = op_file_data.get('description', '[no-description]')
                    data_metadata['category_id'] = op_file_data.get('category_id', -1)
                    data_metadata['author'] = op_file_data.get('author', '[no-author]')
                    data_metadata['github'] = op_file_data.get('github', '[no-github]')
                    data_metadata['email'] = op_file_data.get('email', '[no-email]')
                    data_metadata['unique_id'] = op_file_data.get(
                        'unique_id', f"{data_metadata.get('github')}_{data_metadata.get('name')}_"
                                     f"{data_metadata.get('version')}")
                    data_metadata['action'] = op_file_data.get('action', None)
                    data_metadata['required_inputs'] = op_file_data.get('required_inputs', {})
                    data_metadata['parent_operation'] = op_file_data.get('parent_operation', None)
                    data_metadata['inheritance'] = op_file_data.get('inheritance', [])
                    data_metadata['is_loop'] = op_file_data.get('is_loop', False)
                    data_metadata['is_cpu_bound'] = op_file_data.get('is_cpu_bound', False)
                    data_metadata['is_gpu_bound'] = op_file_data.get('is_gpu_bound', False)
                    data_metadata['parallel'] = op_file_data.get('parallel', False)

            except Exception as e:
                CustomLogger().error(e, 'FileDiskOperations')

        else:
            CustomLogger().error(FileNotFoundError(f"Operation file not found for operation: {operation_file}"),
                                 'FileDiskOperations')

    if parent_operation is not None:
        data_metadata['parent_operation'] = parent_operation

    if isinstance(data_metadata.get('parent_operation', None), dict):
        try:
            data_metadata['parent_operation'] = await from_dict(
                data=data_metadata.get('parent_operation', {}),
                file_dir=file_dir
            )
        except Exception as e:
            CustomLogger().error(e, 'FileDiskOperations')
            data_metadata['parent_operation'] = None
    else:
        data_metadata['parent_operation'] = None

    if data_metadata.get('inheritance') is not None:
        if isinstance(data_metadata.get('inheritance'), list):
            children = data_metadata.get('inheritance')
            data_metadata['inheritance'] = []
            for child in children:
                if isinstance(child, dict):
                    try:
                        child_op = await from_dict(
                            data=child,
                            file_dir=file_dir
                        )
                        data_metadata['inheritance'].append(child_op)
                    except Exception as e:
                        CustomLogger().error(e, 'FileDiskOperations')

    return data_metadata

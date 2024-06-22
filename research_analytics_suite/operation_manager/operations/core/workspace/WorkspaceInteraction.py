"""
WorkspaceInteraction Module

Contains functionality for workspace interactions in an operation.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

import json
import os

import aiofiles


def pack_as_local_reference(operation) -> dict:
    """Provide a reference to the unique_id, name, and version of the operation."""
    return {
        'unique_id': operation.unique_id,
        'version': operation.version,
        'name': operation.name,
    }


def pack_for_save(operation) -> dict:
    """Provide a dictionary representation of the operation."""

    _child_operations = None
    if operation.child_operations is not None:
        _child_operations = [child.pack_as_local_reference() for child in operation.child_operations.values()]

    return {
        'unique_id': operation.unique_id,
        'version': operation.version,
        'name': operation.name,
        'action': operation.action,
        'persistent': operation.persistent,
        'concurrent': operation.concurrent,
        'is_cpu_bound': operation.is_cpu_bound,
        'dependencies': operation.dependencies if operation.dependencies else None,
        'parent_operation': operation.parent_operation.pack_as_local_reference() if operation.parent_operation else None,
        'child_operations': _child_operations if _child_operations else None,
        'result_variable_id': operation.result_variable_id,
    }


async def save_operation_in_workspace(operation, overwrite: bool = False):
    """
    Save the BaseOperation object to disk.

    Args:
        overwrite (bool, optional): Whether to overwrite the existing operation file. Defaults to False.
    """
    file_ext = f".json"
    stripped_state = pack_for_save(operation)

    dir_path = (f"{operation.config.BASE_DIR}/{operation.config.WORKSPACE_NAME}/"
                f"{operation.config.WORKSPACE_OPERATIONS_DIR}")
    os.makedirs(dir_path, exist_ok=True)

    name = f"{operation.name}_{operation.short_id}"
    if operation.version > 0:
        name = f"{name}_{operation.short_id}-{operation.version}"

    if operation.version == 0 and os.path.exists(f"{dir_path}/{name}{file_ext}"):
        if not overwrite:
            operation._version = 1
            while True:
                name = f"{operation.name}_{operation.short_id}-{operation.version}"
                if not os.path.exists(f"{dir_path}/{name}{file_ext}"):
                    break
                operation.version += 1

    file_path = f"{dir_path}/{name}{file_ext}"

    async with aiofiles.open(file_path, 'w') as file:
        await file.write(json.dumps(stripped_state))


async def get_result(operation) -> tuple[dict, str]:
    """
    Retrieve the results of the operation from the workspace.

    Returns:
        dict[name, value]: The name of the variable and its value.
        str: The memory_id location of the stored variable.
    """
    try:
        _memory_id, _value = await operation.workspace.get_user_variable_value(name=f"result_{operation.name}",
                                                                               memory_id=f'{operation.runtime_id}')
        return _value, _memory_id
    except Exception as e:
        operation.logger.error(Exception(f"Error retrieving result for operation '{operation.name}': {e}"), operation)

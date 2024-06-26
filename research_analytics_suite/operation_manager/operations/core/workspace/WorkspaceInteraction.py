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
        'category_id': operation.category_id,
        'author': operation.author,
        'github': operation.github,
        'version': operation.version,
        'name': operation.name,
        'description': operation.description,
    }


def pack_for_save(operation) -> dict:
    """Provide a dictionary representation of the operation."""

    _child_operations = None
    if operation.child_operations is not None:
        _child_operations = [pack_as_local_reference(child) for child in operation.child_operations.values()]

    return {
        'unique_id': operation.unique_id,
        'category_id': operation.category_id,
        'version': operation.version,
        'name': operation.name,
        'author': operation.author,
        'github': operation.github,
        'email': operation.email,
        'description': operation.description,
        'action': operation.action,
        'persistent': operation.persistent,
        'concurrent': operation.concurrent,
        'is_cpu_bound': operation.is_cpu_bound,
        'dependencies': operation.dependencies if operation.dependencies else None,
        'parent_operation': pack_as_local_reference(operation.parent_operation) if operation.parent_operation else None,
        'child_operations': _child_operations if _child_operations else None,
    }


async def save_operation_in_workspace(operation, overwrite: bool = False):
    """
    Save the BaseOperation object to disk.

    Args:
        operation (BaseOperation): The operation to save.
        overwrite (bool, optional): Whether to overwrite the existing operation file. Defaults to False.
    """
    file_ext = f".json"
    stripped_state = pack_for_save(operation)

    dir_path = (f"{operation.config.BASE_DIR}/{operation.config.WORKSPACE_NAME}/"
                f"{operation.config.WORKSPACE_OPERATIONS_DIR}")
    os.makedirs(dir_path, exist_ok=True)

    name = f"{stripped_state['github']}_{stripped_state['name']}_{stripped_state['version']}"

    if os.path.exists(os.path.join(dir_path, f"{name}{file_ext}")):
        if not overwrite:
            appended_version = 1
            while True:
                name = (f"{stripped_state['github']}_{stripped_state['name']}_"
                        f"{stripped_state['version']}-{appended_version}")
                if not os.path.exists(f"{dir_path}/{name}{file_ext}"):
                    operation.version = f"{operation.version}-{appended_version}"
                    stripped_state['version'] = f"{operation.version}"
                    break
                appended_version += 1

    file_path = f"{dir_path}/{name}{file_ext}"

    async with aiofiles.open(file_path, 'w') as file:
        await file.write(json.dumps(stripped_state, indent=4))

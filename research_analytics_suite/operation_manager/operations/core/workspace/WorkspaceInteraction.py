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
from research_analytics_suite.commands import command


@command
def pack_as_local_reference(operation) -> dict:
    """Provide a reference to the unique_id, name, and version of the operation."""
    return {
        'name': operation.name,
        'version': operation.version,
        'description': operation.description,
        'category_id': operation.category_id,
        'author': operation.author,
        'github': operation.github,
        'unique_id': operation.unique_id,
    }


@command
def pack_for_save(operation) -> dict:
    """Provide a dictionary representation of the operation."""

    _inheritance = None
    if operation.inheritance is not None:
        _inheritance = [pack_as_local_reference(child) for child in operation.inheritance]

    return {
        'name': operation.name,
        'version': operation.version,
        'description': operation.description,
        'category_id': operation.category_id,
        'author': operation.author,
        'github': operation.github,
        'email': operation.email,
        'unique_id': operation.unique_id,
        'action': operation.action,
        'required_inputs': operation.required_inputs if operation.required_inputs else {},
        'parent_operation': pack_as_local_reference(operation.parent_operation) if operation.parent_operation else None,
        'inheritance': _inheritance if _inheritance else [],
        'is_loop': operation.is_loop,
        'is_cpu_bound': operation.is_cpu_bound,
        'parallel': operation.parallel,
    }


@command
async def save_operation_in_workspace(operation, overwrite: bool = False):
    """
    Save the BaseOperation object to disk.

    Args:
        operation (BaseOperation): The operation to save.
        overwrite (bool, optional): Whether to overwrite the existing operation file. Defaults to False.
    """
    file_ext = ".json"
    stripped_state = pack_for_save(operation)

    dir_path = os.path.join(operation.config.BASE_DIR, "workspaces", operation.config.WORKSPACE_NAME, operation.config.WORKSPACE_OPERATIONS_DIR)
    os.makedirs(dir_path, exist_ok=True)

    name = f"{stripped_state['github']}_{stripped_state['name']}_{stripped_state['version']}"

    if os.path.exists(os.path.join(f"{dir_path}", f"{name}{file_ext}")):
        if not overwrite:
            appended_version = 1
            while True:
                name = f"{stripped_state['github']}_{stripped_state['name']}_{stripped_state['version']}-{appended_version}"
                if not os.path.exists(os.path.join(f"{dir_path}", f"{name}{file_ext}")):
                    operation.version = f"{operation.version}-{appended_version}"
                    stripped_state['version'] = f"{operation.version}"
                    break
                appended_version += 1

    file_path = os.path.join(f"{dir_path}", f"{name}{file_ext}")

    async with aiofiles.open(file_path, 'w') as file:
        await file.write(json.dumps(stripped_state, indent=4))

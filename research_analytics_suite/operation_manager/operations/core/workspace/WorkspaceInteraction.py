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
from research_analytics_suite.operation_manager.operations.core.memory.OperationAttributes import OperationAttributes
from research_analytics_suite.utils import Config


@command
def pack_as_local_reference(operation: OperationAttributes) -> dict:
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
async def save_operation_in_workspace(operation_attributes: OperationAttributes, overwrite: bool = False):
    """
    Save the BaseOperation object to disk.

    Args:
        operation_attributes (OperationAttributes): The attributes of the operation to save.
        overwrite (bool, optional): Whether to overwrite the existing operation file. Defaults to False.
    """
    file_ext = ".json"
    attributes_to_save = operation_attributes.export_attributes()

    dir_path = os.path.join(Config().BASE_DIR, "workspaces", Config().WORKSPACE_NAME, Config().WORKSPACE_OPERATIONS_DIR)
    os.makedirs(dir_path, exist_ok=True)

    name = f"{attributes_to_save['github']}_{attributes_to_save['name']}_{attributes_to_save['version']}"

    if os.path.exists(os.path.join(f"{dir_path}", f"{name}{file_ext}")):
        if not overwrite:
            appended_version = 1
            while True:
                _attempt = f"{name}-{appended_version}"
                if not os.path.exists(os.path.join(f"{dir_path}", f"{_attempt}{file_ext}")):
                    attributes_to_save['version'] = f"{attributes_to_save['version']}-{appended_version}"
                    name = _attempt
                    break
                appended_version += 1

    file_path = os.path.normpath(os.path.join(f"{dir_path}", f"{name}{file_ext}"))

    async with aiofiles.open(file_path, 'w') as file:
        await file.write(json.dumps(attributes_to_save, indent=4))

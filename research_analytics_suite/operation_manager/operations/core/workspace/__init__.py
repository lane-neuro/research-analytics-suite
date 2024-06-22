"""
Workspace Package

Provides functionalities for workspace interactions, loading, and saving operations.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

from .WorkspaceInteraction import save_operation_in_workspace, get_result, pack_as_local_reference, pack_for_save
from .FileDiskOperations import load_from_disk, load_operation_group, from_dict

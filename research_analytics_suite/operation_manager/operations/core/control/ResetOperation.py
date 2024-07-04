"""
ResetOperation Module

Contains functionality to reset an operation.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""


async def reset_operation(operation, child_operations=False):
    """
    Reset the operation and all child operations, if applicable.
    """
    operation.is_ready = False

    if (operation.status == "running"
            or operation.status == "paused"
            or operation.status == "completed"
            or operation.status == "error"):
        if child_operations and operation.inheritance is not None:
            await operation.reset_child_operations()
        await operation.stop()
        await operation.start()
        operation.progress = 0
        operation.add_log_entry(f"[RESET] {operation.name}")
    else:
        operation.add_log_entry(f"[RESET] {operation.name} - Already reset")

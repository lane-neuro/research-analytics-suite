"""
PauseOperation Module

Contains functionality to pause an operation.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import asyncio


async def pause_operation(operation, child_operations=False):
    """
    Pause the operation and all child operations, if applicable.
    """
    if operation.status == "running":
        try:
            operation.is_ready = False

            if child_operations and operation.child_operations is not None:
                await _pause_child_operations(operation)

            await operation.pause_event.clear()
            operation.status = "paused"
        except Exception as e:
            operation.handle_error(e)
        finally:
            operation.add_log_entry(f"[PAUSE] {operation.name}")
    else:
        operation.add_log_entry(f"[PAUSE] {operation.name} - Already paused")


async def _pause_child_operations(operation):
    """
    Pause all child operations.
    """
    tasks = [op.pause(True) for op in operation.child_operations.values()]
    await asyncio.gather(*tasks)

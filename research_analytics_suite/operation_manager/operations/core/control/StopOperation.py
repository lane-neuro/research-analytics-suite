"""
StopOperation Module

Contains functionality to stop an operation.

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


async def stop_operation(operation, child_operations=False):
    """
    Stop the operation and all child operations, if applicable.
    """
    if operation.status == "running":
        try:
            operation.is_ready = False

            if child_operations and operation.inheritance is not None:
                await stop_child_operations(operation)
            operation.task.cancel()
            operation.status = "stopped"
        except Exception as e:
            operation.handle_error(e)
        finally:
            operation.add_log_entry(f"[STOP] {operation.name}")
    else:
        operation.add_log_entry(f"[STOP] {operation.name} - Already stopped")


async def stop_child_operations(operation):
    """
    Stop all child operations.
    """
    tasks = [child.stop() for child in operation.inheritance]
    await asyncio.gather(*tasks)

"""
ResumeOperation Module

Contains functionality to resume an operation.

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


async def resume_operation(operation, with_inherited=False):
    """
    Resume the operation and all child operations, if applicable.
    """
    if operation.status == "paused":
        try:
            operation.is_ready = True

            if with_inherited and operation.inheritance:
                await resume_child_operations(operation)
            await operation.pause_event.set()
            operation.status = "running"
        except Exception as e:
            operation.handle_error(e)
        finally:
            operation.add_log_entry(f"[RESUME] {operation.name}")
    else:
        operation.add_log_entry(f"[RESUME] {operation.name} - Already running")


async def resume_child_operations(operation):
    """
    Resume all child operations.
    """
    if not operation.inheritance:
        return
    tasks = [op.resume() for op in operation.inheritance]
    await asyncio.gather(*tasks)

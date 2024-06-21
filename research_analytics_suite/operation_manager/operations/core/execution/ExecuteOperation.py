"""
ExecuteOperation Module

Contains functionality to execute an operation.

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
from .PrepareAction import prepare_action_for_exec


async def execute_operation(operation):
    """
    Execute the operation and all child operations.
    """
    try:
        if operation.child_operations is not None:
            await operation.execute_child_operations()
        await prepare_action_for_exec(operation)
        await run_operations(operation, [operation])
        if not operation.persistent:
            operation._status = "completed"
            operation.add_log_entry(f"[COMPLETE]")
    except Exception as e:
        operation.handle_error(e)


async def run_operations(operation, operations):
    """
    Run the specified operations.
    """
    tasks = []
    for op in operations:
        if op.status != "completed":
            if op.action is not None:
                tasks.append(op.execute_action())

    if operation.concurrent and tasks and len(tasks) > 0:
        await asyncio.gather(*tasks)
    elif not operation.concurrent and tasks and len(tasks) > 0:
        for task in tasks:
            await task
            operation.add_log_entry(f"[RESULT] {operation.result_variable_id}")

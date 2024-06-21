"""
StartOperation Module

Contains functionality to start an operation.

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


async def start_operation(operation):
    """
    Start the operation and all child operations.
    """
    try:
        if operation.child_operations is not None:
            await _start_child_operations(operation)
        operation.status = "started"
    except Exception as e:
        operation.handle_error(e)


async def _start_child_operations(operation):
    """
    Start all child operations.
    """
    tasks = [op.start() for op in operation.child_operations.values()]
    if operation.concurrent:
        await asyncio.gather(*tasks)
    else:
        for task in tasks:
            await task

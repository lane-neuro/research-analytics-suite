"""
ChildOperationManagement Module

Contains functionality to manage child operations in an operation.

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
import os

from research_analytics_suite.commands import command


@command
async def add_child_operation(operation, child_operation) -> None:
    """
    Add a child operation to the current operation.

    Args:
        operation: The parent operation.
        child_operation: The child operation to be added.
    """
    from research_analytics_suite.operation_manager.operations.core import BaseOperation
    from research_analytics_suite.utils import Config

    if isinstance(child_operation, dict):
        _file_dir = os.path.join(Config().BASE_DIR, Config().WORKSPACE_NAME, Config().WORKSPACE_OPERATIONS_DIR)
        child_operation = await BaseOperation.from_dict(data=child_operation, parent_operation=operation,
                                                        file_dir=_file_dir)

    if not isinstance(child_operation, BaseOperation):
        operation.handle_error("operation must be an instance of BaseOperation")
        return

    if not isinstance(child_operation.parent_operation, BaseOperation):
        child_operation.parent_operation = operation

    for child in operation.inheritance or []:
        if child_operation.runtime_id == child.runtime_id:
            operation.add_log_entry(f"[CHILD] (runtime_id already exists) {child_operation.name} - doing nothing")
            return

    operation.inheritance.append(child_operation)

    operation.add_log_entry(f"[CHILD] (added) {child_operation.name}")


@command
async def link_child_operation(operation, child_operation) -> bool:
    """
    Link a child operation to the current operation.

    Args:
        operation: The parent operation.
        child_operation: The child operation to be linked.
    """
    from research_analytics_suite.operation_manager.operations.core import BaseOperation
    if not isinstance(child_operation, BaseOperation):
        operation.handle_error("operation must be an instance of BaseOperation")
        return False

    for child in operation.inheritance:
        if child_operation.runtime_id == child.runtime_id:
            operation.add_log_entry(f"[CHILD] (runtime_id already exists) {child_operation.name} - doing nothing")
            return True

    child_operation.parent_operation = operation
    operation.inheritance.append(child_operation)

    operation.add_log_entry(f"[CHILD] (linked) {child_operation.name}")
    return True


@command
async def remove_child_operation(operation, child_operation) -> None:
    """
    Remove a child operation from the current operation.

    Args:
        operation: The parent operation.
        child_operation: The child operation to be removed.
    """

    from research_analytics_suite.operation_manager.operations.core import BaseOperation
    if not isinstance(child_operation, BaseOperation):
        operation.handle_error("operation must be an instance of BaseOperation")
        return

    child_operation.parent_operation = None
    for child in operation.inheritance:
        if child_operation.runtime_id == child.runtime_id:
            operation.inheritance.pop(child.runtime_id)
            break
    operation.add_log_entry(f"[CHILD] (removed) {child_operation.name}")


async def start_child_operations(operation) -> None:
    """
    Start all child operations.

    Args:
        operation: The parent operation.
    """
    tasks = [child.start_operation() for child in operation.inheritance]
    if operation.parallel:
        await asyncio.gather(*tasks)
    else:
        for task in tasks:
            await task


async def pause_child_operations(operation) -> None:
    """
    Pause all child operations.

    Args:
        operation: The parent operation.
    """
    tasks = [child.pause(True) for child in operation.inheritance]
    await asyncio.gather(*tasks)


async def resume_child_operations(operation) -> None:
    """
    Resume all child operations.

    Args:
        operation: The parent operation.
    """
    tasks = [child.resume() for child in operation.inheritance]
    await asyncio.gather(*tasks)


async def stop_child_operations(operation) -> None:
    """
    Stop all child operations.

    Args:
        operation: The parent operation.
    """
    tasks = [child.stop() for child in operation.inheritance]
    await asyncio.gather(*tasks)


async def reset_child_operations(operation) -> None:
    """
    Reset all child operations.

    Args:
        operation: The parent operation.
    """
    tasks = [child.reset() for child in operation.inheritance]
    await asyncio.gather(*tasks)

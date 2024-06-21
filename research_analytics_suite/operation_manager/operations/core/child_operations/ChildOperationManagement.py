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


async def add_child_operation(operation, child_operation, dependencies: dict = None):
    """
    Add a child operation to the current operation.

    Args:
        operation: The parent operation.
        child_operation: The child operation to be added.
        dependencies (dict, optional): List of operation names that the child operation depends on.
                                        Defaults to None.
    """
    from research_analytics_suite.operation_manager.operations.core import BaseOperation

    if isinstance(child_operation, dict):
        _file_dir = os.path.join(operation.config.BASE_DIR, operation.config.WORKSPACE_NAME,
                                 operation.config.WORKSPACE_OPERATIONS_DIR)
        child_operation = await BaseOperation.from_dict(data=child_operation, parent_operation=operation,
                                                        file_dir=_file_dir)

    if not isinstance(child_operation, BaseOperation):
        operation.handle_error("operation must be an instance of BaseOperation")
        return

    if dependencies is not None:
        operation.dependencies[child_operation.unique_id] = dependencies.get(child_operation.unique_id)

    if not isinstance(child_operation.parent_operation, BaseOperation):
        child_operation.parent_operation = operation

    if operation.child_operations is None:
        operation._child_operations = dict()
    if child_operation.runtime_id not in operation.child_operations.keys():
        operation.child_operations[child_operation.runtime_id] = child_operation

    operation.add_log_entry(f"[CHILD] (added) {child_operation.name}")


async def link_child_operation(operation, child_operation, dependencies: dict = None):
    """
    Link a child operation to the current operation.

    Args:
        operation: The parent operation.
        child_operation: The child operation to be linked.
        dependencies (dict, optional): The dependencies of the child operation. Defaults to None.
    """
    from research_analytics_suite.operation_manager.operations.core import BaseOperation
    if not isinstance(child_operation, BaseOperation):
        operation.handle_error("operation must be an instance of BaseOperation")
        return False

    if not isinstance(dependencies, dict):
        dependencies = dict()

    if child_operation.runtime_id not in operation.child_operations.keys():
        if operation.child_operations is None:
            operation.child_operations = dict()
        operation.child_operations[child_operation.runtime_id] = child_operation
    else:
        operation.add_log_entry(f"[CHILD] (runtime_id already exists) {child_operation.name} - doing nothing")
        return True

    if operation.dependencies is not None:
        if child_operation.unique_id not in operation.dependencies and dependencies.get(child_operation.unique_id):
            operation.dependencies[child_operation.unique_id] = dependencies.get(child_operation.unique_id)

    child_operation.parent_operation = operation
    operation.add_log_entry(f"[CHILD] (linked) {child_operation.name}")
    return True


def remove_child_operation(operation, child_operation):
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
    del operation.child_operations[child_operation.runtime_id]
    if child_operation.unique_id in operation.dependencies.keys():
        del operation.dependencies[child_operation.unique_id]
    operation.add_log_entry(f"[CHILD] (removed) {child_operation.name}")


async def start_child_operations(operation):
    """
    Start all child operations.

    Args:
        operation: The parent operation.
    """
    tasks = [op.start() for op in operation.child_operations.values()]
    if operation.concurrent:
        await asyncio.gather(*tasks)
    else:
        for task in tasks:
            await task


async def pause_child_operations(operation):
    """
    Pause all child operations.

    Args:
        operation: The parent operation.
    """
    tasks = [op.pause(True) for op in operation.child_operations.values()]
    await asyncio.gather(*tasks)


async def resume_child_operations(operation):
    """
    Resume all child operations.

    Args:
        operation: The parent operation.
    """
    tasks = [op.resume() for op in operation.child_operations.values()]
    await asyncio.gather(*tasks)


async def stop_child_operations(operation):
    """
    Stop all child operations.

    Args:
        operation: The parent operation.
    """
    tasks = [op.stop() for op in operation.child_operations.values()]
    await asyncio.gather(*tasks)


async def reset_child_operations(operation):
    """
    Reset all child operations.

    Args:
        operation: The parent operation.
    """
    tasks = [op.reset() for op in operation.child_operations.values()]
    await asyncio.gather(*tasks)

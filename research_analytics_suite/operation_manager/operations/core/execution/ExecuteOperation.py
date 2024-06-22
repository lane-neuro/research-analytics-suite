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
from concurrent.futures import ProcessPoolExecutor

from .PrepareAction import prepare_action_for_exec


async def execute_operation(operation):
    """
    Execute the operation and all child operations.
    """
    try:
        if operation.child_operations is not None:
            await execute_child_operations(operation)

        await prepare_action_for_exec(operation)
        await run_operations(operation, [operation])
        if not operation.persistent:
            operation.status = "completed"
            operation.add_log_entry(f"[COMPLETE]")
    except Exception as e:
        operation.handle_error(e)


async def execute_child_operations(parent_operation):
    """
    Execute all child operations.
    """
    if not parent_operation.dependencies:
        if parent_operation.child_operations is not None:
            await run_operations(parent_operation, parent_operation.child_operations.values())
    else:
        execution_order = parent_operation.determine_execution_order()
        await run_operations(parent_operation, execution_order)


async def run_operations(operation, operations):
    """
    Run the specified operations.
    """
    tasks = []
    for op in operations:
        if op.status != "completed":
            if op.action_callable is not None:
                tasks.append(op.execute_action())

    if operation.concurrent and tasks and len(tasks) > 0:
        await asyncio.gather(*tasks)
    elif not operation.concurrent and tasks and len(tasks) > 0:
        for task in tasks:
            await task
            operation.add_log_entry(f"[RESULT] {operation.result_variable_id}")


async def execute_action(operation):
    """
    Execute the action associated with the operation.
    """
    try:
        if operation.is_cpu_bound:
            with ProcessPoolExecutor() as executor:
                operation._status = "running"
                operation.add_log_entry(f"[RUN] {operation.name}: CPU-bound Operation")
                _exec_output = await asyncio.get_event_loop().run_in_executor(executor, operation.action_callable)
                if _exec_output is not None:
                    operation.result_variable_id, _result = await operation.workspace.add_user_variable(
                        name=f"result_{operation.name}",
                        value=_exec_output.result() if asyncio.isfuture(_exec_output) else _exec_output,
                        memory_id=f'{operation.runtime_id}')
                    operation.add_log_entry(f"[RESULT] {operation.result_variable_id} {_result}")
        else:
            if operation.action_callable is not None:
                if callable(operation.action_callable):
                    operation._status = "running"
                    if asyncio.iscoroutinefunction(operation.action_callable):
                        operation.add_log_entry(f"[RUN - ASYNC] {operation.name}")
                        _exec_output = await operation.action_callable()
                        if _exec_output is not None:
                            operation.result_variable_id, _result = await operation.workspace.add_user_variable(
                                name=f"result_{operation.name}",
                                value=_exec_output.result() if asyncio.isfuture(_exec_output) else _exec_output,
                                memory_id=f'{operation.runtime_id}')
                            operation.add_log_entry(f"[RESULT] {operation.result_variable_id} {_result}")

                    else:
                        operation.add_log_entry(f"[RUN] {operation.name}")
                        _exec_output = operation.action_callable()
                        if _exec_output is not None:
                            operation.result_variable_id, _result = await operation.workspace.add_user_variable(
                                name=f"result_{operation.name}",
                                value=_exec_output.result() if asyncio.isfuture(_exec_output) else _exec_output,
                                memory_id=f'{operation.runtime_id}')
                            operation.add_log_entry(f"[RESULT] {operation.result_variable_id} {_result}")
            else:
                operation.handle_error(Exception("No action provided for operation"))
    except Exception as e:
        operation.handle_error(e)

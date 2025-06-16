import asyncio
from concurrent.futures import ProcessPoolExecutor
from typing import List

from research_analytics_suite.operation_manager.computation.GPUComputation import gpu_computation
from research_analytics_suite.utils import CustomLogger
from .PrepareAction import prepare_action_for_exec


async def execute_operation(operation):
    """
    Execute the operation and all child operations.
    """
    try:
        if operation.inheritance:
            await execute_inherited_operations(operation)

        # try:
        #     await operation.validate_inputs()
        # except ValueError or Exception as e:
        #     operation.handle_error(e)
        #     return

        await prepare_action_for_exec(operation)
        await run_operations(operation, [operation])

        if operation.parent_operation:
            for slot in operation.memory_outputs:
                await operation.parent_operation.add_input(slot)

        if not operation.is_loop:
            operation.status = "completed"
            operation.add_log_entry(f"[COMPLETE]")
    except Exception as e:
        operation.handle_error(e)


async def execute_inherited_operations(parent_operation):
    """
    Execute all child operations.
    """
    if not parent_operation.required_inputs:
        if parent_operation.inheritance:
            await run_operations(parent_operation, parent_operation.inheritance)
    else:
        execution_order = _determine_execution_order(parent_operation)
        await run_operations(parent_operation, execution_order)


def _determine_execution_order(parent_operation) -> List:
    """
    Determine the execution order of child operations based on required inputs.

    Returns:
        List[BaseOperation]: The execution order of child operations.
    """
    parent_operation.add_log_entry(f"Determining execution order")
    execution_order = []
    processed = set()
    while len(processed) < len(parent_operation.inheritance):
        for child in parent_operation.inheritance:
            if child.name not in processed and all(
                    dep in processed for dep in parent_operation.required_inputs.get(child.name, {})):
                execution_order.append(child)
                processed.add(child.name)
    return execution_order


async def run_operations(operation, operations):
    """
    Run the specified operations.
    """
    tasks = []
    for op in operations:
        if op.status != "completed":
            tasks.append(execute_action(op))

    if operation.parallel and tasks:
        await asyncio.gather(*tasks)
    elif tasks:
        for task in tasks:
            await task


async def execute_action(operation):
    """
    Execute the action associated with the operation.
    """
    from research_analytics_suite.data_engine.memory.MemoryManager import MemoryManager
    memory_manager = MemoryManager()

    try:
        operation.status = "running"
        operation.add_log_entry(f"[RUN] {operation.name}")

        if operation.is_cpu_bound:
            with ProcessPoolExecutor() as executor:
                _exec_output = await asyncio.get_event_loop().run_in_executor(executor, operation.action_callable)
        elif operation.is_gpu_bound:
            _exec_output = await asyncio.get_event_loop().run_in_executor(
                None, gpu_computation, operation.action_callable)
        else:
            _exec_output = await operation.action_callable() if asyncio.iscoroutinefunction(operation.action_callable) else operation.action_callable()

        if _exec_output is not None:
            _result = _exec_output.result() if asyncio.isfuture(_exec_output) else _exec_output
            CustomLogger().info(_result)

            # Ensure the result is a dictionary
            if not isinstance(_result, dict):
                CustomLogger().error(Exception(f"Operation {operation.name} did not return a dictionary."),
                                     operation.name)

            # Update memory slots with the result
            for key, value in _result.copy().items() if _result is not None else {}:
                await operation.add_output(key, value)
                _result.pop(key)

        operation.status = "completed"

    except Exception as e:
        operation.handle_error(e)

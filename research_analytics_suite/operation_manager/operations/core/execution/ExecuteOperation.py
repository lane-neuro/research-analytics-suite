import asyncio
from concurrent.futures import ProcessPoolExecutor
from typing import List

from research_analytics_suite.utils import CustomLogger
from .PrepareAction import prepare_action_for_exec


async def execute_operation(operation):
    """
    Execute the operation and all child operations.
    """
    try:
        if operation.inheritance:
            await execute_inherited_operations(operation)

        await operation.validate_memory_inputs()

        await prepare_action_for_exec(operation)
        await run_operations(operation, [operation])

        await operation.validate_memory_outputs()
        if operation.parent_operation:
            for slot in operation.memory_outputs.slots:
                await operation.parent_operation.add_memory_input_slot(slot)

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
    try:
        if operation.is_cpu_bound:
            with ProcessPoolExecutor() as executor:
                operation.status = "running"
                operation.add_log_entry(f"[RUN] {operation.name}: CPU-bound Operation")
                _exec_output = await asyncio.get_event_loop().run_in_executor(executor, operation.action_callable)
        else:
            operation.status = "running"
            operation.add_log_entry(f"[RUN - ASYNC] {operation.name}")
            _exec_output = operation.action_callable
            _exec_output = await _exec_output() if asyncio.iscoroutinefunction(_exec_output) else _exec_output()

        if _exec_output is not None:
            _result = _exec_output.result() if asyncio.isfuture(_exec_output) else _exec_output

            # Ensure the result is a dictionary
            if not isinstance(_result, dict):
                CustomLogger().error(Exception(f"Operation {operation.name} did not return a dictionary."),
                                     operation.name)

            # Update all memory output slots with the result of the operation
            for name, value in _result.items():
                slots = operation.memory_outputs.find_slots_by_name(name)
                if slots and len(slots) > 0:
                    for slot in slots:
                        slot.data = {name: (type(value), value)}
                        await operation.memory_outputs.update_slot(slot)
                else:
                    from research_analytics_suite.data_engine import MemorySlot
                    new_slot = MemorySlot(
                        memory_id=f'{operation.runtime_id}',
                        name=f"{name}",
                        operation_required=False,
                        data={name: (type(value), value)}
                    )
                    await operation.add_memory_output_slot(new_slot)

        operation.add_log_entry(f"[RESULT] {operation.memory_outputs.list_slots()}")
    except Exception as e:
        operation.handle_error(e)

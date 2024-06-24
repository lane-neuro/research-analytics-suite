import asyncio
import inspect
import types
from typing import Any


def action_serialized(operation) -> str:
    """Gets the serializable action to be executed by the operation."""
    if isinstance(operation.action, (types.MethodType, types.FunctionType)):
        action = inspect.getsource(operation.action)
    elif callable(operation.action):
        try:
            action = inspect.getsource(operation.action)
        except OSError:
            action = f"{operation.action}"
    elif isinstance(operation.action, str):
        action = operation.action
    else:
        action = None
    return action

async def prepare_action_for_exec(operation):
    """
    Prepare the action for execution.
    """
    _action = None
    try:
        # if operation.memory_inputs is not None:
        #     await operation.memory_inputs.preprocess_data()

        if isinstance(operation.action, str):
            code = operation.action
            if operation.memory_inputs and operation.memory_inputs.list_slots():
                _action = await _execute_code_action(code, operation.memory_inputs.list_slots())
                operation.add_log_entry(f"Memory Inputs: {operation.memory_inputs.list_slots()}")
            else:
                _action = await _execute_code_action(code, [])
            operation.add_log_entry(f"[CODE] {code}")
        elif callable(operation.action):
            if asyncio.iscoroutinefunction(operation.action):
                _action = operation.action
            elif isinstance(operation.action, types.MethodType):
                _action = operation.action
            else:
                t_action = operation.action
                operation.add_log_entry(f"Memory Inputs: {operation.memory_inputs.list_slots()}")
                _action = _execute_callable_action(t_action=t_action,
                                                   memory_inputs=operation.memory_inputs.list_slots() if
                                                   operation.memory_inputs else [])
        operation.action_callable = _action
    except Exception as e:
        operation.handle_error(e)


async def _execute_code_action(code, memory_inputs: list = None) -> callable:
    """
    Execute a code action.

    Args:
        code (str): The code to execute.
        memory_inputs (list): The inputs for the code action.

    Returns:
        callable: The action callable.
    """
    async def action() -> Any:
        locals_dict = {}
        if memory_inputs:
            for slot in memory_inputs:
                locals_dict[slot.name] = await slot.get_data_by_key(slot.name)
        print(locals_dict)
        try:
            exec(code, {}, locals_dict)
            # Ensure the result is a dictionary
            if not isinstance(locals_dict, dict):
                raise ValueError("The result of the executed code must be a dictionary.")
            return locals_dict
        except Exception as e:
            raise RuntimeError(f"Error executing code: {e}")

    return action


def _execute_callable_action(t_action, memory_inputs: list = None) -> callable:
    """
    Execute a callable action.

    Args:
        t_action (callable): The callable to execute.
        memory_inputs (list): The memory inputs to use for the action.

    Returns:
        callable: The action callable.
    """
    def action() -> Any:
        inputs = {slot.name: slot.data for slot in memory_inputs} if memory_inputs else {}
        _output = t_action(*inputs)
        if _output is not None:
            return _output
        return

    return action

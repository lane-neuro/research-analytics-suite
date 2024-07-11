import asyncio
import inspect
import types
from typing import Any, Callable
import ast

SAFE_BUILTINS = {
    'print': print,
    'range': range,
    'len': len,
    'int': int,
    'float': float,
    '__import__': __import__,
}

SAFE_MODULES = {
    'math': __import__('math'),
    'numpy': __import__('numpy'),
    'pandas': __import__('pandas'),
    'sklearn': __import__('sklearn'),
    'torch': __import__('torch'),
    'matplotlib': __import__('matplotlib'),
}


def action_serialized(action) -> str:
    """Gets the serializable action to be executed by the operation."""
    if isinstance(action, str):
        return action
    elif callable(action):
        try:
            source = inspect.getsource(action).strip()
            return source
        except (TypeError, OSError):
            try:
                # Attempt to get the qualified name for better clarity
                qualname = action.__qualname__
                module = action.__module__
                return f"<callable {module}.{qualname}>"
            except AttributeError:
                return repr(action)
    elif isinstance(action, property):
        return f"<property object at {hex(id(action))}>"
    else:
        return repr(action)



async def prepare_action_for_exec(operation):
    """
    Prepare the action for execution.
    """
    _action = None
    try:
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


async def _execute_code_action(code: str, memory_inputs: list = None) -> Callable[[], Any]:
    """
    Execute a code action.

    Args:
        code (str): The code to execute.
        memory_inputs (list): The inputs for the code action.

    Returns:
        callable: The action callable.
    """

    async def action() -> Any:

        # Extract the actual data values from the MemorySlot tuples
        inputs = {slot.name: await slot.get_data_by_key(slot.name) for slot in memory_inputs} if memory_inputs else {}
        for k, v in inputs.items():
            if isinstance(v, tuple):
                if v[0] is type(None):
                    inputs[k] = None
                elif v[0] == 'module':
                    try:
                        inputs[k] = __import__(v[1])
                    except ImportError:
                        inputs[k] = None
                elif (v[0] == 'function' or v[0] == 'method' or v[0] == 'builtin_function_or_method' or
                      v[0] == 'method-wrapper' or v[0] == 'class'):
                    inputs[k] = v[1]
                else:
                    inputs[k] = v[0](v[1])
            else:
                inputs[k] = v

        # Create a restricted execution environment
        safe_globals = {"__builtins__": SAFE_BUILTINS}
        # noinspection PyTypeChecker
        safe_globals.update(SAFE_MODULES)

        try:
            parsed_code = ast.parse(code, mode='exec')
            exec(compile(parsed_code, '<string>', 'exec'), safe_globals, inputs)
            return inputs  # Return the modified inputs dictionary with updated values
        except Exception as e:
            raise RuntimeError(f"Error executing code: {e}")

    return action


def _execute_callable_action(t_action, memory_inputs: list = None):
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
        # Extract the actual data values from the MemorySlot tuples
        inputs = {k: v for k, (t, v) in inputs.items()}
        _output = t_action(*inputs.values())
        if _output is not None:
            return _output
        return

    return action

import asyncio
import inspect
import types
from typing import Callable
import ast

from research_analytics_suite.commands import command
from research_analytics_suite.utils.LazyModuleLoader import LazyModuleLoader

SAFE_BUILTINS = {
    'print': print,
    'range': range,
    'len': len,
    'int': int,
    'float': float,
    '__import__': __import__,
}


@command
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
    from research_analytics_suite.utils import CustomLogger

    _action = None
    try:
        if operation.action is None:
            if callable(operation.execute):
                operation.action = operation.execute
            else:
                CustomLogger().error(TypeError("operation.execute is not callable and no action is provided."),
                                     operation.name)
                return

        if isinstance(operation.action, str):
            code = operation.action

            async def _code_action():
                if operation.memory_inputs:
                    result = await _execute_code_action(code, operation.memory_inputs)
                    CustomLogger().debug(f"Memory Inputs: {operation.memory_inputs}")
                    operation.add_log_entry(f"Memory Inputs: {operation.memory_inputs}")
                else:
                    CustomLogger().debug(f"No memory inputs for code action: {operation.name}")
                    result = await _execute_code_action(code, set())
                operation.add_log_entry(f"[CODE] {code}")
                return result

            _action = _code_action
            CustomLogger().debug(f"Code prepared for execution: {operation.name}")
        elif callable(operation.action):
            if asyncio.iscoroutinefunction(operation.action):
                CustomLogger().debug(f"Action is a coroutine: {operation.action}")
                _action = operation.action
            elif isinstance(operation.action, types.MethodType):
                CustomLogger().debug(f"Action is a method: {operation.action}")
                _action = operation.action
            else:
                CustomLogger().debug(f"Action is a callable: {operation.action}")
                t_action = operation.action
                operation.add_log_entry(f"Memory Inputs: {operation.memory_inputs}")
                _action = lambda: _execute_callable_action(t_action=t_action, memory_inputs=operation.memory_inputs)
            CustomLogger().debug(f"Callable prepared for execution: {operation.name}")
        operation.action_callable = _action
        CustomLogger().debug(f"Action prepared for execution: {operation.name}")
    except Exception as e:
        operation.handle_error(e)


async def _execute_code_action(code: str, memory_inputs: set = None) -> Callable[[], any]:
    """
    Execute a code action.

    Args:
        code (str): The code to execute.
        memory_inputs (list): The inputs for the code action.

    Returns:
        callable: The action callable.
    """
    from research_analytics_suite.data_engine.memory.MemoryManager import MemoryManager
    memory_manager = MemoryManager()

    async def action() -> any:
        inputs = {}

        for slot_id in memory_inputs:
            _name = await memory_manager.slot_name(slot_id)
            _data = await memory_manager.slot_data(slot_id)
            inputs[_name] = _data

        # Create a restricted execution environment
        safe_globals = {"__builtins__": SAFE_BUILTINS}
        # noinspection PyTypeChecker

        safe_globals.update(LazyModuleLoader().get_all_modules())

        try:
            parsed_code = ast.parse(code, mode='exec')
            exec(compile(parsed_code, '<string>', 'exec'), safe_globals, inputs)
            return inputs  # Return the modified inputs dictionary with updated values
        except Exception as e:
            raise RuntimeError(f"Error executing code: {e}")

    return action


def _execute_callable_action(t_action, memory_inputs: set = None):
    """
    Execute a callable action.

    Args:
        t_action (callable): The callable to execute.
        memory_inputs (set): The memory inputs to use for the action.

    Returns:
        callable: The action callable.
    """
    from research_analytics_suite.data_engine.memory.MemoryManager import MemoryManager
    _memory_manager = MemoryManager()

    def action() -> any:
        inputs = {}
        for _slot_id in memory_inputs:
            _name = _memory_manager.slot_name(_slot_id)
            _data = _memory_manager.slot_data(_slot_id)
            inputs[_name] = _data

        _output = t_action(**inputs)
        if _output is not None:
            return _output
        return

    return action

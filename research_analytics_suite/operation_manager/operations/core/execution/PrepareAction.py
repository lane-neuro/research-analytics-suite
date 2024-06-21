"""
PrepareAction Module

Contains functionality to prepare an action for execution in an operation.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import types
from typing import Any


async def prepare_action_for_exec(operation):
    """
    Prepare the action for execution.
    """
    try:
        if isinstance(operation.action, str):
            code = operation.action
            operation.action = _execute_code_action(code)
            operation.add_log_entry(f"[CODE] {code}")
        elif callable(operation.action):
            if isinstance(operation.action, types.MethodType):
                operation._action = operation.action
            else:
                t_action = operation.action
                operation.action = _execute_callable_action(t_action)
    except Exception as e:
        operation.handle_error(e)


def _execute_code_action(code) -> callable:
    """
    Execute a code action.

    Args:
        code (str): The code to execute.

    Returns:
        callable: The action callable.
    """
    def action():
        _output = dict()
        exec(code, {}, _output)
        return _output

    return action


def _execute_callable_action(t_action) -> callable:
    """
    Execute a callable action.

    Args:
        t_action (callable): The callable to execute.

    Returns:
        callable: The action callable.
    """
    def action() -> Any:
        _output = t_action()
        if _output is not None:
            return _output
        return

    return action

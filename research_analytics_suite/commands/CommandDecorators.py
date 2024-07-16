"""
Command decorators for registering commands.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from __future__ import annotations
import inspect
from research_analytics_suite.commands.utils.text_utils import clean_description, get_class_from_method

temp_command_registry = []
registered_methods = set()


def register_command(func, cls=None):
    """
    Registers a command function with the command registry.
    Args:
        func: The command function to register.
        cls: The class object associated with the command function.
    """
    sig = inspect.signature(func)
    class_name = get_class_from_method(func)[0]
    type_hints = func.__annotations__
    args = [
        {'name': param, 'type': type_hints.get(param, any)} for param in sig.parameters if param not in ('self', 'cls')
    ]
    return_type = type_hints.get('return', None)
    return_type = return_type if isinstance(return_type, list) else [return_type] if return_type else None
    description = clean_description(func.__doc__) if func.__doc__ else None
    is_method = 'self' in sig.parameters or 'cls' in sig.parameters

    temp_command_registry.append({
        'func': func,
        'name': func.__name__,
        'description': description,
        'class_name': class_name,
        'class_obj': cls if cls else None,
        'instances': {id(cls): cls} if cls else {},
        'args': args,
        'return_type': return_type,
        'is_method': is_method,
        '_is_command': True
    })


def link_class_commands(cls):
    """
    Decorator to associate each class instance with the corresponding command functions at runtime.
    This decorator auto-detects all command methods in a class and registers them with the
    class instance information.
    Args:
        cls: The class to link commands to.
    """
    global registered_methods

    for name, method in inspect.getmembers(
            cls, predicate=lambda x: inspect.isfunction(x) or inspect.ismethod(x) or inspect.iscoroutinefunction(x)):
        if hasattr(method, '_is_command') and (cls.__name__, name) not in registered_methods:
            register_command(method, cls)

    return cls


def command(func=None):
    """
    Decorator to register a command.
    This decorator auto-detects the command name, argument names, types, and return type.
    Args:
        func: The command function to register.
    """
    global registered_methods
    tmp_class = get_class_from_method(func)

    def wrapper(f):
        f._is_command = True
        register_command(f, tmp_class[0])
        if tmp_class[0]:
            registered_methods.add(tmp_class)
        return f

    if func is None:
        return wrapper
    else:
        return wrapper(func)

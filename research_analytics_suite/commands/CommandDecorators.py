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
import inspect
from typing import get_type_hints

temp_command_registry = []


def register_commands(cls):
    """
    Decorator to register all commands in a class.

    This decorator auto-detects all command methods in a class and registers them.
    """
    class_name = cls.__name__
    for method_name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if hasattr(method, '_is_command'):
            sig = inspect.signature(method)
            type_hints = get_type_hints(method)
            args = [{'name': param, 'type': type_hints.get(param, str)} for param in sig.parameters if param not in
                    ('self', 'cls')]
            return_type = type_hints.get('return', None)

            # Check if the method is already registered to prevent duplicates
            if not any(cmd_meta['func'] == method for cmd_meta in temp_command_registry):
                temp_command_registry.append({
                    'func': method,
                    'name': method.__name__,
                    'class_name': class_name,
                    'args': args,
                    'return_type': return_type,
                    'is_method': True if 'self' in sig.parameters or 'cls' in sig.parameters else False
                })
            else:
                for cmd_meta in temp_command_registry:
                    if cmd_meta['func'] == method:
                        cmd_meta['name'] = method.__name__
                        cmd_meta['class_name'] = class_name
                        cmd_meta['is_method'] = True if 'self' in sig.parameters or 'cls' in sig.parameters else False
    return cls


def command(func=None):
    """
    Decorator to register a command.

    This decorator auto-detects the command name, argument names, types, and return type.
    """
    def wrapper(f):
        # Auto-detect arguments and return type
        sig = inspect.signature(f)
        try:
            type_hints = get_type_hints(f)
        except NameError as e:
            raise TypeError(f"Invalid type hint in function {f.__name__}: {e}")

        args = [{'name': param, 'type': type_hints.get(param, str)} for param in sig.parameters if
                param not in ('self', 'cls')]
        return_type = type_hints.get('return', None)

        # Determine if the function is a method or static method
        is_method = 'self' in sig.parameters or 'cls' in sig.parameters

        # Check if the function is already registered to prevent duplicates
        if not any(cmd_meta['func'] == f for cmd_meta in temp_command_registry):
            temp_command_registry.append({
                'func': f,
                'name': f.__name__,
                # Include the class name for methods, 2nd to last part of the qualname
                'class_name': f.__qualname__.split('.')[-2] if is_method else None,
                'args': args,
                'return_type': return_type,
                'is_method': is_method
            })

        f._is_command = True
        return f

    if func is None:
        return wrapper
    else:
        return wrapper(func)

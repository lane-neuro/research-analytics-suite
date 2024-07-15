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

temp_command_registry = []


def clean_description(description: str) -> str:
    """
    Cleans up the description string by removing extra whitespace and trimming unnecessary parts.

    Args:
        description (str): The original description string.

    Returns:
        str: The cleaned description.
    """
    description = ' '.join(description.split())  # Remove extra whitespace
    if 'Args' in description:
        description = description.split('Args')[0]
    if 'Returns' in description:
        description = description.split('Returns')[0]
    return description.strip()


def register_commands(cls):
    """
    Decorator to register all commands in a class.

    This decorator auto-detects all command methods in a class and registers them.
    """
    class_name = cls.__name__
    for method_name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if hasattr(method, '_is_command'):
            sig = inspect.signature(method)
            type_hints = method.__annotations__
            args = [{'name': param, 'type': type_hints.get(param, any)} for param in sig.parameters if param not in ('self', 'cls')]
            return_type = type_hints.get('return', None)
            if return_type:
                return_type = return_type if isinstance(return_type, list) else [return_type]

            description = method.__doc__ if method.__doc__ else None
            description = clean_description(description) if description else None

            # Check if the method is already registered to prevent duplicates
            if not any(cmd_meta['func'] == method for cmd_meta in temp_command_registry):
                temp_command_registry.append({
                    'func': method,
                    'name': method.__name__,
                    'description': description,
                    'class_name': class_name,
                    'class_obj': cls,
                    'args': args,
                    'return_type': return_type,
                    'is_method': 'self' in sig.parameters or 'cls' in sig.parameters,
                    'is_command': True
                })
            else:
                for cmd_meta in temp_command_registry:
                    if cmd_meta['func'] == method:
                        cmd_meta['name'] = method.__name__
                        cmd_meta['description'] = description
                        cmd_meta['class_name'] = class_name
                        cmd_meta['class_obj'] = cls
                        cmd_meta['args'] = args
                        cmd_meta['return_type'] = return_type
                        cmd_meta['is_method'] = 'self' in sig.parameters or 'cls' in sig.parameters,
                        cmd_meta['is_command'] = True
    return cls


def command(func=None):
    """
    Decorator to register a command.

    This decorator auto-detects the command name, argument names, types, and return type.
    """
    def wrapper(f):
        # Auto-detect arguments and return type
        sig = inspect.signature(f)
        type_hints = f.__annotations__

        args = [{'name': param, 'type': type_hints.get(param, any)} for param in sig.parameters if param not in ('self', 'cls')]
        return_type = type_hints.get('return', None)
        if return_type:
            return_type = return_type if isinstance(return_type, list) else [return_type]

        description = f.__doc__ if f.__doc__ else None
        description = clean_description(description) if description else None

        # Determine if the function is a method or static method
        is_method = 'self' in sig.parameters or 'cls' in sig.parameters

        # Check if the function is already registered to prevent duplicates
        if not any(cmd_meta['func'] == f for cmd_meta in temp_command_registry):
            temp_command_registry.append({
                'func': f,
                'name': f.__name__,
                'description': description,
                # Include the class name for methods, 2nd to last part of the qualname
                'class_name': f.__qualname__.split('.')[-2] if is_method and '.' in f.__qualname__ and f.__qualname__.count('.') > 1 else None,
                'class_obj': f.__qualname__,
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

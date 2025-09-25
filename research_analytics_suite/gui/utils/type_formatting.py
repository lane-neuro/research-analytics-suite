"""
Type Formatting Utilities

This module provides utilities for formatting type annotations in a user-friendly way for GUI display.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from typing import get_origin, get_args, Union, Optional, List, Dict, Tuple, Set, Any
import typing


def format_type_for_display(type_obj) -> str:
    """
    Format a type object for user-friendly display in the GUI.

    Args:
        type_obj: The type object to format (can be built-in type, Union, List, etc.)

    Returns:
        str: A user-friendly string representation of the type

    Examples:
        str -> "str"
        Union[int, str] -> "int | str"
        List[float] -> "List[float]"
        Optional[str] -> "str?"
        <class 'list'> -> "list"
    """
    if type_obj is None:
        return "None"

    # Handle built-in types
    if isinstance(type_obj, type):
        return type_obj.__name__

    # Handle typing module constructs
    origin = get_origin(type_obj)
    args = get_args(type_obj)

    if origin is Union:
        # Handle Union types (including Optional)
        if len(args) == 2 and type(None) in args:
            # This is Optional[T] which is Union[T, None]
            non_none_type = args[0] if args[1] is type(None) else args[1]
            return f"{format_type_for_display(non_none_type)}?"
        else:
            # Regular Union
            formatted_args = [format_type_for_display(arg) for arg in args]
            return " | ".join(formatted_args)

    elif origin in (list, List):
        # Handle List[T]
        if args:
            inner_type = format_type_for_display(args[0])
            return f"List[{inner_type}]"
        else:
            return "List"

    elif origin in (dict, Dict):
        # Handle Dict[K, V]
        if args and len(args) == 2:
            key_type = format_type_for_display(args[0])
            value_type = format_type_for_display(args[1])
            return f"Dict[{key_type}, {value_type}]"
        else:
            return "Dict"

    elif origin in (tuple, Tuple):
        # Handle Tuple[T, ...]
        if args:
            if len(args) == 2 and args[1] is ...:
                # Variable length tuple: Tuple[int, ...]
                inner_type = format_type_for_display(args[0])
                return f"Tuple[{inner_type}, ...]"
            else:
                # Fixed length tuple: Tuple[int, str, float]
                formatted_args = [format_type_for_display(arg) for arg in args]
                return f"Tuple[{', '.join(formatted_args)}]"
        else:
            return "Tuple"

    elif origin in (set, Set):
        # Handle Set[T]
        if args:
            inner_type = format_type_for_display(args[0])
            return f"Set[{inner_type}]"
        else:
            return "Set"

    elif origin is type(Any):
        return "Any"

    # Handle string representations (fallback)
    if isinstance(type_obj, str):
        return type_obj

    # Handle typing module types that have __name__
    if hasattr(type_obj, '__name__'):
        return type_obj.__name__

    # Handle typing module types with string representation
    if hasattr(type_obj, '__module__') and type_obj.__module__ == 'typing':
        type_str = str(type_obj)
        # Clean up typing module prefix
        if type_str.startswith('typing.'):
            return type_str[7:]  # Remove 'typing.' prefix
        return type_str

    # Fallback to string representation
    return str(type_obj)


def format_input_output_entry(name: str, type_obj, include_brackets: bool = True) -> str:
    """
    Format an input/output entry for display in listboxes.

    Args:
        name (str): The name of the input/output
        type_obj: The type object
        include_brackets (bool): Whether to include brackets around the type

    Returns:
        str: Formatted string like "name [type]" or "name - type"

    Examples:
        "categories", list -> "categories (list)"
        "bins", Union[int, str] -> "bins (int | str)"
    """
    formatted_type = format_type_for_display(type_obj)

    if include_brackets:
        return f"{name} ({formatted_type})"
    else:
        return f"{name} - {formatted_type}"


def format_memory_slot_type(type_obj) -> str:
    """
    Format a memory slot type for display in memory slot previews.

    Args:
        type_obj: The type object from the memory slot

    Returns:
        str: Formatted type string optimized for memory slot display
    """
    # For memory slots, we want concise but clear type representations
    formatted = format_type_for_display(type_obj)

    # Shorten some common long types for memory slot display
    replacements = {
        "List[float]": "List[float]",  # Keep as-is, it's already concise
        "List[int]": "List[int]",
        "Dict[str, Any]": "Dict[str, *]",  # Use * for Any in compact display
        "Optional": "?"  # Very compact optional notation
    }

    for long_form, short_form in replacements.items():
        if long_form in formatted:
            formatted = formatted.replace(long_form, short_form)

    return formatted
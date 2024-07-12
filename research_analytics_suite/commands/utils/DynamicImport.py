import importlib
import re
from typing import Any, Union, Type, Optional, List, Dict, ForwardRef, Tuple


def parse_typing_alias(alias: str, elements: str) -> Type[Any]:
    """
    Parses the elements inside a typing alias and returns the corresponding type.

    Args:
        alias: The alias like 'Optional', 'List', 'Dict', 'Union', 'Tuple'.
        elements: The elements inside the brackets.

    Returns:
        type: The corresponding type.
    """
    typing_aliases = {
        'Optional': Optional,
        'List': List,
        'Dict': Dict,
        'Union': Union,
        'Tuple': Tuple,
        'Any': Any,
    }

    if alias == 'Optional':
        return Optional[dynamic_import(elements)]
    elif alias == 'List':
        return List[dynamic_import(elements)]
    elif alias == 'Dict':
        # Split by commas, but only at the top level
        parts = re.split(r',\s*(?![^[]*\])', elements)
        if len(parts) != 2:
            raise ValueError(f"Invalid elements for Dict: {elements}")
        key, value = parts
        return Dict[dynamic_import(key.strip()), dynamic_import(value.strip() if isinstance(value, str) else value)]
    elif alias == 'Union':
        types = [dynamic_import(element.strip()) for element in re.split(r',\s*(?![^[]*\])', elements)]
        return Union[tuple(types)]
    elif alias == 'Tuple':
        types = [dynamic_import(element.strip()) for element in re.split(r',\s*(?![^[]*\])', elements)]
        return Tuple[tuple(types)]
    else:
        raise ValueError(f"Unknown typing alias: {alias}")


def dynamic_import(import_string: Union[str, Type[Any]]) -> Type[Any]:
    """
    Dynamically imports a class from a module.

    Args:
        import_string: The import string in the format 'module_path.class_name' or a type object.

    Returns:
        type: The class type.
    """
    if isinstance(import_string, type):
        return import_string

    if isinstance(import_string, ForwardRef):
        import_string = import_string.__forward_arg__

    if not isinstance(import_string, str):
        import_string = str(import_string)

    # Handle typing imports like Optional[str], List[int], etc.
    typing_aliases = {
        'Optional': Optional,
        'List': List,
        'Dict': Dict,
        'Union': Union,
        'Tuple': Tuple,
        'Any': Any,
    }

    # Check if the import string is a recognized type alias
    for alias, _ in typing_aliases.items():
        if import_string.startswith(f'{alias}['):
            inner_elements = import_string[len(alias) + 1:-1]
            return parse_typing_alias(alias, inner_elements)

    # Handle standard imports and built-in types
    try:
        if '.' in import_string:
            module_path, class_name = import_string.rsplit('.', 1)
            module = importlib.import_module(module_path)
            return getattr(module, class_name)
        else:
            # Check if the string corresponds to a built-in type
            built_in_types = {
                'int': int,
                'float': float,
                'str': str,
                'bool': bool,
                'list': list,
                'dict': dict,
                'set': set,
                'tuple': tuple
            }
            if import_string in built_in_types:
                return built_in_types[import_string]

            # Check globals for any other types
            if import_string in globals():
                return globals().get(import_string)

            raise ImportError(f"No module named '{import_string}'")

    except (AttributeError, ImportError, NameError, Exception) as e:
        return type(any)  # Fallback for any exception

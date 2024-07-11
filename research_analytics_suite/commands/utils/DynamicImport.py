import importlib
import typing
from typing import Any, Union, Type, ForwardRef


import importlib
from typing import Any, Union, Type, ForwardRef, Optional, List, Dict


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
    try:
        return eval(import_string, globals(), locals())
    except (NameError, SyntaxError):
        pass

    if '.' not in import_string:
        if import_string not in globals():
            return type(any)
        return globals().get(import_string)
    else:
        module_path, class_name = import_string.rsplit('.', 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
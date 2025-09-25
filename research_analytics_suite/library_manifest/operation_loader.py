"""
Dynamic Operation Library Loader

This module provides dynamic discovery and loading of operation classes from the operation_library
directory structure. It replaces the static import approach with runtime discovery, enabling
automatic registration of new operations without manual maintenance of import lists.

Author: Lane
"""

import os
import sys
import importlib
import inspect
from pathlib import Path
from typing import List, Type, Optional
from research_analytics_suite.utils import CustomLogger


def discover_operations() -> List[Type]:
    """
    Dynamically discover and load all operation classes from the operation library.

    This function searches for operation modules in both development and distribution scenarios:
    - Development: Looks in the source operation_library directory
    - Distribution: Looks in the bundled operation_library_src directory

    Returns:
        List[Type]: List of operation classes that inherit from BaseOperation
    """
    logger = CustomLogger()
    operations = []

    # Determine the search paths for operations
    search_paths = _get_operation_search_paths()

    for search_path in search_paths:
        logger.debug(f"Searching for operations in: {search_path}")

        if not search_path.exists():
            logger.debug(f"Path does not exist: {search_path}")
            continue

        # Discover operation modules
        operation_modules = _discover_operation_modules(search_path)

        # Load and validate operation classes
        for module_path in operation_modules:
            try:
                operation_class = _load_operation_from_file(module_path, search_path)
                if operation_class:
                    operations.append(operation_class)
                    logger.debug(f"Loaded operation: {operation_class.__name__}")
            except Exception as e:
                logger.error(f"Failed to load operation from {module_path}: {e}")

    logger.debug(f"Discovered {len(operations)} operation classes")
    return operations


def _get_operation_search_paths() -> List[Path]:
    """
    Get the list of paths to search for operation modules.

    Returns:
        List[Path]: List of paths to search for operations
    """
    paths = []

    # Development path - source operation_library
    try:
        import research_analytics_suite.operation_library
        source_path = Path(research_analytics_suite.operation_library.__file__).parent
        paths.append(source_path)
    except ImportError:
        pass

    # Distribution path - bundled operation_library_src
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller bundled app
        bundled_path = Path(sys._MEIPASS) / "operation_library_src"
        paths.append(bundled_path)
    else:
        # Look for operation_library_src in common locations
        possible_bundled_paths = [
            Path.cwd() / "operation_library_src",
            Path(__file__).parent.parent / "operation_library_src"
        ]
        for path in possible_bundled_paths:
            if path.exists():
                paths.append(path)

    return paths


def _discover_operation_modules(search_path: Path) -> List[Path]:
    """
    Discover Python module files in the given path that could contain operations.

    Args:
        search_path (Path): Path to search for Python modules

    Returns:
        List[Path]: List of Python module file paths
    """
    operation_modules = []

    for file_path in search_path.iterdir():
        if (file_path.is_file() and
            file_path.suffix == '.py' and
            not file_path.name.startswith('__') and
            file_path.name not in ['loader.py']):
            operation_modules.append(file_path)

    return operation_modules


def _load_operation_from_file(module_path: Path, search_path: Path) -> Optional[Type]:
    """
    Load an operation class from a Python file.

    Args:
        module_path (Path): Path to the Python module file
        search_path (Path): Base search path for module resolution

    Returns:
        Optional[Type]: Operation class if found and valid, None otherwise
    """
    logger = CustomLogger()

    try:
        # Create module name from file path
        module_name = module_path.stem

        # For bundled/source files, load directly from file
        if not str(search_path).endswith('operation_library'):
            return _load_module_from_source_file(module_path)

        # For development, use importlib with proper package structure
        full_module_name = f"research_analytics_suite.operation_library.{module_name}"

        try:
            # Try to import from the package first
            module = importlib.import_module(full_module_name)
        except ImportError:
            # Fallback to loading from source file
            return _load_module_from_source_file(module_path)

        # Find operation class in the module
        return _find_operation_class_in_module(module)

    except Exception as e:
        logger.error(f"Error loading operation from {module_path}: {e}")
        return None


def _load_module_from_source_file(module_path: Path) -> Optional[Type]:
    """
    Load a module directly from a source file and extract the operation class.

    Args:
        module_path (Path): Path to the Python source file

    Returns:
        Optional[Type]: Operation class if found and valid, None otherwise
    """
    logger = CustomLogger()

    try:
        # Create a unique module name to avoid conflicts
        module_name = f"dynamic_operation_{module_path.stem}"

        # Load module from file
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)

        # Add to sys.modules to support relative imports
        sys.modules[module_name] = module

        try:
            spec.loader.exec_module(module)
        except Exception as e:
            # Clean up on failure
            sys.modules.pop(module_name, None)
            raise e

        # Find operation class in the loaded module
        return _find_operation_class_in_module(module)

    except Exception as e:
        logger.error(f"Error loading module from source file {module_path}: {e}")
        return None


def _find_operation_class_in_module(module) -> Optional[Type]:
    """
    Find and validate an operation class within a loaded module.

    Args:
        module: The loaded Python module

    Returns:
        Optional[Type]: Operation class if found and valid, None otherwise
    """
    # Import BaseOperation here to avoid circular imports
    try:
        from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation
    except ImportError:
        from research_analytics_suite.operation_manager import BaseOperation

    # Look for classes that inherit from BaseOperation
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if (obj != BaseOperation and
            issubclass(obj, BaseOperation) and
            obj.__module__ == module.__name__):

            # Additional validation - ensure it has required attributes
            if _validate_operation_class(obj):
                return obj

    return None


def _validate_operation_class(operation_class: Type) -> bool:
    """
    Validate that an operation class meets the minimum requirements.

    Args:
        operation_class (Type): The operation class to validate

    Returns:
        bool: True if valid, False otherwise
    """
    # Check for required class attributes
    required_attrs = ['name', 'execute']

    for attr in required_attrs:
        if not hasattr(operation_class, attr):
            return False

    # Check that execute is callable
    if not callable(getattr(operation_class, 'execute', None)):
        return False

    return True
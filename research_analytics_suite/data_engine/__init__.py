"""
data_engine package

Universal data processing engine that handles ANY data type of ANY size with optimal
performance through intelligent adapter selection and execution optimization.

The Universal Data Engine provides a single, intelligent solution that automatically
optimizes for any data processing task with zero configuration required.
"""

# Universal Data Engine
from .UniversalDataEngine import UniversalDataEngine, quick_load, quick_save, quick_analyze
from .core.DataProfile import DataProfile
from .adapters import AdapterRegistry, BaseAdapter
from .execution import ExecutionEngine, ExecutionBackend
from .storage import StorageLayer, StorageBackend

# Workspace
from .Workspace import Workspace

# Essential memory management
from .memory import MemoryManager

# Main exports
__all__ = [
    # Universal Data System
    'UniversalDataEngine',
    'DataProfile',
    'AdapterRegistry',
    'BaseAdapter',
    'ExecutionEngine',
    'ExecutionBackend',
    'StorageLayer',
    'StorageBackend',
    'quick_load',
    'quick_save',
    'quick_analyze',

    # Workspace
    'Workspace',

    # Memory Management
    'MemoryManager'
]

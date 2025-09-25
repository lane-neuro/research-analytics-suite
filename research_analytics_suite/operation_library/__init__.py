"""
Operation Library Package

This package provides a dynamically loaded library of operations for the Research Analytics Suite.
Operations are discovered and loaded automatically at runtime, eliminating the need for manual
import maintenance.

Author: Lane
"""

# Backward compatibility: provide OPERATIONS list using dynamic discovery
def _get_operations_list():
    """
    Get the list of operation classes using dynamic discovery.
    This maintains backward compatibility for any code that still expects
    the OPERATIONS list.
    """
    try:
        return discover_operations()
    except Exception:
        # Fallback to empty list if dynamic loading fails
        return []


# Lazy-loaded OPERATIONS list for backward compatibility
class _OperationsList:
    """
    Lazy-loaded operations list that uses dynamic discovery when accessed.
    """
    def __init__(self):
        self._operations = None

    def __iter__(self):
        if self._operations is None:
            self._operations = _get_operations_list()
        return iter(self._operations)

    def __len__(self):
        if self._operations is None:
            self._operations = _get_operations_list()
        return len(self._operations)

    def __getitem__(self, index):
        if self._operations is None:
            self._operations = _get_operations_list()
        return self._operations[index]


# Provide OPERATIONS for backward compatibility
OPERATIONS = _OperationsList()

# Export the dynamic loader for direct use
from research_analytics_suite.library_manifest.operation_loader import discover_operations

__all__ = ['OPERATIONS', 'discover_operations']

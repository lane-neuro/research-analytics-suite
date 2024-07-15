"""
SingletonChecker Module

This module provides a function to check if a class is a singleton.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""


def is_singleton(cls):
    """
    Check if a class is a singleton by inspecting its class attribute.

    Args:
        cls: The class to check.

    Returns:
        bool: True if the class is a singleton, False otherwise.
    """
    # Check if the class has the '_instance' attribute
    if hasattr(cls, '_instance'):
        instance = getattr(cls, '_instance')
        # Ensure the '_instance' attribute is an instance of the class
        if instance is not None and isinstance(instance, type(cls)):
            return True
    return False


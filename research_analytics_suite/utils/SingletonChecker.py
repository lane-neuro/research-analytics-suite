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
    Check if a class is a singleton by inspecting its metaclass.

    Args:
        cls: The class to check.

    Returns:
        bool: True if the class is a singleton, False otherwise.
    """
    if not hasattr(cls, '__class__'):
        return False

    meta = cls.__class__

    if not hasattr(meta, '_instances'):
        return False

    if not isinstance(meta._instances, dict):
        return False

    return cls in meta._instances

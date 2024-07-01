"""
Utility functions for the operation library.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import importlib


def check_verified(identifier):
    try:
        importlib.import_module(f'operation_library.{identifier}')
        return True
    except ImportError:
        return False

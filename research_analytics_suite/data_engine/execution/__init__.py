"""
Execution Package

Adaptive execution engine for optimal backend selection and processing.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Development
"""

from .ExecutionEngine import ExecutionEngine, ExecutionBackend, ExecutionContext, ExecutionResult

__all__ = [
    'ExecutionEngine',
    'ExecutionBackend',
    'ExecutionContext',
    'ExecutionResult'
]
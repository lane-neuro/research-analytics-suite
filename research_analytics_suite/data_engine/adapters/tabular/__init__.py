"""
Tabular Adapters Package

High-performance adapters for tabular data processing using existing dependencies.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Development
"""

# Import adapters using existing dependencies only
try:
    from .PandasAdapter import PandasAdapter
except ImportError:
    PandasAdapter = None

try:
    from .DaskAdapter import DaskAdapter
except ImportError:
    DaskAdapter = None

__all__ = []

if PandasAdapter:
    __all__.append('PandasAdapter')

if DaskAdapter:
    __all__.append('DaskAdapter')
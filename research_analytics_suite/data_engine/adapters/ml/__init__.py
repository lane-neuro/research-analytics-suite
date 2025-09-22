"""
ML Adapters Package

Machine learning data adapters using existing dependencies.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Development
"""

try:
    from .TorchAdapter import TorchAdapter
except ImportError:
    TorchAdapter = None

try:
    from .NumpyAdapter import NumpyAdapter
except ImportError:
    NumpyAdapter = None

__all__ = []

if TorchAdapter:
    __all__.append('TorchAdapter')

if NumpyAdapter:
    __all__.append('NumpyAdapter')
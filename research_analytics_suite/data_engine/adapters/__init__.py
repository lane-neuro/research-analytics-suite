"""
Adapters Package

Universal data adapters for handling any data type with optimal performance.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Development
"""

from .BaseAdapter import BaseAdapter, StreamingAdapter, MLAdapter
from .AdapterRegistry import AdapterRegistry

# Import adapters from subpackages
from .tabular import *
from .ml import *

__all__ = [
    'BaseAdapter',
    'StreamingAdapter',
    'MLAdapter',
    'AdapterRegistry'
]
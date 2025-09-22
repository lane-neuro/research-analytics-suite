"""
Storage Package

Universal storage abstraction layer for accessing any storage system.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Development
"""

from .StorageBackend import (
    StorageBackend,
    LocalFileSystem,
    InMemoryStorage,
    TemporaryStorage,
    CloudStorageBase
)
from .StorageLayer import StorageLayer

__all__ = [
    'StorageBackend',
    'LocalFileSystem',
    'InMemoryStorage',
    'TemporaryStorage',
    'CloudStorageBase',
    'StorageLayer'
]
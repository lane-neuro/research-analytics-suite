"""
LazyModuleLoader

This module provides a class that allows for lazy loading of modules in Python. This can be useful for managing the
import of large modules that may not be needed in every execution of a script.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""


class LazyModuleLoader:
    def __init__(self):
        self._modules = {
            'math': None,
            'numpy': None,
            'pandas': None,
            'sklearn': None,
            'torch': None,
        }

    def __getattr__(self, name):
        return self.get_module(name)

    def get_module(self, name):
        if name in self._modules:
            if self._modules[name] is None:
                self._modules[name] = __import__(name)
            return self._modules[name]
        raise AttributeError(f"Module '{name}' not found")

    def get_all_modules(self):
        for name in self._modules:
            self.get_module(name)
        return self._modules

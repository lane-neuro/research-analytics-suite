"""



Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

import asyncio
from abc import ABC, abstractmethod
from concurrent.futures import ProcessPoolExecutor
from typing import Tuple

from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler


class BaseOperation(ABC):
    """
    An abstract base class that defines a common interface for all operations.

    This class requires that any child class implement the execute, start, pause, stop, and resume methods.
    """

    @abstractmethod
    def __init__(self, name: str = "BaseOperation"):
        self.name = name
        self._status = "idle"

    @abstractmethod
    def progress(self) -> Tuple[int, str]:
        pass

    @abstractmethod
    async def update_progress(self):
        pass

    @abstractmethod
    async def execute(self):
        pass

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def stop(self):
        pass

    @abstractmethod
    async def pause(self):
        pass

    @abstractmethod
    async def resume(self):
        pass

    @abstractmethod
    async def reset(self):
        pass

    @abstractmethod
    def get_progress(self):
        pass

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @status.getter
    def status(self):
        return self._status

"""
This module defines the abstract base class BaseOperation, which provides a common interface for all operations in the
NeuroBehavioral Analytics Suite. The BaseOperation class requires any child class to implement the execute, start, pause,
stop, and resume methods. It also provides a property for the status of the operation, which can be "idle", "started",
"paused", "running", or "stopped". This class is designed to be inherited by other classes that represent specific
operations.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

from abc import ABC, abstractmethod
from typing import Tuple


class BaseOperation(ABC):
    """
    An abstract base class that defines a common interface for all operations.

    This class requires that any child class implement the execute, start, pause, stop, and resume methods.
    """

    @abstractmethod
    def __init__(self):
        """
        Initialize the operation with status "idle".
        """
        pass

    @abstractmethod
    async def start(self):
        """
        Abstract method to start the operation.
        Must be implemented by any child class.
        """
        pass

    @abstractmethod
    async def resume(self):
        """
        Abstract method to resume the operation.
        Must be implemented by any child class.
        """
        pass

    @abstractmethod
    async def pause(self):
        """
        Abstract method to pause the operation.
        Must be implemented by any child class.
        """
        pass

    @abstractmethod
    async def stop(self):
        """
        Abstract method to stop the operation.
        Must be implemented by any child class.
        """
        pass

    @abstractmethod
    async def reset(self):
        """
        Abstract method to reset the operation.
        Must be implemented by any child class.
        """
        pass

    @abstractmethod
    def progress(self) -> Tuple[int, str]:
        """
        Abstract method to get the progress of the operation.
        Must be implemented by any child class.
        """
        pass

    @abstractmethod
    async def execute(self):
        """
        Abstract method to execute the operation.
        Must be implemented by any child class.
        """
        pass

    @abstractmethod
    def get_progress(self):
        """
        Abstract method to get the progress of the operation.
        Must be implemented by any child class.
        """
        pass

    @abstractmethod
    async def update_progress(self):
        """
        Abstract method to update the progress of the operation.
        Must be implemented by any child class.
        """
        pass

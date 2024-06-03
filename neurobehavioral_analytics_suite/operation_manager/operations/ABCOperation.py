"""
This module defines the abstract base class ABCOperation, which provides a common interface for all operations in the
NeuroBehavioral Analytics Suite. The ABCOperation class requires any child class to implement execute, start, pause,
stop, and resume methods. It also provides a property for the status of the operation, which can be "idle", "started",
"paused", "running", or "stopped". This class is designed to be inherited by other classes that represent specific
operation.

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


class ABCOperation(ABC):
    """
    An abstract base class that defines a common interface for all operations.
    """

    @abstractmethod
    def __init__(self):
        """
        Initialize the operation instance.
        """
        pass

    @abstractmethod
    def init_operation(self):
        """
        Initialize any resources or setup required for the operation before it starts.
        """
        pass

    @abstractmethod
    async def start(self):
        """
        Start the operation.
        """
        pass

    @abstractmethod
    async def execute(self):
        """
        Execute the operation.
        """
        pass

    @abstractmethod
    def get_result(self):
        """
        Retrieve the result of the operation, if applicable.
        """
        pass

    @abstractmethod
    async def pause(self):
        """
        Pause the operation.
        """
        pass

    @abstractmethod
    async def resume(self):
        """
        Resume the operation.
        """
        pass

    @abstractmethod
    async def stop(self):
        """
        Stop the operations.
        """
        pass

    @abstractmethod
    async def reset(self):
        """
        Reset the operations.
        """
        pass

    @abstractmethod
    async def restart(self):
        """
        Restart the operations from the beginning.
        """
        pass

    @abstractmethod
    def is_running(self):
        """
        Check if the operations is currently running.
        """
        pass

    def is_complete(self):
        """
        Check if the operations is complete.
        """
        pass

    @abstractmethod
    def is_paused(self):
        """
        Check if the operations is currently paused.
        """
        pass

    @abstractmethod
    def is_stopped(self):
        """
        Check if the operations is currently stopped.
        """
        pass

    @abstractmethod
    def progress(self) -> Tuple[int, str]:
        """
        Get the progress of the operations.
        """
        pass

    @abstractmethod
    async def update_progress(self):
        """
        Update the progress of the operations.
        """
        pass

    @abstractmethod
    def cleanup_operation(self):
        """
        Clean up any resources or perform any necessary teardown after the operations has completed or been stopped.
        """
        pass

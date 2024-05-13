"""
A module that defines the BaseOperation class, which is an abstract base class (ABC).

The BaseOperation class defines a common interface for all operations with an abstract execute method. Any class that
inherits from BaseOperation must implement the execute method.

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
from typing import Any


class BaseOperation(ABC):
    """
    An abstract base class that defines a common interface for all operations.

    This class requires that any child class implement the execute, start, pause, stop, and resume methods.
    """

    def __init__(self) -> None:
        self.task = None
        self.status = "idle"
        self.name = "BaseOperation"

    @abstractmethod
    async def execute(self) -> Any:
        """
        An abstract method that will execute the operation.

        This method should be implemented by any concrete class that inherits from this base class.
        """
        pass

    @abstractmethod
    async def start(self) -> None:
        """
        An abstract method that will start the operation.

        This method should be implemented by any concrete class that inherits from this base class.
        """
        pass

    @abstractmethod
    async def pause(self) -> None:
        """
        An abstract method that will pause the operation.

        This method should be implemented by any concrete class that inherits from this base class.
        """
        pass

    @abstractmethod
    async def stop(self) -> None:
        """
        An abstract method that will stop the operation.

        This method should be implemented by any concrete class that inherits from this base class.
        """
        pass

    @abstractmethod
    async def resume(self) -> None:
        """
        An abstract method that will resume the operation.

        This method should be implemented by any concrete class that inherits from this base class.
        """
        pass

    @abstractmethod
    async def reset(self) -> None:
        """
        An abstract method that will reset the operation.

        This method should be implemented by any concrete class that inherits from this base class.
        """
        pass

    @abstractmethod
    def progress(self) -> int:
        """
        An abstract method that will return the current progress of the operation.

        This method should be implemented by any concrete class that inherits from this base class.

        Returns:
            int: The current progress of the operation.
        """
        pass

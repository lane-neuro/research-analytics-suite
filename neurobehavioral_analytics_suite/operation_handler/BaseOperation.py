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


class BaseOperation(ABC):
    """
    An abstract base class that defines a common interface for all operations.

    This class requires that any child class implement the execute, start, pause, stop, and resume methods.
    """

    @abstractmethod
    async def execute(self):
        """
        An abstract method that will execute the operation.

        This method should be implemented by any concrete class that inherits from this base class.
        """
        pass

    @abstractmethod
    async def start(self):
        """
        An abstract method that will start the operation.

        This method should be implemented by any concrete class that inherits from this base class.
        """
        pass

    @abstractmethod
    async def pause(self):
        """
        An abstract method that will pause the operation.

        This method should be implemented by any concrete class that inherits from this base class.
        """
        pass

    @abstractmethod
    async def stop(self):
        """
        An abstract method that will stop the operation.

        This method should be implemented by any concrete class that inherits from this base class.
        """
        pass

    @abstractmethod
    async def resume(self):
        """
        An abstract method that will resume the operation.

        This method should be implemented by any concrete class that inherits from this base class.
        """
        pass

    @abstractmethod
    async def reset(self):
        """
        An abstract method that will reset the operation.

        This method should be implemented by any concrete class that inherits from this base class.
        """
        pass

    @abstractmethod
    def status(self):
        """
        An abstract method that will return the current status of the operation.

        This method should be implemented by any concrete class that inherits from this base class.
        """
        pass

    @abstractmethod
    def progress(self):
        """
        An abstract method that will return the current progress of the operation.

        This method should be implemented by any concrete class that inherits from this base class.
        """
        pass

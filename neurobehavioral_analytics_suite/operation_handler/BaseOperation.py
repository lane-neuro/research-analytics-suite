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

    This class requires that any child class implement the execute method.

    Methods:
        execute: An abstract method that will execute the operation.
    """

    @abstractmethod
    def execute(self):
        """
        An abstract method that will execute the operation.

        This method should be implemented by any concrete class that inherits from this base class.
        """
        pass

    async def start(self):
        """
        Starts the operation.
        """

        await self.execute()

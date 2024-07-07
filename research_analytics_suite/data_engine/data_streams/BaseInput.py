"""
BaseInput Module

This module defines the BaseInput class, which serves as a base class for handling live data inputs in the
Research Analytics Suite. It provides a common interface for different types of live data inputs.

Author: Lane
"""


class BaseInput:
    """
    A base class for handling live data inputs.

    Methods:
        start(): Starts the live data input.
        stop(): Stops the live data input.
        read(): Reads data from the live input.
    """
    def __init__(self, source):
        """Initializes the BaseInput object."""
        self._source = source

    def start(self):   # pragma: no cover
        """Starts the live data input."""
        raise NotImplementedError("Subclasses should implement this method")

    def stop(self):   # pragma: no cover
        """Stops the live data input."""
        raise NotImplementedError("Subclasses should implement this method")

    def read(self):  # pragma: no cover
        """Reads data from the live input."""
        raise NotImplementedError("Subclasses should implement this method")

    @property
    def source(self):
        """The source of the live data input."""
        return self._source

    @source.setter
    def source(self, value):
        self._source = value

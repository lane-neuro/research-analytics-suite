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
    def start(self):
        """Starts the live data input."""
        raise NotImplementedError("Subclasses should implement this method")

    def stop(self):
        """Stops the live data input."""
        raise NotImplementedError("Subclasses should implement this method")

    def read(self):
        """Reads data from the live input."""
        raise NotImplementedError("Subclasses should implement this method")

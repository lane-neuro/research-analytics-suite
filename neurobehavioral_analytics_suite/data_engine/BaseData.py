"""
base_data.py

Defines the BaseData class for handling single data points.

Classes:
    BaseData - A simple class for handling single data points.
"""


class BaseData:
    """
    A class to represent a single data point.

    Attributes:
        data: The data point.
    """
    def __init__(self, data):
        """
        Initializes the BaseData instance.

        Args:
            data: The data point.
        """
        self.data = data

    def get_data(self):
        """
        Retrieves the data point.

        Returns:
            The data point.
        """
        return self.data

    def set_data(self, new_data):
        """
        Sets the data point.

        Args:
            new_data: The new data point.
        """
        self.data = new_data

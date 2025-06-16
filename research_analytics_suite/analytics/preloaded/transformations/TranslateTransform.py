"""
Module for applying translation transformation in the Research Analytics Suite.

This module defines the TranslateTransform class which is designed to apply a translation transformation
to a given datapoint. It includes methods for initializing the transformation and applying it to a datapoint.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""


class TranslateTransform:
    """
    A class to apply a translation transformation to a given datapoint.

    This class is responsible for applying a translation transformation to a datapoint. The translation deltas
    can be specified during initialization.

    Attributes:
        delta_x (float): The x-coordinate of the translation delta.
        delta_y (float): The y-coordinate of the translation delta.
    """

    def __init__(self, delta_x, delta_y):
        """
        Initializes the TranslateTransform object with the provided translation deltas.

        Args:
            delta_x (float): The x-coordinate of the translation delta.
            delta_y (float): The y-coordinate of the translation delta.
        """

        self.delta_x = delta_x
        self.delta_y = delta_y

    def __repr__(self):
        """
        Returns a string representation of the TranslateTransform object.

        The string representation includes the translation deltas.

        Returns:
            str: A string representation of the TranslateTransform object.
        """

        return f"TranslateTransform, x,y = ({self.delta_x}, {self.delta_y})"

    def transform(self, datapoint):
        """
        Applies the translation transformation to the given datapoint.

        This method adds the translation deltas to the x and y coordinates of the datapoint.

        Args:
            datapoint: The datapoint to apply the translation transformation to.

        Returns:
            The transformed datapoint.
        """

        datapoint.x += self.delta_x
        datapoint.y += self.delta_y
        return datapoint

"""
Module for applying perspective transformation in the Research Analytics Suite.

This module defines the PerspectiveTransform class which is designed to apply a perspective transformation
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


class PerspectiveTransform:
    """
    A class to apply a perspective transformation to a given datapoint.

    This class is responsible for applying a perspective transformation to a datapoint. The perspective coefficient
    can be specified during initialization.

    Attributes:
        perspective_coeff (float): The coefficient of the perspective transformation.
    """

    def __init__(self, perspective_coeff=0.0001):
        """
        Initializes the PerspectiveTransform object with the provided perspective coefficient.

        Args:
            perspective_coeff (float): The coefficient of the perspective transformation.
        """

        self.perspective_coeff = perspective_coeff

    def __repr__(self):
        """
        Returns a string representation of the PerspectiveTransform object.

        The string representation includes the perspective coefficient.

        Returns:
            str: A string representation of the PerspectiveTransform object.
        """

        return f"PerspectiveTransform, perspective_coeff = {self.perspective_coeff}"

    def transform(self, datapoint):
        """
        Applies the perspective transformation to the given datapoint.

        This method scales the x and y coordinates of the datapoint based on the perspective coefficient and the y
        coordinate of the datapoint.

        Args:
            datapoint: The datapoint to apply the perspective transformation to.

        Returns:
            The transformed datapoint.
        """

        scale = 1.0 + self.perspective_coeff * datapoint.y
        datapoint.x *= scale
        datapoint.y *= scale
        return datapoint

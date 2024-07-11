"""
Module for applying rotation transformation in the Research Analytics Suite.

This module defines the RotateTransform class which is designed to apply a rotation transformation
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

import math

from research_analytics_suite.commands import register_commands, command


@register_commands
class RotateTransform:
    """
    A class to apply a rotation transformation to a given datapoint.

    This class is responsible for applying a rotation transformation to a datapoint. The rotation angle
    can be specified during initialization.

    Attributes:
        theta (float): The angle of the rotation transformation in radians.
    """

    def __init__(self, theta):
        """
        Initializes the RotateTransform object with the provided rotation angle.

        Args:
            theta (float): The angle of the rotation transformation in radians.
        """

        self.theta = theta

    def __repr__(self):
        """
        Returns a string representation of the RotateTransform object.

        The string representation includes the rotation angle.

        Returns:
            str: A string representation of the RotateTransform object.
        """

        return f"RotateTransform, theta = {self.theta}"

    @command
    def transform(self, datapoint):
        """
        Applies the rotation transformation to the given datapoint.

        This method rotates the x and y coordinates of the datapoint based on the rotation angle.

        Args:
            datapoint: The datapoint to apply the rotation transformation to.

        Returns:
            The transformed datapoint.
        """

        original_x = datapoint.x
        datapoint.x = original_x * math.cos(self.theta) - datapoint.y * math.sin(self.theta)
        datapoint.y = original_x * math.sin(self.theta) + datapoint.y * math.cos(self.theta)
        return datapoint

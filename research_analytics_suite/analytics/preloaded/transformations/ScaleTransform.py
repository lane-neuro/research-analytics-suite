"""
Module for applying scale transformation in the Research Analytics Suite.

This module defines the ScaleTransform class which is designed to apply a scale transformation
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
from research_analytics_suite.commands import register_commands, command


@register_commands
class ScaleTransform:
    """
    A class to apply a scale transformation to a given datapoint.

    This class is responsible for applying a scale transformation to a datapoint. The scale factor
    can be specified during initialization.

    Attributes:
        scale (float): The factor of the scale transformation.
    """

    def __init__(self, scale):
        """
        Initializes the ScaleTransform object with the provided scale factor.

        Args:
            scale (float): The factor of the scale transformation.
        """

        self.scale = scale

    def __repr__(self):
        """
        Returns a string representation of the ScaleTransform object.

        The string representation includes the scale factor.

        Returns:
            str: A string representation of the ScaleTransform object.
        """

        return f"ScaleTransform, scalar = {self.scale}"

    @command
    def transform(self, datapoint):
        """
        Applies the scale transformation to the given datapoint.

        This method scales the x and y coordinates of the datapoint based on the scale factor.

        Args:
            datapoint: The datapoint to apply the scale transformation to.

        Returns:
            The transformed datapoint.
        """

        datapoint.x *= self.scale
        datapoint.y *= self.scale
        return datapoint

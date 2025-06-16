"""
Module for applying jitter transformation in the Research Analytics Suite.

This module defines the JitterTransform class which is designed to apply a jitter transformation to a given datapoint.
It includes methods for initializing the transformation and applying it to a datapoint.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

import numpy as np


class JitterTransform:
    """
    A class to apply a jitter transformation to a given datapoint.

    This class is responsible for applying a jitter transformation to a datapoint. The jitter strength can be
    specified during initialization.

    Attributes:
        jitter_strength (float): The strength of the jitter transformation.
    """

    def __init__(self, jitter_strength=0.1):
        """
        Initializes the JitterTransform object with the provided jitter strength.

        Args:
            jitter_strength (float): The strength of the jitter transformation.
        """

        self.jitter_strength = jitter_strength

    def __repr__(self):
        """
        Returns a string representation of the JitterTransform object.

        The string representation includes the jitter strength.

        Returns:
            str: A string representation of the JitterTransform object.
        """

        return f"JitterTransform, jitter_strength = {self.jitter_strength}"

    def transform(self, datapoint):
        """
        Applies the jitter transformation to the given datapoint.

        This method adds a random value between -jitter_strength and jitter_strength to the x and y coordinates of the
        datapoint.

        Args:
            datapoint: The datapoint to apply the jitter transformation to.

        Returns:
            The transformed datapoint.
        """

        datapoint.x += np.random.uniform(-self.jitter_strength, self.jitter_strength)
        datapoint.y += np.random.uniform(-self.jitter_strength, self.jitter_strength)
        return datapoint

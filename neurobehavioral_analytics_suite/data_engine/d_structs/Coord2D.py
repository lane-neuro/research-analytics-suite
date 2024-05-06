"""
Module for handling 2D coordinates in the NeuroBehavioral Analytics Suite.

This module defines the Coord2D class which is designed to handle 2D coordinates. It includes methods for initializing
the coordinates, returning a formatted string representation, and applying transformations.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

from copy import deepcopy
from neurobehavioral_analytics_suite.data_engine import DataEngine


class Coord2D:
    """
    A class to handle 2D coordinates.

    This class is responsible for handling 2D coordinates. It includes methods for initializing the coordinates,
    returning a formatted string representation, and applying transformations.

    Attributes:
        x (float): The x-coordinate.
        y (float): The y-coordinate.
        likelihood (float): The likelihood of the coordinate.
    """

    def __init__(self, x_in: float, y_in: float, likelihood_in: float = None):
        """
        Initializes the Coord2D object with the provided coordinates and likelihood.

        Args:
            x_in (float): The x-coordinate.
            y_in (float): The y-coordinate.
            likelihood_in (float): The likelihood of the coordinate.
        """

        self.x = float(x_in)
        self.y = float(y_in)
        self.likelihood = float(likelihood_in) if likelihood_in else None

    def formatted_str(self):
        """
        Returns a formatted string representation of the Coord2D object.

        The string representation includes the coordinates and likelihood.

        Returns:
            str: A formatted string representation of the Coord2D object.
        """

        if self.likelihood is not None:
            return f"{self.x}_{self.y}_{self.likelihood}"
        else:
            return f"{self.x}_{self.y}"

    def __repr__(self):
        """
        Returns a string representation of the Coord2D object.

        The string representation includes the coordinates and likelihood.

        Returns:
            str: A string representation of the Coord2D object.
        """

        if self.likelihood is not None:
            return f"{self.x}_{self.y}_{self.likelihood}"
        else:
            return f"{self.x}_{self.y}"

    def transform(self, engine: DataEngine):
        """
        Applies the transformation to the Coord2D object.

        This method applies the transformation to the coordinates.

        Args:
            engine (DataEngine): The engine to apply the transformation.

        Returns:
            The transformed Coord2D object.
        """

        new_datapoint = deepcopy(self)  # Create a new data point object
        return engine.transform(new_datapoint)
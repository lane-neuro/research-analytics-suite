"""
SingleFrame.py

This module defines the SingleFrame class which encapsulates all func related to a single frame in a neurobehavioral
analytics project. It includes methods for initializing the frame, transforming it using a DataEngine object, and
providing a string representation of the frame.

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
from neurobehavioral_analytics_suite.data_engine.d_structs.Coord2D import Coord2D


class SingleFrame(object):
    """
    A class to hold all func related to a single frame.

    Args:
        use_likelihood (bool): A flag to determine whether to use likelihood or not.
        *data_in (list): A list of func related to a single frame.

    Attributes:
        frame_num (int): The frame number.
        coords (list): A list of Coord2D objects representing coordinates in the frame.
    """

    def __init__(self, use_likelihood, *data_in):
        """
        Initializes the SingleFrame object with the provided parameters.

        Args:
            use_likelihood (bool): A flag to determine whether to use likelihood or not.
            *data_in (list): A list of func related to a single frame.
        """

        self.use_likelihood = use_likelihood
        row = []
        for jj in data_in:
            row.extend(jj)
        self.frame_num = row[0]
        self.coords = []
        step = 3
        for ii in range(1, len(row), step):
            if self.use_likelihood:
                self.coords.extend([Coord2D(row[ii], row[ii + 1], row[ii + 2])])
            else:
                self.coords.extend([Coord2D(row[ii], row[ii + 1])])

    def __repr__(self):
        """
        Returns a string representation of the SingleFrame object.

        Returns:
            str: A string representation of the SingleFrame object.
        """

        frame_out = ""

        for coord in self.coords:
            frame_out = f"{frame_out},{repr(coord)}"
        return f"{frame_out}"

    def transform(self, engine: DataEngine):
        """
        Transforms the SingleFrame object using the provided DataEngine object.

        Args:
            engine (DataEngine): The DataEngine object to use for the transformation.

        Returns:
            SingleFrame: A new SingleFrame object that has been transformed.
        """

        new_frame = deepcopy(self)  # Create a new frame object
        for coord in new_frame.coords:
            coord.transform(engine)
        return new_frame

    def get_coord(self, index):
        """
        Returns a specific coordinate based on its index.

        Args:
            index (int): The index of the coordinate.

        Returns:
            Coord2D: The coordinate at the given index.
        """
        return self.coords[index]

    def add_coord(self, coord):
        """
        Adds a new coordinate to the coords list.

        Args:
            coord (Coord2D): The coordinate to add.

        Returns:
            None
        """
        self.coords.append(coord)

    def remove_coord(self, index):
        """
        Removes a specific coordinate based on its index.

        Args:
            index (int): The index of the coordinate to remove.

        Returns:
            None
        """
        self.coords.pop(index)

    def update_coord(self, index, coord):
        """
        Updates a specific coordinate based on its index.

        Args:
            index (int): The index of the coordinate to update.
            coord (Coord2D): The new coordinate.

        Returns:
            None
        """
        self.coords[index] = coord

    def get_average_coord(self):
        """
        Calculates and returns the average coordinate position across all coordinates in the frame.

        Returns:
            tuple: The average x and y position.
        """
        avg_x = sum(coord.x for coord in self.coords) / len(self.coords)
        avg_y = sum(coord.y for coord in self.coords) / len(self.coords)
        return avg_x, avg_y

    def get_max_coord(self):
        """
        Finds and returns the maximum coordinate position across all coordinates in the frame.

        Returns:
            tuple: The maximum x and y position.
        """
        max_x = max(coord.x for coord in self.coords)
        max_y = max(coord.y for coord in self.coords)
        return max_x, max_y

    def get_min_coord(self):
        """
        Finds and returns the minimum coordinate position across all coordinates in the frame.

        Returns:
            tuple: The minimum x and y position.
        """
        min_x = min(coord.x for coord in self.coords)
        min_y = min(coord.y for coord in self.coords)
        return min_x, min_y

    def distance_to_other_frame(self, other_frame):
        """
        Calculates the distance to another SingleFrame instance. This could be useful for comparing frames.

        Args:
            other_frame (SingleFrame): The other frame to compare with.

        Returns:
            float: The distance to the other frame.
        """
        # Note that this assumes that both frames have the same number of coordinates.
        return sum(((coord.x - other_coord.x) ** 2 + (coord.y - other_coord.y) ** 2) ** 0.5
                   for coord, other_coord in zip(self.coords, other_frame.coords))

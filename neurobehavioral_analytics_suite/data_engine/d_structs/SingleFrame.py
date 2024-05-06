"""
SingleFrame.py

This module defines the SingleFrame class which encapsulates all data related to a single frame in a neurobehavioral
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
    A class to hold all data related to a single frame.

    Args:
        use_likelihood (bool): A flag to determine whether to use likelihood or not.
        *data_in (list): A list of data related to a single frame.

    Attributes:
        frame_num (int): The frame number.
        coords (list): A list of Coord2D objects representing coordinates in the frame.
    """

    def __init__(self, use_likelihood, *data_in):
        """
        Initializes the SingleFrame object with the provided parameters.

        Args:
            use_likelihood (bool): A flag to determine whether to use likelihood or not.
            *data_in (list): A list of data related to a single frame.
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

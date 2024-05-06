"""
Module for storing positional data from xy-coordinate tracking datasets in the NeuroBehavioral Analytics Suite.

This module defines the PoseData class which is designed to handle positional data from xy-coordinate tracking datasets.
It includes methods for initializing the data, extracting data from a CSV file, and formatting data for console output.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

import csv
from copy import deepcopy
from neurobehavioral_analytics_suite.data_engine.d_structs.SingleFrame import SingleFrame
from neurobehavioral_analytics_suite.data_engine.project import ProjectMetadata


class PoseData:
    """
    A class to handle positional data from xy-coordinate tracking datasets.

    This class is responsible for handling positional data from xy-coordinate tracking datasets. It includes methods
    for initializing the data, extracting data from a CSV file, and formatting data for console output.

    Attributes:
        use_likelihood (bool): Whether to check for p-value.
        meta (ProjectMetadata): Binds with ProjectMetadata.
        csv_path (str): The path to the CSV file.
        frames (list): The list of frames.
    """

    def __init__(self, meta: ProjectMetadata, csv_path: str, use_likelihood):
        """
        Initializes the PoseData object with the provided metadata, CSV path, and likelihood check.

        Args:
            meta (ProjectMetadata): The metadata.
            csv_path (str): The path to the CSV file.
            use_likelihood (bool): Whether to check for p-value.
        """

        self.use_likelihood = use_likelihood
        self.meta = meta
        self.csv_path = csv_path
        self.frames = []
        print("PoseData object initialized")

    def __repr__(self):
        """
        Returns a string representation of the PoseData object.

        The string representation includes the formatted data.

        Returns:
            str: A string representation of the PoseData object.
        """

        return f"PoseData:(\'{self.pack()}\')"

    def pack(self):
        """
        Formats data for console output.

        Returns:
            str: Formatted output.
        """

        pose_out = ""
        if self.meta.end_index == 0:
            for iframe in self.frames:
                rounded_frame = self.round_frame(iframe)
                frame_str = "~"
                for coord in rounded_frame.coords:
                    if self.use_likelihood:
                        frame_str += f"{coord.x}_{coord.y}_{coord.likelihood},"
                    else:
                        frame_str += f"{coord.x}_{coord.y},"
                pose_out += frame_str.rstrip(',')  # Remove trailing comma if present
        else:
            # TODO
            pass
        return pose_out

    def round_frame(self, frame):
        """
        Rounds the coordinates in a frame.

        Args:
            frame: The frame to round the coordinates in.

        Returns:
            The frame with rounded coordinates.
        """

        # Create a deep copy so that the original data isn't modified
        rounded_frame = deepcopy(frame)
        for coord in rounded_frame.coords:
            coord.x = round(coord.x, 3)
            coord.y = round(coord.y, 3)
            if self.use_likelihood:
                coord.likelihood = round(coord.likelihood, 3)
            else:
                coord.likelihood = None  # You can set it to None or just not store it at all.
        return rounded_frame

    def extract_csv(self):
        """
        Extracts data from a CSV file.

        Returns:
            None
        """

        with open(self.csv_path, mode='r') as file:
            csv_file = csv.reader(file)

            for i, row in enumerate(csv_file, -3):
                if self.meta.body_parts_count == 0:
                    self.meta.body_parts_count = (len(row) - 1) / (3 if self.use_likelihood else 2)
                if i >= 0:
                    self.frames.extend([SingleFrame(self.use_likelihood, row[:])])
        print(
            f"PoseData: \'{self.meta.subject}\' .csv file extracted for {self.meta.body_parts_count} coordinates across {len(self.frames)} frames.")

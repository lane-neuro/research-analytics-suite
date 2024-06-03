"""
Module for storing positional func from xy-coordinate tracking datasets in the NeuroBehavioral Analytics Suite.

This module defines the PoseData class which is designed to handle positional func from xy-coordinate tracking datasets.
It includes methods for initializing the func, extracting func from a CSV file, and formatting func for console output.

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
import json
import matplotlib.pyplot as plt
import time
from copy import deepcopy
from neurobehavioral_analytics_suite.data_engine.data_structures.SingleFrame import SingleFrame
from neurobehavioral_analytics_suite.data_engine.project import ProjectMetadata


class PoseData:
    """
    A class to handle positional func from xy-coordinate tracking datasets.

    This class is responsible for handling positional func from xy-coordinate tracking datasets. It includes methods
    for initializing the func, extracting func from a CSV file, and formatting func for console output.

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

        self.logger = None
        self.use_likelihood = use_likelihood
        self.meta = meta
        self.csv_path = csv_path
        self.frames = []

    def __repr__(self):
        """
        Returns a string representation of the PoseData object.

        The string representation includes the formatted func.

        Returns:
            str: A string representation of the PoseData object.
        """

        return f"PoseData:(\'{self.pack()}\')"

    def __getstate__(self):
        state = self.__dict__.copy()
        # Exclude self.logger
        state.pop('logger', None)
        return state

    def __setstate__(self, state):
        # Restore non-serializable attributes here
        self.__dict__.update(state)
        self.logger = None

    def attach_logger(self, logger):
        """
        Attaches a logger to the AnalyticsCore object.

        This method attaches a logger to the PoseData object.

        Args:
            logger: The logger to attach.
        """

        self.logger = logger
        self.logger.info("Logger attached to PoseData object.")

    def pack(self, output_format='string'):
        """
        Formats func for console output.

        Args:
            output_format (str): The desired output format. Options are 'string' and 'json'.

        Returns:
            str or dict: Formatted output.
        """

        # Check if frames are available
        if not self.frames:
            raise ValueError("No frames available to pack")

        if output_format == 'string':
            return self.pack_as_string()
        elif output_format == 'json':
            return self.pack_as_json()
        else:
            raise ValueError(f"Unsupported output_format: {output_format}")

    def pack_as_string(self):
        pose_out = ""
        for iframe in self.frames[self.meta.start_index:self.meta.end_index]:
            rounded_frame = self.round_frame(iframe)
            frame_str = "~"
            for coord in rounded_frame.coords:
                if self.use_likelihood:
                    frame_str += f"{coord.x}_{coord.y}_{coord.likelihood},"
                else:
                    frame_str += f"{coord.x}_{coord.y},"
            pose_out += frame_str.rstrip(',')  # Remove trailing comma if present
        return pose_out

    def pack_as_json(self):
        pose_out = []
        for iframe in self.frames[self.meta.start_index:self.meta.end_index]:
            rounded_frame = self.round_frame(iframe)
            frame_data = []
            for coord in rounded_frame.coords:
                if self.use_likelihood:
                    frame_data.append({
                        'x': coord.x,
                        'y': coord.y,
                        'likelihood': coord.likelihood
                    })
                else:
                    frame_data.append({
                        'x': coord.x,
                        'y': coord.y
                    })
            pose_out.append(frame_data)
        return json.dumps(pose_out)

    def round_frame(self, frame):
        """
        Rounds the coordinates in a frame.

        Args:
            frame: The frame to round the coordinates in.

        Returns:
            The frame with rounded coordinates.
        """

        # Create a deep copy so that the original func isn't modified
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
        Extracts func from a CSV file.

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
        self.meta.logger.info(
            f"PoseData: \'{self.meta.subject}\' .csv file extracted for {self.meta.body_parts_count} coordinates across"
            f" {len(self.frames)} frames.")

    def filter_frames(self, condition):
        """
        Filters out frames based on a condition.

        Args:
            condition (function): A function that takes a frame and returns a boolean.

        Returns:
            list: The list of frames that meet the condition.
        """
        return [frame for frame in self.frames if condition(frame)]

    def transform_data(self, transformation):
        """
        Applies a transformation to the func.

        Args:
            transformation (function): A function that takes a frame and returns a transformed frame.

        Returns:
            None
        """
        self.frames = [transformation(frame) for frame in self.frames]

    def aggregate_data(self, aggregation):
        """
        Performs an aggregation on the func.

        Args:
            aggregation (function): A function that takes a list of frames and returns an aggregated result_output.

        Returns:
            The result_output of the aggregation.
        """
        return aggregation(self.frames)

    def annotate_data(self, annotation):
        """
        Adds an annotation to the func.

        Args:
            annotation (function): A function that takes a frame and returns an annotated frame.

        Returns:
            None
        """
        self.frames = [annotation(frame) for frame in self.frames]

    def condition(self, frame):
        """
        A condition function that checks if the average likelihood of the coordinates in a frame is above 0.5.

        Args:
            frame (SingleFrame): The frame to check.

        Returns:
            bool: True if the average likelihood is above 0.5, False otherwise.
        """
        if frame.use_likelihood:
            average_likelihood = sum(coord.likelihood for coord in frame.coords) / len(frame.coords)
            return average_likelihood > 0.5
        else:
            return True  # If likelihood is not used, all frames pass the condition

    def transformation(self, frame):
        """
        A transformation function that normalizes the coordinates in a frame.

        Args:
            frame (SingleFrame): The frame to transform.

        Returns:
            SingleFrame: The transformed frame.
        """
        max_x = max(coord.x for coord in frame.coords)
        max_y = max(coord.y for coord in frame.coords)
        for coord in frame.coords:
            coord.x /= max_x
            coord.y /= max_y
        return frame

    def aggregation(self, frames):
        """
        An aggregation function that calculates the average position of all coordinates in each frame.

        Args:
            frames (list): The list of frames.

        Returns:
            list: The list of average positions.
        """
        average_positions = []
        for frame in frames:
            average_x = sum(coord.x for coord in frame.coords) / len(frame.coords)
            average_y = sum(coord.y for coord in frame.coords) / len(frame.coords)
            average_positions.append((average_x, average_y))
        return average_positions

    def annotation(self, frame):
        """
        An annotation function that adds a timestamp to a frame.

        Args:
            frame (SingleFrame): The frame to annotate.

        Returns:
            SingleFrame: The annotated frame.
        """
        frame.timestamp = time.time()  # Add a timestamp to the frame
        return frame

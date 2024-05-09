"""
A module for the NeuroBehavioral Analytics Suite's Data Engine.

This module contains the DataEngine class, which serves as the primary data handler for a project. It includes methods
for initializing the data engine, setting the data range, and executing the data engine.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

from neurobehavioral_analytics_suite.data_engine.d_structs.PoseData import PoseData
from neurobehavioral_analytics_suite.analytics.Analytics import Analytics
from neurobehavioral_analytics_suite.data_engine.project.ProjectMetadata import ProjectMetadata


class DataEngine:
    """
    The primary data handler for a project.

    This class is responsible for initializing the data engine, setting the data range, and executing the data engine.

    Attributes:
        dask_client: Pointer to primary Dask client.
        b_likelihood: Whether to filter data for p-value (project-global).
        analytics: Initialize Analytics Engine.
        meta: Initialize ProjectMetadata object.
        pose: Initialize PoseData object to process .csv data.
    """

    def __init__(
            self,
            directory_in: str,
            user_in: str,
            subject_in: str,
            framerate: int,
            csv_path: str,
            use_likelihood=True
    ):
        """
        Initializes the DataEngine.

        Args:
            directory_in (str): Directory where project files will be located.
            user_in (str): Name of user/experimenter.
            subject_in (str): Name of the subject of experiment (e.g., mouse, human, rat, etc.).
            framerate (int): Camera Framerate.
            csv_path (str): List of files containing experimental data.
            use_likelihood (bool): Whether to filter data for p-value (project-global).
        """

        self.dask_client = None  # Pointer to primary Dask client
        self.b_likelihood = use_likelihood  # Whether to filter data for p-value (project-global)
        self.analytics = Analytics()  # Initialize Analytics Engine
        self.meta = ProjectMetadata(  # Initialize ProjectMetadata object
            directory_in,
            user_in,
            subject_in,
            framerate,
            self.analytics,
        )
        self.pose = PoseData(  # Initialize PoseData object to process .csv data
            self.meta,
            csv_path,
            self.b_likelihood
        )
        self.pose.extract_csv()  # Extract & process positional data from .csv

    def __repr__(self):
        """
        Returns a readable string containing all DataEngine parameters.

        Returns:
            str: A string representation of the DataEngine instance.
        """

        transformations = ', '.join([str(transform) for transform in self.analytics.transformations])
        return (f"DataEngine:(\nMetadata:\'{self.meta}\',"
                f"\n\nTransformations: [{transformations}],"
                f"\n\nPose Tokens:\'{self.pose.pack()}\', "
                f"\n\nNumber of Pose Tokens: {len(self.pose.pack())})")

    def set_range(self, start_frame: int, end_frame: int):
        """
        Sets the current data range.

        Args:
            start_frame (int): The start frame of the data range.
            end_frame (int): The end frame of the data range.
        """

        self.meta.start_index = start_frame
        self.meta.end_index = end_frame
        print(f"DataEngine: current data range set to {start_frame} : {end_frame}")
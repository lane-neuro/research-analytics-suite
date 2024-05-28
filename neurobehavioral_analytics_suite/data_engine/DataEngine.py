"""
A module for the NeuroBehavioral Analytics Suite's Data Engine.

This module contains the DataEngine class, which serves as the primary func handler for a project. It includes methods
for initializing the func engine, setting the func range, and executing the func engine.

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
from neurobehavioral_analytics_suite.utils.Logger import Logger


class DataEngine:
    """
    The primary func handler for a project.

    This class is responsible for initializing the func engine, setting the func range, and executing the func engine.

    Attributes:
        dask_client: Pointer to primary Dask client.
        b_likelihood: Whether to filter func for p-value (project-global).
        analytics: Initialize Analytics Engine.
        meta: Initialize ProjectMetadata object.
        pose: Initialize PoseData object to process .csv func.
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
            csv_path (str): List of files containing experimental func.
            use_likelihood (bool): Whether to filter func for p-value (project-global).
        """

        self.logger = None  # Pointer to Logger
        self.dask_client = None  # Pointer to primary Dask client
        self.b_likelihood = use_likelihood  # Whether to filter func for p-value (project-global)
        self.analytics = Analytics()  # Initialize Analytics Engine
        self.meta = ProjectMetadata(  # Initialize ProjectMetadata object
            directory_in,
            user_in,
            subject_in,
            framerate,
            self.analytics
        )
        self.pose = PoseData(  # Initialize PoseData object to process .csv func
            self.meta,
            csv_path,
            self.b_likelihood
        )

    def extract_csv(self):
        self.pose.extract_csv()  # Extract & process positional func from .csv

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

    def __getstate__(self):
        state = self.__dict__.copy()
        # Exclude self.logger
        state.pop('logger', None)
        return state

    def __setstate__(self, state):
        # Restore non-serializable attributes here
        self.__dict__.update(state)
        self.logger = None

    def attach_logger(self, logger: Logger):
        """
        Attaches a logger to the DataEngine object and assigns the logger to other objects in instance.

        This method attaches a logger to the DataEngine object.

        Args:
            logger: The logger to attach.
        """

        self.logger = logger
        self.logger.info("Logger attached to DataEngine object.")

        self.meta.attach_logger(logger)
        self.pose.attach_logger(logger)
        self.analytics.attach_logger(logger)

    def get_pickleable_data(self):
        data = self.__dict__.copy()

        # Exclude serializable objects
        data.pop('logger', None)

        return data

    def set_range(self, start_frame: int, end_frame: int):
        """
        Sets the current func range.

        Args:
            start_frame (int): The start frame of the func range.
            end_frame (int): The end frame of the func range.
        """

        self.meta.start_index = start_frame
        self.meta.end_index = end_frame
        self.logger.info(f"DataEngine: current func range set to {start_frame} : {end_frame}")

"""
Module for storing project metadata for the active project in the NeuroBehavioral Analytics Suite.

This module defines the ProjectMetadata class which is designed to store project metadata for the
active project. It includes methods for initializing the metadata, and providing a string representation of the metadata

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

from neurobehavioral_analytics_suite.analytics import AnalyticsCore
from neurobehavioral_analytics_suite.utils.Logger import Logger


class ProjectMetadata:
    """
    A class to store project metadata for the active project.

    This class is responsible for storing project metadata such as the directory, user, subject,
    framerate, and analytics for the active project.

    Attributes:
        analytics (AnalyticsCore): Pointer to AnalyticsCore engine.
        base_dir (str): Root directory for project.
        username (str): Name of current experimenter / researcher.
        subject (str): Name of subject (i.e., 'mouse-2', 'CB6', etc.).
        body_parts_count (int): Number of body parts in pixel-tracking func.
        framerate (int): Framerate of the camera.
        start_index (int): First frame index of relevant func.
        end_index (int): Final frame index of relevant func.
    """

    def __init__(self, directory_in: str, user_in: str, subject_in: str, framerate_in: int,
                 analytics_in: AnalyticsCore):
        """
        Initializes the ProjectMetadata object with the provided parameters.

        Args:
            directory_in (str): Root directory for project.
            user_in (str): Name of current experimenter / researcher.
            subject_in (str): Name of subject (i.e., 'mouse-2', 'CB6', etc.).
            framerate_in (int): Framerate of the camera.
            analytics_in (AnalyticsCore): Pointer to AnalyticsCore engine.
        """

        self.logger = None                          # pointer to Logger
        self.analytics = analytics_in               # pointer to AnalyticsCore engine
        self.base_dir = directory_in                # root directory for project
        self.username = user_in                     # name of current experimenter / researcher
        self.subject = subject_in                   # name of subject (i.e., 'mouse-2', 'CB6', etc.)
        self.body_parts_count = 0                   # number of body parts in pixel-tracking func
        self.framerate = framerate_in               # framerate of the camera
        self.start_index = 0                        # first frame index of relevant func
        self.end_index = 0                          # final frame index of relevant func

    def __repr__(self):
        """
        Returns a string representation of the ProjectMetadata object.

        The string representation includes the subject, number of body parts, and framerate.

        Returns:
            str: A string representation of the ProjectMetadata object.
        """

        return (f"ProjectMetadata:(Animal: \'{self.subject}\', Number of Body Parts: {self.body_parts_count}, "
                f"Framerate:{self.framerate}fps)")

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
        Attaches a logger to the ProjectMetadata object.

        This method attaches a logger to the ProjectMetadata object.

        Args:
            logger: The logger to attach.
        """

        self.logger = logger
        self.logger.info("Logger attached to ProjectMetadata object.")

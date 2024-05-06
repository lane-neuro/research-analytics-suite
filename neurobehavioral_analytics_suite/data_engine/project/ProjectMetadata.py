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

from neurobehavioral_analytics_suite.analytics import Analytics


class ProjectMetadata:
    """
    A class to store project metadata for the active project.

    This class is responsible for storing project metadata such as the directory, user, subject,
    framerate, and analytics for the active project.

    Attributes:
        analytics (Analytics): Pointer to Analytics engine.
        base_dir (str): Root directory for project.
        username (str): Name of current experimenter / researcher.
        subject (str): Name of subject (i.e., 'mouse-2', 'CB6', etc.).
        body_parts_count (int): Number of body parts in pixel-tracking data.
        framerate (int): Framerate of the camera.
        start_index (int): First frame index of relevant data.
        end_index (int): Final frame index of relevant data.
    """

    def __init__(self, directory_in: str, user_in: str, subject_in: str, framerate_in: int,
                 analytics_in: Analytics):
        """
        Initializes the ProjectMetadata object with the provided parameters.

        Args:
            directory_in (str): Root directory for project.
            user_in (str): Name of current experimenter / researcher.
            subject_in (str): Name of subject (i.e., 'mouse-2', 'CB6', etc.).
            framerate_in (int): Framerate of the camera.
            analytics_in (Analytics): Pointer to Analytics engine.
        """

        self.analytics = analytics_in               # pointer to Analytics engine
        self.base_dir = directory_in                # root directory for project
        self.username = user_in                     # name of current experimenter / researcher
        self.subject = subject_in                   # name of subject (i.e., 'mouse-2', 'CB6', etc.)
        self.body_parts_count = 0                   # number of body parts in pixel-tracking data
        self.framerate = framerate_in               # framerate of the camera
        self.start_index = 0                        # first frame index of relevant data
        self.end_index = 0                          # final frame index of relevant data

        print(f"Metadata storage initialized...")

    def __repr__(self):
        """
        Returns a string representation of the ProjectMetadata object.

        The string representation includes the subject, number of body parts, and framerate.

        Returns:
            str: A string representation of the ProjectMetadata object.
        """

        return (f"ProjectMetadata:(Animal: \'{self.subject}\', Number of Body Parts: {self.body_parts_count}, "
                f"Framerate:{self.framerate}fps)")

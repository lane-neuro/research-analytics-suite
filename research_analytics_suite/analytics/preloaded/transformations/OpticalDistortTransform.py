"""
Module for applying optical distortion transformation in the Research Analytics Suite.

This module defines the OpticalDistortTransform class which is designed to apply an optical distortion transformation
to a given datapoint. It includes methods for initializing the transformation and applying it to a datapoint.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""


class OpticalDistortTransform:
    """
    A class to apply an optical distortion transformation to a given datapoint.

    This class is responsible for applying an optical distortion transformation to a datapoint. The distortion strength
    can be specified during initialization.

    Attributes:
        pose_frames: The frames of the pose to be transformed.
        k1 (float): The strength of the optical distortion transformation.
        x_center (float): The x-coordinate of the center of the distortion.
        y_center (float): The y-coordinate of the center of the distortion.
    """

    def __init__(self, pose_frames, k1=5e-10):
        """
        Initializes the OpticalDistortTransform object with the provided distortion strength and pose frames.

        Args:
            pose_frames: The frames of the pose to be transformed.
            k1 (float): The strength of the optical distortion transformation.
        """

        x_vals = [coord.x for frame in pose_frames for coord in frame.coords]
        y_vals = [coord.y for frame in pose_frames for coord in frame.coords]

        self.x_center = (max(x_vals) + min(x_vals)) / 2
        self.y_center = (max(y_vals) + min(y_vals)) / 2

        # Calculate k1 based on your requirements.
        # Here, I've simply normalized it based on the image space,
        # but you might want to adjust this based on the desired distortion level.
        self.k1 = k1 * (max(x_vals) - min(x_vals))

    def __repr__(self):
        """
        Returns a string representation of the OpticalDistortTransform object.

        The string representation includes the distortion strength.

        Returns:
            str: A string representation of the OpticalDistortTransform object.
        """

        return f"OpticalDistortTransform, k1 = {self.k1}"

    def transform(self, datapoint):
        """
        Applies the optical distortion transformation to the given datapoint.

        This method applies a radial distortion to the x and y coordinates of the datapoint.

        Args:
            datapoint: The datapoint to apply the optical distortion transformation to.

        Returns:
            The transformed datapoint.
        """

        x = datapoint.x - self.x_center
        y = datapoint.y - self.y_center
        r2 = x ** 2 + y ** 2
        x_distorted = x * (1 + self.k1 * r2) + self.x_center
        y_distorted = y * (1 + self.k1 * r2) + self.y_center
        datapoint.x = x_distorted
        datapoint.y = y_distorted
        return datapoint

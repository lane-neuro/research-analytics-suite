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
        max_distortion (float): The maximum allowable distortion factor.
    """

    def __init__(self, pose_frames, k1=5e-10, max_distortion=1e6):
        """
        Initializes the OpticalDistortTransform object with the provided distortion strength and pose frames.

        Args:
            pose_frames: The frames of the pose to be transformed.
            k1 (float): The strength of the optical distortion transformation.
            max_distortion (float): The maximum allowable distortion factor.
        """
        if k1 < 0:
            raise ValueError("k1 must be non-negative")

        x_vals = [coord.x for frame in pose_frames for coord in frame.coords]
        y_vals = [coord.y for frame in pose_frames for coord in frame.coords]

        self.x_center = (max(x_vals) + min(x_vals)) / 2
        self.y_center = (max(y_vals) + min(y_vals)) / 2

        self.k1 = k1 * (max(x_vals) - min(x_vals))
        self.max_distortion = max_distortion

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
        try:
            x = float(datapoint.x) - self.x_center
            y = float(datapoint.y) - self.y_center
        except ValueError:
            raise TypeError("Datapoint coordinates must be numeric")

        r2 = x ** 2 + y ** 2

        # Cap the maximum value of r2 to prevent extremely large distortion factors
        max_r2 = (1 / self.k1) if self.k1 > 0 else float('inf')
        r2 = min(r2, max_r2)

        distortion_factor = 1 + self.k1 * r2

        if distortion_factor > self.max_distortion:
            from research_analytics_suite.utils import CustomLogger
            CustomLogger().error(
                ValueError("The distortion is too strong for the given k1 value and datapoint coordinates."),
                self.__class__.__name__)
            distortion_factor = self.max_distortion

        x_distorted = x * distortion_factor + self.x_center
        y_distorted = y * distortion_factor + self.y_center
        datapoint.x = x_distorted
        datapoint.y = y_distorted

        return datapoint


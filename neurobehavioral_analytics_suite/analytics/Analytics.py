"""
Analytical Engine to process neurobehavioral func from NBAS-DataEngine.

This module defines the Analytics class which is designed to apply a series of transformations
to a given datapoint. It includes methods for initializing the transformation list, adding a transformation,
and applying all transformations to a datapoint.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""


class Analytics:
    """
    A class to apply a series of transformations to a given datapoint.

    This class is responsible for applying a series of transformations to a datapoint. The transformations
    can be specified during initialization or added later.

    Attributes:
        transformations (list): The list of transformations to be applied.
    """

    def __init__(self, transformations=None):
        """
        Initializes the Analytics object with the provided list of transformations.

        Args:
            transformations (list): The list of transformations to be applied.
        """

        self.logger = None

        if transformations is None:
            self.transformations = []
        else:
            self.transformations = transformations

    def __repr__(self):
        """
        Returns a string representation of the Analytics object.

        The string representation includes the number of transformations.

        Returns:
            str: A string representation of the Analytics object.
        """

        return f"Analytics, number of transformations = {len(self.transformations)}"

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
        Attaches a logger to the Analytics object.

        This method attaches a logger to the Analytics object.

        Args:
            logger: The logger to attach.
        """

        self.logger = logger
        self.logger.info("Logger attached to Analytics object.")

    def transform(self, datapoint):
        """
        Applies all transformations to the given datapoint.

        This method applies each transformation in the list to the datapoint in order.

        Args:
            datapoint: The datapoint to apply the transformations to.

        Returns:
            The transformed datapoint.
        """

        for transformation in self.transformations:
            datapoint = transformation.transform(datapoint)
        return datapoint

    def add_transformation(self, transformation):
        """
        Adds a transformation to the list of transformations.

        This method adds a transformation to the end of the list of transformations.

        Args:
            transformation: The transformation to add.
        """

        self.transformations.append(transformation)

"""
DataPipeline Module

This module defines the DataPipeline class, which provides a framework for building and managing
data transformation pipelines within the neurobehavioral analytics suite.

Author: Lane
"""


class DataPipeline:
    """
    A class to build and manage data transformation pipelines.
    """
    def __init__(self):
        """
        Initializes the DataPipeline instance.
        """
        self._steps = []

    def add_step(self, step):
        """
        Adds a transformation step to the pipeline.

        Args:
            step (function): The transformation step to add.
        """
        self._steps.append(step)

    def execute(self, data):
        """
        Executes the transformation pipeline on the data.

        Args:
            data: The data to transform.

        Returns:
            The transformed data.
        """
        for step in self._steps:
            data = step(data)
        return data

    @property
    def steps(self):
        return self._steps

    @steps.setter
    def steps(self, value):
        self._steps = value

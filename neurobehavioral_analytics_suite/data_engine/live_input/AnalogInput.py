"""
AnalogInput Module

Defines the AnalogInput class for handling live data input from analog sources.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from neurobehavioral_analytics_suite.data_engine.live_input import BaseInput


class AnalogInput(BaseInput):
    """
    Class for handling live data input from an analog source.

    Attributes:
        read_function: The function to read data from the analog source.
    """
    def __init__(self, read_function):
        """
        Initializes the AnalogInput instance.

        Args:
            read_function (function): The function to read data from the analog source.
        """
        super().__init__(source="Analog")
        self.read_function = read_function

    def read_data(self):
        """
        Reads data from the analog source.

        Returns:
            The data read from the analog source.
        """
        return self.read_function()

    def close(self):
        """
        Placeholder for closing any resources, if necessary.
        """
        pass

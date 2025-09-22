"""
LiveDataHandler Module

This module defines the LiveDataHandler class, which handles live data inputs and integrates them into the
Research Analytics Suite. It manages the lifecycle of live data sources and updates the data engine with new data.

Author: Lane
"""

from .BaseInput import BaseInput
from research_analytics_suite.utils.CustomLogger import CustomLogger
from research_analytics_suite.commands import command, link_class_commands


@link_class_commands
class LiveDataHandler:
    """
    A class to handle live data inputs and integrate them into the Research Analytics Suite.

    Attributes:
        data_engine (DataEngineOptimized): The data engine to update with live data.
        live_inputs (list): List of live data inputs.
    """
    def __init__(self, data_engine):
        """
        Initializes the LiveDataHandler instance.

        Args:
            data_engine (DataEngineOptimized): The data engine to update with live data.
        """
        self.data_engine = data_engine
        self._logger = CustomLogger()
        self.live_inputs = []

    @command
    def add_live_input(self, live_input: BaseInput):
        """
        Adds a live data input to the handler.

        Args:
            live_input (BaseInput): The live data input to add.
        """
        self.live_inputs.append(live_input)

    @command
    def start_all(self):
        """Starts all live data inputs."""
        for live_input in self.live_inputs:
            live_input.start()

    @command
    def stop_all(self):
        """Stops all live data inputs."""
        for live_input in self.live_inputs:
            live_input.stop()

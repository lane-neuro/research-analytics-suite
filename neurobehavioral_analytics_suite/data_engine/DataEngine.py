"""
Data Engine for NeuroBehavioral Analytics Suite.

This module contains the DataEngine class which serves as the primary data handler for a project. It includes methods
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

import asyncio
import nest_asyncio
from aioconsole import ainput
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
        cmd_history: String array of prior commands entered into terminal.
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
        self.cmd_history = []  # String array of prior commands entered into terminal

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

    async def console_loop(self):
        """
        Handles user-input data from the console.

        This method is responsible for asynchronously waiting for user input from the console.
        The input is then added to the command history of the DataEngine instance.

        Returns:
            str: User-input data from the console.
        """

        # Await user input from the console
        line = await ainput('->> ')

        # Add the input line to the command history
        self.cmd_history.append(line)

        return line

    async def exec_loop(self):
        """
        Executes the main loop of the data engine.

        This method is responsible for setting up the asyncio event loop and continuously monitoring for tasks.
        It specifically waits for user input from the console and executes the input as a command.
        If an exception occurs during the execution of the command, it is caught and printed to the console.

        Note: This method runs indefinitely until the program is stopped.
        """

        # Initialize the Dask client to None
        self.dask_client = None

        # Apply the nest_asyncio patch to enable nested use of asyncio's event loop
        nest_asyncio.apply()

        # Get the main event loop
        main_loop = asyncio.get_event_loop()

        # Start an indefinite loop to monitor asyncio tasks
        while True:

            # Create a list of tasks for asyncio to monitor
            # Currently, the only task is waiting for user input from the console
            tasks = [
                main_loop.create_task(self.console_loop()),
            ]

            # Wait for the tasks to complete
            # In this case, it waits for user input from the console
            user_input = await asyncio.gather(*tasks)

            # Try to execute the user input as a command
            # If an exception occurs, catch it and print it to the console
            try:
                print(user_input)
                print(exec(user_input[0]))
            except Exception as e:
                print("An exception occurred: " + str(e))

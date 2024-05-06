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
import psutil
from aioconsole import ainput

from neurobehavioral_analytics_suite.data_engine import ProgressTask
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
        self.tasks = []  # List of asyncio.Future objects representing tasks
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

    async def monitor_resource_usage(self, cpu_threshold=90, memory_threshold=90):
        """
        Monitors the usage of CPU and memory.

        If the usage of CPU or memory exceeds the specified thresholds, a warning is printed.

        Args:
            cpu_threshold (int): The CPU usage threshold.
            memory_threshold (int): The memory usage threshold.
        """
        while True:
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent

            if cpu_usage > cpu_threshold:
                print(f"Warning: CPU usage has exceeded {cpu_threshold}%: current usage is {cpu_usage}%")

            if memory_usage > memory_threshold:
                print(f"Warning: Memory usage has exceeded {memory_threshold}%: current usage is {memory_usage}%")

            await asyncio.sleep(1)  # sleep for 1 second before checking again

    async def monitor_task_progress(self, task: ProgressTask):
        """
        Monitors the progress of a task.

        This method continuously checks the progress of a given task until it's done.
        The progress is assumed to be stored in the 'progress' attribute of the task object.
        The method sleeps for 1 second between each check.

        Args:
            task (ProgressTask): The task object representing the task. It should be an instance of the ProgressTask
            class.

        Note:
            This is a coroutine and should be awaited.
        """

        while not task.done():
            # The progress of the task could be stored as an attribute of the future object
            # This is just a placeholder implementation and would depend on your specific use case
            print(f"Task progress: {task.progress}%")
            await asyncio.sleep(1)  # sleep for 1 second before checking again

    async def monitor_errors(self, future):
        """
        Monitors for errors in a task.

        Args:
            future (Future): The future object representing the task.
        """
        try:
            result = await future
            print(f"Task completed with result: {result}")
        except Exception as e:
            print(f"An error occurred in the task: {e}")

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
                main_loop.create_task(self.monitor_resource_usage()),
            ]

            # Add tasks for error handling, progress monitoring, and task completion checking
            # Assume that self.tasks is a list of asyncio.Future objects representing the tasks
            for task in self.tasks:
                tasks.append(main_loop.create_task(self.monitor_errors(task)))
                tasks.append(main_loop.create_task(self.monitor_task_progress(task)))

            # Wait for the tasks to complete
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

            # Handle the results of the completed tasks
            for task in list(done):
                try:
                    result = task.result()
                    print(f"Task completed with result: {result}")
                except Exception as e:
                    print(f"An error occurred in the task: {e}")
                    done.remove(task)

            # Reschedule the pending tasks
            self.tasks = list(pending)

"""
The primary data handler for a project.
"""

__author__ = 'Lane'
__copyright__ = 'Lane'
__credits__ = ['Lane']
__license__ = 'BSD 3-Clause License'
__version__ = '0.0.0.1'
__maintainer__ = 'Lane'
__emails__ = 'justlane@uw.edu'
__status__ = 'Prototype'

import asyncio
import nest_asyncio
from aioconsole import ainput
from .d_structs.PoseData import PoseData
from ..analytics.Analytics import Analytics
from .project.ProjectMetadata import ProjectMetadata


class DataEngine:

    def __init__(
            self,
            directory_in: str,
            user_in: str,
            subject_in: str,
            framerate: int,
            csv_path: str,
            use_likelihood=True
    ):

        self.dask_client = None                             # Pointer to primary Dask client

        self.b_likelihood = use_likelihood                  # Whether to filter data for p-value (project-global)

        self.analytics = Analytics()                        # Initialize Analytics Engine
        self.meta = ProjectMetadata(                        # Initialize ProjectMetadata object
            directory_in,
            user_in,
            subject_in,
            framerate,
            self.analytics,
        )
        self.pose = PoseData(                               # Initialize PoseData object to process .csv data
            self.meta,
            csv_path,
            self.b_likelihood
        )
        self.pose.extract_csv()                             # Extract & process positional data from .csv

        self.cmd_history = []                               # String array of prior commands entered into terminal

    def __repr__(self):
        # Returns readable string containing all DataEngine parameters
        transformations = ', '.join([str(transform) for transform in self.analytics.transformations])
        return (f"DataEngine:(\nMetadata:\'{self.meta}\',"
                f"\n\nTransformations: [{transformations}],"
                f"\n\nPose Tokens:\'{self.pose.pack()}\', "
                f"\n\nNumber of Pose Tokens: {len(self.pose.pack())})")

    def set_range(self, start_frame: int, end_frame: int):
        self.meta.start_index = start_frame
        self.meta.end_index = end_frame
        print(f"DataEngine: current data range set to {start_frame} : {end_frame}")

    async def console_loop(self):
        """
        The console-input method of the data engine.

        Returns user-input data from the console.
        """

        line = await ainput('->> ')
        self.cmd_history.append(line)           # add command to array
        return line

    async def exec_loop(self):
        """
        The main loop for executing the data engine.
        """

        self.dask_client = None

        # allows for nested asyncio loops/threads
        nest_asyncio.apply()
        main_loop = asyncio.get_event_loop()

        # Indefinite execution loop monitoring multiple asyncio threads
        while True:

            # an array of concurrent tasks for asycio to monitor
            tasks = [
                main_loop.create_task(self.console_loop()),
            ]

            # awaits for task completions, particularly for user input to the console
            user_input = await asyncio.gather(*tasks)
            try:
                print(user_input)
                print(exec(user_input[0]))
            except Exception as e:
                print("An exception occurred: " + str(e))

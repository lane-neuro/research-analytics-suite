#! python
# -*- coding: utf-8 -*-

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
import aioconsole
from aioconsole import ainput

from .d_structs.PoseData import PoseData
from ..analytics.Analytics import Analytics
from .project.ProjectMetadata import ProjectMetadata
from dask.distributed import Client

"""
Docstring
"""


class DataEngine:

    def __init__(self, directory_in: str, user_in: str, subject_in: str, framerate: int, csv_path: str,
                 use_likelihood=True):
        self.dask_client = None
        self.use_likelihood = use_likelihood
        self.analytics = Analytics()
        self.meta = ProjectMetadata(directory_in, user_in, subject_in, framerate, self.analytics)
        self.pose = PoseData(self.meta, csv_path, self.use_likelihood)
        self.pose.extract_csv()

    def __repr__(self):
        transformations = ', '.join([str(transform) for transform in self.analytics.transformations])
        return f"DataEngine:(\nMetadata:\'{self.meta}\',\n\nTransformations: [{transformations}],\n\nPose Tokens:\'{self.pose.pack()}\', \n\nNumber of Pose Tokens: {len(self.pose.pack())})"

    def set_range(self, start_frame: int, end_frame: int):
        self.meta.start_index = start_frame
        self.meta.end_index = end_frame
        print(f"DataEngine: current data range set to {start_frame} : {end_frame}")

    async def console_loop(self):
        line = await ainput('->> ')
        return line

    async def exec_loop(self):
        # self.dask_client = await Client(asynchronous=True)

        nest_asyncio.apply()
        main_loop = asyncio.get_event_loop()
        while True:
            tasks = [main_loop.create_task(self.console_loop())]
            user_input = await asyncio.gather(*tasks)
            try:
                print(user_input)
                print(exec(user_input[0]))
            except Exception as e:
                print("An exception occurred. " + str(e))

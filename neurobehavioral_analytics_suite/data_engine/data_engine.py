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

"""
Docstring
"""


# Imports

def start_data_engine():
    print("Starting Data Engine")


class data_engine:

    def __init__(self, animal: str, framerate: int, csv_path: str, use_likelihood=True):
        self.use_likelihood = use_likelihood
        self.engine = bGPT_engine()
        self.meta = bGPT_metadata(animal, framerate, self.engine)
        self.pose = bGPT_posedata(self.meta, csv_path, self.use_likelihood)
        self.pose.extract_csv()

        ## special transformations for training that use full sequence information
        self.optical_distortion = OpticalDistortTransform(self.pose.frames)
        self.engine.add_transformation(self.optical_distortion)

    def __repr__(self):
        transformations = ', '.join([str(transform) for transform in self.engine.transformations])
        return f"bGPT_generator:(\nMetadata:\'{self.meta}\',\n\nTransformations: [{transformations}],\n\nPose Tokens:\'{self.pose.pack()}\', \n\nNumber of Pose Tokens: {len(self.pose.pack())})"

    def transform(self, *args):
        transformations = list(args)
        self.engine = bGPT_engine(transformations)
        self.pose.transform(self.engine)
        return repr(self)

    def set_range(self, start_frame: int, end_frame: int):
        self.meta.start_index = start_frame
        self.meta.end_index = end_frame
        print(f"bGPT_generator: current data range set to {start_frame} : {end_frame}")

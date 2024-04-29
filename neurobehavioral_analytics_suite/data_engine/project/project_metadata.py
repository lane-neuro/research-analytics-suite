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

from neurobehavioral_analytics_suite.data_engine import data_engine

"""
Docstring
"""


# Imports

class project_metadata:

    def __init__(self, animal_in: str, framerate_in: int, engine_in: data_engine):
        self.animal = animal_in
        self.body_parts_count = 0
        self.framerate = framerate_in
        self.engine = engine_in
        self.start_index = 0
        self.end_index = 0
        print(f"Metadata storage initialized...")

    def __repr__(self):
        return f"project_metadata:(Animal: \'{self.animal}\', Number of Body Parts: {self.body_parts_count}, Framerate:{self.framerate}fps)"


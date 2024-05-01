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

from ...analytics import Analytics

"""
Docstring
"""


class ProjectMetadata(object):

    def __init__(self, directory_in: str, user_in: str, animal_in: str, framerate_in: int,
                 analytics_in: Analytics):
        self.BASE_DIR = directory_in
        self.username = user_in
        self.animal = animal_in
        self.body_parts_count = 0
        self.framerate = framerate_in
        self.analytics = analytics_in
        self.start_index = 0
        self.end_index = 0
        print(f"Metadata storage initialized...")

    def __repr__(self):
        return f"ProjectMetadata:(Animal: \'{self.animal}\', Number of Body Parts: {self.body_parts_count}, Framerate:{self.framerate}fps)"


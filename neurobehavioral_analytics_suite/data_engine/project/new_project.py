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

from .load_project import load_project
from .save_project import save_project
from ..DataEngine import DataEngine

"""
Docstring
"""


def new_project(csv_dir_in: str, user_in: str, subject_in: str, framerate_in: int, csv_path: str):
    base_engine = DataEngine(csv_dir_in, user_in, subject_in, framerate_in, csv_path)
    save_file = save_project(base_engine)
    return load_project(save_file)


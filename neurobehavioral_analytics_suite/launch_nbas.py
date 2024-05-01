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

import argparse
from .data_engine.DataEngine import start_data_engine
from .data_engine.project.new_project import new_project
from .data_engine.project.project_load import project_load

"""
Docstring
"""


def launch_nbas():
    arg, extra = launch_args().parse_known_args()
    if arg.load_project is None:
        print('New Project Parameters Detected - Creating New Project')
        proj = new_project(arg.directory, arg.user_name, arg.subject_name, arg.camera_framerate, arg.file_list)
        start_data_engine(proj)
    else:
        print('Project File Detected - Loading Project at: ' + arg.load_project)
        start_data_engine(project_load(arg.load_project))


def launch_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-l', '--load_project',
                        help='Load project from specified file')
    parser.add_argument('-u', '--user_name',
                        help='Name of user/experimenter')
    parser.add_argument('-d', '--directory',
                        help='Directory where project files will be located')
    parser.add_argument('-s', '--subject_name',
                        help='Name of the subject of experiment (e.g., mouse, human, rat, etc.)')
    parser.add_argument('-f', '--file_list',
                        help='List of files containing experimental data')
    parser.add_argument('-c', '--camera_framerate',
                        help='Camera Framerate')

    return parser

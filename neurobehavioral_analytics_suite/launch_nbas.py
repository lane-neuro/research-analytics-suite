"""
Launch script for NeuroBehavioral Analytics Suite
"""

__author__ = 'Lane'
__copyright__ = 'Lane'
__credits__ = ['Lane']
__license__ = 'BSD 3-Clause License'
__version__ = '0.0.0.1'
__maintainer__ = 'Lane'
__emails__ = 'justlane@uw.edu'
__status__ = 'Prototype'

import argparse
import asyncio
from .data_engine.project.new_project import new_project
from .data_engine.project.load_project import load_project


def launch_nbas():
    """
    Launches NeuroBehavioral Analytics Suite
    """

    active_project = None
    args, extra = launch_args().parse_known_args()

    # Checks args for -o '--open_project' flag.
    # Exists: Open project from file
    if args.open_project is None:
        print('New Project Parameters Detected - Creating New Project')
        active_project = new_project(args.directory, args.user_name, args.subject_name,
                                     args.camera_framerate, args.file_list)
    else:
        print('Project File Detected - Loading Project at: ' + args.open_project)
        active_project = load_project(args.open_project)

    # ensure we now have an active project open
    assert active_project is not None

    # initialize asyncio primary event loop
    asyncio.ensure_future(active_project.exec_loop())
    asyncio.get_event_loop().run_forever()


def launch_args():
    """
    Parse command line arguments

    :return:

    """

    parser = argparse.ArgumentParser()

    parser.add_argument('-o', '--open_project',
                        help='Opens an existing project from the specified file')
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

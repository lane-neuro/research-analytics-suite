"""
A module for launching the NeuroBehavioral Analytics Suite.

This module contains the main entry point for launching the NeuroBehavioral Analytics Suite. It includes functions
for parsing command line arguments and launching the application.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

import argparse
import asyncio
from neurobehavioral_analytics_suite.data_engine.project.new_project import new_project
from neurobehavioral_analytics_suite.data_engine.project.load_project import load_project
from neurobehavioral_analytics_suite.operation_handler.OperationHandler import OperationHandler


async def launch_nbas():
    """
    Launches the NeuroBehavioral Analytics Suite.

    This function checks the command line arguments to determine whether to create a new project or open an existing
    one. It then initializes the asyncio event loop and starts the application.

    Raises:
        AssertionError: If no active project is open.
    """

    active_project = None
    args, extra = launch_args().parse_known_args()

    # Checks args for -o '--open_project' flag.
    # If it exists, open the project from the file
    if args.open_project is None:
        print('New Project Parameters Detected - Creating New Project')
        active_project = new_project(args.directory, args.user_name, args.subject_name,
                                     args.camera_framerate, args.file_list)
    else:
        print('Project File Detected - Loading Project at: ' + args.open_project)
        active_project = load_project(args.open_project)

    # Ensure we now have an active project open
    assert active_project is not None

    operation_handler = OperationHandler()
    asyncio.run(operation_handler.exec_loop_coroutine)


def launch_args():
    """
    Parses command line arguments for launching the NeuroBehavioral Analytics Suite.

    The arguments include options for opening an existing project, creating a new project, and specifying various
    project parameters.

    Returns:
        argparse.ArgumentParser: The argument parser with the parsed command line arguments.
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
                        help='List of files containing experimental func')
    parser.add_argument('-c', '--camera_framerate',
                        help='Camera Framerate')

    return parser

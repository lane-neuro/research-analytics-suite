"""
A module for launching the Research Analytics Suite.

This module contains the main entry point for launching the Research Analytics Suite. It includes functions
for parsing command line arguments and launching the application.

Author: Lane
"""

import argparse
import asyncio

from research_analytics_suite.data_engine.Config import Config
from research_analytics_suite.data_engine.Workspace import Workspace
from research_analytics_suite.gui.GuiLauncher import GuiLauncher
from research_analytics_suite.operation_manager.OperationControl import OperationControl
from research_analytics_suite.utils.CustomLogger import CustomLogger


async def launch_ras():
    """
    Launches the Research Analytics Suite.

    This function checks the command line arguments to determine whether to create a new project or open an existing
    one. It then initializes the asyncio event loop and starts the application.

    Raises:
        AssertionError: If no active project is open.
    """
    # Parse command line arguments, if any
    args = launch_args().parse_args()
    launch_tasks = []

    # Initialize the Config and Logger
    config = Config()
    await config.initialize()

    logger = CustomLogger()
    await logger.initialize()

    operation_control = OperationControl()
    await operation_control.initialize()

    # Initialize new Workspace and Config
    _workspace = Workspace()
    await _workspace.initialize()

    # Checks args for -o '--open_project' flag.
    # If it exists, open the project from the file
    if args.open_project is None:
        logger.info('New Project Parameters Detected - Creating New Project')
        data_engine = _workspace.create_project(args.directory, args.user_name, args.subject_name,
                                                args.camera_framerate, args.file_list)
    else:
        logger.info('Project File Detected - Loading Project at: ' + args.open_project)
        data_engine = await _workspace.load_workspace(args.open_project)

    launch_tasks.append(operation_control.exec_loop())
    gui_launcher = None

    if args.gui is not None and args.gui.lower() == 'true':
        try:
            gui_launcher = GuiLauncher(data_engine=data_engine)
        except Exception as e:
            logger.error(e)
        finally:
            launch_tasks.append(gui_launcher.setup_main_window())

    logger.info("Launching RAS")

    try:
        await asyncio.gather(*launch_tasks)
    except Exception as e:
        logger.error(e)
    finally:
        logger.info("Cleaning up...")
        await _workspace.save_current_workspace()
        logger.info("Exiting Research Analytics Suite...")
        asyncio.get_event_loop().close()


def launch_args():
    """
    Parses command line arguments for launching the Research Analytics Suite.

    The arguments include options for opening an existing project, creating a new project, and specifying various
    project parameters.

    Returns:
        argparse.ArgumentParser: The argument parser with the parsed command line arguments.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('-g', '--gui', help='Launches the Research Analytics Suite GUI')
    parser.add_argument('-o', '--open_project', help='Opens an existing project from the specified file')
    parser.add_argument('-u', '--user_name', help='Name of user/experimenter')
    parser.add_argument('-d', '--directory', help='Directory where project files will be located')
    parser.add_argument('-s', '--subject_name', help='Name of the experimental subject (e.g., mouse, human, etc.)')
    parser.add_argument('-f', '--file_list', help='List of files containing experimental data')
    parser.add_argument('-c', '--camera_framerate', help='Camera Framerate')

    return parser

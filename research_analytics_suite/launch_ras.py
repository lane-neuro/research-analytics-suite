"""
A module for launching the Research Analytics Suite.

This module contains the main entry point for launching the Research Analytics Suite. It includes functions
for parsing command line arguments and launching the application.

Author: Lane
"""

import argparse
import asyncio
import os.path

from research_analytics_suite.data_engine.Config import Config
from research_analytics_suite.data_engine.Workspace import Workspace
from research_analytics_suite.gui.GuiLauncher import GuiLauncher
from research_analytics_suite.operation_manager.OperationControl import OperationControl
from research_analytics_suite.utils.CustomLogger import CustomLogger


async def launch_ras():
    """
    Launches the Research Analytics Suite.

    This function checks the command line arguments to determine whether to create a new workspace or open an existing
    one. It then initializes the asyncio event loop and starts the application.

    Raises:
        AssertionError: If no active project is open.
    """
    # Parse command line arguments, if any
    _args = launch_args().parse_args()
    _launch_tasks = []

    # Initialize the Config and Logger
    _config = Config()
    await _config.initialize()

    _logger = CustomLogger()
    await _logger.initialize()

    _operation_control = OperationControl()
    await _operation_control.initialize()

    # Initialize new Workspace and Config
    _workspace = Workspace()
    await _workspace.initialize()

    # Checks args for -o '--open_workspace' flag.
    # If it exists, open the workspace from the file
    if _args.open_workspace is None and _args.config is None:
        _logger.info('New Workspace Parameters Detected - Creating New Workspace')
        try:
            if _args.directory is None:
                _args.directory = os.path.expanduser(f"~/Research-Analytics-Suite/workspaces/")
            os.makedirs(_args.directory, exist_ok=True)

            if _args.name is None:
                _args.name = "default_workspace"
                workspace_path = os.path.join(_args.directory, _args.name)
                try:
                    os.makedirs(workspace_path, exist_ok=False)
                except FileExistsError:
                    _logger.info(f"Workspace with name '{_args.name}' already exists in directory "
                                 f"'{_args.directory}'... Finding next available workspace name...")
                    i = 1
                    while True:
                        _args.name = f"default_workspace_{i}"
                        workspace_path = os.path.join(_args.directory, _args.name)
                        try:
                            os.makedirs(workspace_path, exist_ok=False)
                            break
                        except FileExistsError:
                            i += 1

            else:
                workspace_path = os.path.join(_args.directory, _args.name)
                try:
                    os.makedirs(workspace_path, exist_ok=False)
                except FileExistsError:
                    _logger.info(f"Workspace with name '{_args.name}' already exists in directory "
                                 f"'{_args.directory}'... Finding next available workspace name...")
                    i = 1
                    while True:
                        _args.name = f"{_args.name}_{i}"
                        workspace_path = os.path.join(_args.directory, _args.name)
                        try:
                            os.makedirs(workspace_path, exist_ok=False)
                            break
                        except FileExistsError:
                            i += 1

            _logger.info('Creating New Workspace at: ' + os.path.join(_args.directory, _args.name))
            _workspace = await _workspace.create_workspace(_args.directory, _args.name)
        except Exception as e:
            _logger.error(e)
    else:
        if _args.open_workspace is not None and _args.config is None:
            _args.config = os.path.join(_args.open_workspace, 'config.json')
        elif _args.open_workspace is None and _args.config is not None:
            _args.open_workspace = os.path.dirname(_args.config)

        if not os.path.exists(_args.open_workspace):
            _logger.error(Exception(f"Workspace folder '{_args.open_workspace}' does not exist."))
            return
        _logger.info('Opening Existing Workspace at: ' + _args.open_workspace)
        _workspace = await _workspace.load_workspace(_args.open_workspace)

    _launch_tasks.append(_operation_control.exec_loop())
    _gui_launcher = None

    if _args.gui is not None and _args.gui.lower() == 'true':
        try:
            _gui_launcher = GuiLauncher()
        except Exception as e:
            _logger.error(e)
        finally:
            _launch_tasks.append(_gui_launcher.setup_main_window())

    _logger.info("Launching RAS")

    try:
        await asyncio.gather(*_launch_tasks)
    except Exception as e:
        _logger.error(e)
    finally:
        _logger.info("Cleaning up...")
        await _workspace.save_current_workspace()
        _logger.info("Exiting Research Analytics Suite...")
        asyncio.get_event_loop().close()


def launch_args():
    """
    Parses command line arguments for launching the Research Analytics Suite.

    The arguments include options for opening an existing workspace, creating a new workspace, and specifying various
    workspace parameters.

    Returns:
        argparse.ArgumentParser: The argument parser with the parsed command line arguments.
    """
    _parser = argparse.ArgumentParser()

    # GUI argument
    _parser.add_argument('-g', '--gui',
                         help='Launches the Research Analytics Suite GUI')

    # Open workspace arguments
    _parser.add_argument('-o', '--open_workspace',
                         help='Opens an existing workspace from the specified folder/directory')
    _parser.add_argument('-c', '--config',
                         help='Path to the configuration file for the workspace')

    # New workspace arguments
    _parser.add_argument('-d', '--directory',
                         help='Directory where workspace files will be located')
    _parser.add_argument('-n', '--name',
                         help='Name of the new workspace')

    return _parser

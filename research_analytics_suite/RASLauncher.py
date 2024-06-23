"""
A module for launching the Research Analytics Suite.

This module contains the main entry point for launching the Research Analytics Suite. It includes functions
for parsing command line arguments and launching the application.

Author: Lane
"""
import asyncio
import os.path

from research_analytics_suite.data_engine import MemoryManager
from research_analytics_suite.data_engine.utils.Config import Config
from research_analytics_suite.data_engine.Workspace import Workspace
from research_analytics_suite.gui.launcher.GuiLauncher import GuiLauncher
from research_analytics_suite.operation_manager.control.OperationControl import OperationControl
from research_analytics_suite.utils.CustomLogger import CustomLogger
from research_analytics_suite.utils.launch_args import get_launch_args


async def RASLauncher():
    """
    Launches the Research Analytics Suite.

    This function checks the command line arguments to determine whether to create a new workspace or open an existing
    one. It then initializes the asyncio event loop and starts the application.

    Raises:
        AssertionError: If no active project is open.
    """
    # Parse command line arguments, if any
    _args = get_launch_args().parse_args()
    _launch_tasks = []
    _gui_launcher = None

    # Initialize Logging singleton class
    _logger = CustomLogger()
    await _logger.initialize()

    # Initialize the default collection if it doesn't exist
    _memory_manager = MemoryManager()
    await _memory_manager.initialize()

    # Initialize Configuration singleton class
    _config = Config()
    await _config.initialize()

    # Initialize OperationControl singleton class
    _operation_control = OperationControl()
    await _operation_control.initialize()

    # Initialize Workspace singleton class
    _workspace = Workspace()
    await _workspace.initialize()

    # Add the operation control loop to the launch tasks
    _launch_tasks.append(_operation_control.exec_loop())

    # Checks args for -o '--open_workspace' flag and -c '--config' flag
    # If -o flag is present, but -c flag is not, set the config path to the open_workspace path
    # If -c flag is present, but -o flag is not, set the open_workspace path to the directory of the config path
    # If neither are present, create a new workspace
    if _args.open_workspace is None and _args.config is None:
        _logger.info('New Workspace Parameters Detected - Creating New Workspace')
        try:
            # Set default directory if not specified
            # TODO: Ensure to accomodate all operating systems (e.g. ~ for Unix, %UserProfile% for Windows)

            # Create the directory if it doesn't exist
            try:
                os.makedirs(_args.directory, exist_ok=True)
            except Exception as e:
                _logger.error(e)
                return

            # Set default name if not specified
            if _args.name is None:
                _args.name = "default_workspace"
                _workspace_path = os.path.join(_args.directory, _args.name)

                # Check if the workspace already exists
                try:
                    os.makedirs(_workspace_path, exist_ok=False)
                except FileExistsError:
                    _logger.info(f"Workspace with name '{_args.name}' already exists in directory "
                                 f"'{_args.directory}'... Finding next available workspace name...")

                    # Find the next available workspace name
                    i = 1
                    while True:
                        _args.name = f"{_args.name}_{i}"
                        _workspace_path = os.path.join(_args.directory, _args.name)
                        try:
                            os.makedirs(_workspace_path, exist_ok=False)
                            break
                        except FileExistsError:
                            i += 1

            # Create the new workspace based on the directory and name
            else:
                _workspace_path = os.path.join(_args.directory, _args.name)
                try:
                    os.makedirs(_workspace_path, exist_ok=False)
                except FileExistsError:
                    _logger.info(f"Workspace with name '{_args.name}' already exists in directory "
                                 f"'{_args.directory}'... Finding next available workspace name...")
                    i = 1
                    _name_base = _args.name
                    while True:
                        _name_attempt = f"{_name_base}_{i}"
                        _workspace_path = os.path.join(_args.directory, _name_attempt)
                        try:
                            os.makedirs(_workspace_path, exist_ok=False)
                            _args.name = _name_attempt
                            break
                        except FileExistsError:
                            i += 1

            _logger.info('Creating New Workspace at: ' + os.path.join(_args.directory, _args.name))
            _workspace = await _workspace.create_workspace(_args.directory, _args.name)
        except Exception as e:
            _logger.error(e)

    # If -o '--open_workspace' flag is present, open the existing workspace
    else:
        if _args.open_workspace is not None and _args.config is None:
            _args.config = os.path.join(os.path.expanduser(
                f"~\\Research-Analytics-Suite\\workspaces"),
                f"{_args.open_workspace}",
                'config.json')

        elif _args.open_workspace is None and _args.config is not None:
            _args.open_workspace = os.path.dirname(_args.config)
            if _args.open_workspace is None or _args.open_workspace == "":
                _args.open_workspace = os.path.expanduser(f"~\\Research-Analytics-Suite\\workspaces")

        if not os.path.exists(f"{_args.directory}\\{_args.open_workspace}"):
            _logger.error(Exception(
                f"Workspace folder '{_args.open_workspace}' does not exist. Creating new workspace..."))
            try:
                _workspace = await _workspace.create_workspace(_args.directory, _args.open_workspace)
            except Exception as e:
                _logger.error(e)
                return
        else:
            _logger.info('Opening Existing Workspace at:\t' + f"{_args.directory}\\{_args.open_workspace}")

            try:
                _workspace = await _workspace.load_workspace(f"{_args.directory}\\{_args.open_workspace}")
            except Exception as e:
                _logger.error(e)

    # Launch the GUI if specified
    if _args.gui is not None and _args.gui.lower() == 'true':
        try:
            _gui_launcher = GuiLauncher()
        except Exception as e:
            _logger.error(e)
        finally:
            _launch_tasks.append(_gui_launcher.setup_main_window())

    _logger.info("Launching RAS")

    # Run the event loop
    try:
        await asyncio.gather(*_launch_tasks)
    except Exception as e:
        _logger.error(e)
    finally:
        _logger.info("Saving Workspace...")
        await _workspace.save_current_workspace()
        _logger.info("Exiting Research Analytics Suite...")
        asyncio.get_event_loop().close()

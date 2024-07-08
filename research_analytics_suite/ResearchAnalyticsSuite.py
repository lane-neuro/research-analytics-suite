"""
Research Analytics Suite (RAS) - ResearchAnalyticsSuite.py

This module contains the ResearchAnalyticsSuite class which initiates the suite and sets up the necessary parameters. It also
contains the main function which creates an instance of the ResearchAnalyticsSuite class and runs it. The suite can be
launched with or without a GUI. The suite can also be launched with a new workspace or an existing workspace.

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
import os
import sys
import nest_asyncio
from research_analytics_suite.utils import CustomLogger
from research_analytics_suite.data_engine.memory import MemoryManager
from research_analytics_suite.library_manifest import LibraryManifest
from research_analytics_suite.utils import Config
from research_analytics_suite.data_engine import Workspace
from research_analytics_suite.gui.launcher import GuiLauncher
from research_analytics_suite.operation_manager.control.OperationControl import OperationControl


class ResearchAnalyticsSuite:
    """
    The Research Analytics Suite class is responsible for initializing and launching the suite. It sets up the necessary
    components and parameters for the suite to run. The suite can be launched with or without a GUI, and with a new or
    existing workspace.

    Methods:
        - launch: Initializes and launches the suite.
    """
    def __init__(self):
        self._logger = CustomLogger()
        self._memory_manager = MemoryManager()
        self._config = Config()
        self._operation_control = OperationControl()
        self._library_manifest = LibraryManifest()
        self._workspace = Workspace()

        self._launch_tasks = []

    def _parse_launch_args(self):
        """
        Parses command line arguments for launching the suite.
        """
        _parser = argparse.ArgumentParser()

        # GUI argument
        _parser.add_argument('-g', '--gui',
                             help='Launches the Research Analytics Suite GUI',
                             choices=['true', 'false'], default='True')

        # Open workspace arguments
        _parser.add_argument('-o', '--open_workspace',
                             help='Opens an existing workspace from the specified folder/directory')
        _parser.add_argument('-c', '--config',
                             help='Path to the configuration file for the workspace')

        # New workspace arguments
        _parser.add_argument('-d', '--directory',
                             help='Directory where workspace files will be located',
                             default=os.path.expanduser(f"~/Research-Analytics-Suite/workspaces/"))
        _parser.add_argument('-n', '--name',
                             help='Name of the new workspace')

        self._args = _parser.parse_args()

    async def _initialize_components(self):
        """
        Initializes the components of the Research Analytics Suite.
        """
        await self._logger.initialize()
        await self._memory_manager.initialize()
        await self._config.initialize()
        await self._operation_control.initialize()
        await self._library_manifest.initialize()
        await self._workspace.initialize()

        # Adds the OperationControl.exec_loop() [RAS primary event handler] to the launch tasks
        self._launch_tasks.append(self._operation_control.exec_loop())

    async def _setup_workspace(self):
        """
        Sets up the workspace for the suite.
            - If no workspace is specified, a new workspace is created.
            - If an existing workspace is specified, the workspace is opened.
        """
        if self._args.open_workspace is None and self._args.config is None:
            await self.create_new_workspace()
        else:
            await self.open_existing_workspace()

    async def create_new_workspace(self):
        try:
            os.makedirs(self._args.directory, exist_ok=True)
        except Exception as e:
            self._logger.error(e, self.__class__.__name__)
            return

        if self._args.name is None:
            self._args.name = "default_workspace"
            workspace_path = os.path.normpath(os.path.join(self._args.directory, self._args.name))
            await self.ensure_unique_workspace(workspace_path)
        else:
            workspace_path = os.path.normpath(os.path.join(self._args.directory, self._args.name))
            await self.ensure_unique_workspace(workspace_path)

        self._logger.info('Creating New Workspace at: ' + workspace_path)
        await self._workspace.create_workspace(self._args.directory, self._args.name)

    async def ensure_unique_workspace(self, workspace_path):
        """
        Ensures the workspace directory is unique by appending a number if necessary.
        """
        base_path = workspace_path
        counter = 1
        while True:
            try:
                os.makedirs(workspace_path, exist_ok=False)
                break
            except FileExistsError:
                self._logger.debug(f"Workspace {workspace_path} already exists. Trying a new name.")
                workspace_path = f"{base_path}_{counter}"
                counter += 1
        return workspace_path

    async def open_existing_workspace(self):
        """
        Opens an existing workspace. If the workspace does not exist, a new workspace is created.
        """
        if self._args.open_workspace is not None and self._args.config is None:
            self._args.config = os.path.normpath(os.path.join(os.path.expanduser("~"), "Research-Analytics-Suite",
                                                              "workspaces", f"{self._args.open_workspace}",
                                                              'config.json'))

        elif self._args.open_workspace is None and self._args.config is not None:
            self._args.open_workspace = os.path.dirname(self._args.config)
            if self._args.open_workspace is None or self._args.open_workspace == "":
                self._args.open_workspace = os.path.normpath(os.path.join(os.path.expanduser("~"),
                                                                          "Research-Analytics-Suite", "workspaces"))

        if not os.path.exists(os.path.normpath(os.path.join(f"{self._args.directory}", self._args.open_workspace))):
            self._logger.error(
                NotADirectoryError(f"Workspace folder '{self._args.open_workspace}' does not exist. Creating new "
                                   f"workspace..."), self.__class__.__name__)
            await self.create_new_workspace()
            return

        _workspace_path = os.path.normpath(os.path.join(self._args.directory, self._args.open_workspace))
        self._logger.info(f'Opening Existing Workspace at:\t{_workspace_path}')
        try:
            await self._workspace.load_workspace(_workspace_path)
        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    async def _launch(self):
        """
        Initializes and launches the Research Analytics Suite.

        Raises:
            Exception: If an error occurs during initialization or launching.
        """
        await self._initialize_components()
        await self._setup_workspace()

        if self._args.gui.lower() == 'true':
            try:
                gui_launcher = GuiLauncher()
                self._launch_tasks.append(gui_launcher.setup_main_window())
            except Exception as e:
                self._logger.error(e, self.__class__.__name__)

        try:
            await asyncio.gather(*self._launch_tasks)
        except Exception as e:
            self._logger.error(e, self.__class__.__name__)
        finally:
            self._logger.info("Saving Workspace...")
            await self._workspace.save_current_workspace()
            self._logger.info("Exiting Research Analytics Suite...")
            asyncio.get_event_loop().close()

    def run(self):
        """
        Runs the Research Analytics Suite.

        Raises:
            KeyboardInterrupt: If the suite is interrupted by a keyboard interrupt.
            Exception: If a fatal error occurs.
        """
        try:
            # Allow nested asyncio loops for Jupyter Notebook compatibility
            nest_asyncio.apply()

            # Parse launch arguments and launch the suite
            self._parse_launch_args()
            asyncio.run(self._launch())
            asyncio.get_event_loop().run_forever()

        except KeyboardInterrupt:
            print('Exiting Research Analytics Suite..')
        except Exception as e:
            print(f"Fatal error occurred: {e}")
        finally:
            print("Cleaning up..")
            asyncio.get_event_loop().close()
            sys.exit(0)


def main(): # pragma: no cover
    suite = ResearchAnalyticsSuite()
    suite.run()


if __name__ == '__main__':  # pragma: no cover
    main()

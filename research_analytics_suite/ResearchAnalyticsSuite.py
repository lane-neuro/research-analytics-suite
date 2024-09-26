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
    The Research Analytics Suite class is responsible for initializing and launching the suite.
    It sets up the necessary components and parameters for the suite to run. The suite can be
    launched with or without a GUI, and with a new or existing workspace.

    Methods:
        - launch: Initializes and launches the suite.
    """

    def __init__(self):
        from research_analytics_suite.commands import CommandRegistry
        from research_analytics_suite.hardware_manager.HardwareInstaller import HardwareInstaller
        from research_analytics_suite.hardware_manager.interface.InterfaceManager import InterfaceManager
        self._config = Config()
        self._logger = CustomLogger()
        self._workspace = Workspace()
        self._memory_manager = MemoryManager()
        self._hardware_installer = HardwareInstaller()
        self._interface_manager = InterfaceManager()
        self._library_manifest = LibraryManifest()
        self._command_registry = CommandRegistry()
        self._operation_control = OperationControl()

        self._launch_tasks = []

        self._args = None

    def _parse_launch_args(self):
        """
        Parses command line arguments for launching the suite.
        """
        parser = argparse.ArgumentParser()

        parser.add_argument('-g', '--gui', help='Launches the Research Analytics Suite GUI',
                            choices=['true', 'false'], default='true')
        parser.add_argument('-o', '--open_workspace',
                            help='Opens or creates a workspace at the specified folder/directory.',
                            default=os.path.expanduser(f"~/Research-Analytics-Suite/workspaces/default_workspace"))

        self._args = parser.parse_args()

    async def _initialize_components(self):
        """
        Initializes the components of the Research Analytics Suite.
        """
        await self._config.initialize()
        await self._logger.initialize()
        await self._memory_manager.initialize()
        await self._setup_workspace()

        await self._operation_control.initialize()
        self._launch_tasks.append(self._operation_control.exec_loop())

        await self._library_manifest.initialize()
        await self._command_registry.initialize()
        await self._hardware_installer.interface_manager.detect_interfaces()

    async def _setup_workspace(self):
        """
        Sets up the workspace for the suite. Creates a new workspace if the specified one doesn't exist.
        """
        workspace_path = os.path.normpath(self._args.open_workspace)
        if not os.path.exists(workspace_path):
            self._logger.info(f"Workspace '{workspace_path}' does not exist. Creating a new workspace...")
            os.makedirs(workspace_path, exist_ok=True)
            workspace_name = os.path.basename(workspace_path)
            parent_path = os.path.dirname(workspace_path)
            await self._workspace.create_workspace(parent_path, workspace_name)
        else:
            self._logger.info(f"Opening existing workspace at '{workspace_path}'")
            await self._workspace.load_workspace(workspace_path)

    async def _launch(self):
        """
        Initializes and launches the Research Analytics Suite.
        """
        await self._initialize_components()

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
        """
        try:
            nest_asyncio.apply()
            self._parse_launch_args()
            asyncio.run(self._launch())
        except KeyboardInterrupt:
            print('Exiting Research Analytics Suite..')
        except Exception as e:
            self._logger.error(Exception(f"Fatal error occurred: {e}"), self.__class__.__name__)
            print(f"Fatal error occurred: {e}")
        finally:
            print("Cleaning up..")
            asyncio.get_event_loop().close()
            sys.exit(0)


def main():  # pragma: no cover
    suite = ResearchAnalyticsSuite()
    suite.run()


if __name__ == '__main__':  # pragma: no cover
    main()

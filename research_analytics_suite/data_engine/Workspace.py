"""
Workspace Module

This module defines the Workspace class, which manages multiple data engines and provides advanced data operations,
including caching, dependency management, and handling live data inputs within the Research Analytics Suite.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from __future__ import annotations
import asyncio
import os
from collections import defaultdict

from research_analytics_suite.commands import link_class_commands, command
from research_analytics_suite.utils.Config import Config
from research_analytics_suite.data_engine.engine.UnifiedDataEngine import UnifiedDataEngine
from research_analytics_suite.utils.CustomLogger import CustomLogger
from research_analytics_suite.data_engine.memory import MemoryManager


@link_class_commands
class Workspace:
    """
    A class to manage multiple data engines, allowing flexible interaction with specific datasets.
    """
    _instance: Workspace = None
    _lock: asyncio.Lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initializes the Workspace instance.
        """
        if not hasattr(self, '_initialized'):
            self._logger = CustomLogger()
            self._config = Config()
            from research_analytics_suite.library_manifest.LibraryManifest import LibraryManifest
            self._library_manifest = LibraryManifest()
            self._memory_manager = MemoryManager()

            self._data_engines = {}
            self._dependencies = defaultdict(list)

            self._distributed = None
            self._db_path = None

            self._initialized = False

    async def initialize(self, config: Config = None) -> None:
        """
        Initializes the workspace. This method is called automatically when the workspace is first accessed.

        Args:
            config (Config): The configuration to use for the workspace
        """
        if not self._initialized:
            async with Workspace._lock:
                if not self._initialized:
                    if config:
                        self._config = config
                    self._data_engines = {}
                    self._dependencies = defaultdict(list)

                    self._logger.debug("Workspace initialized successfully")
                    self._initialized = True

    @command
    def add_data_engine(self, data_engine: UnifiedDataEngine) -> None:
        """
        Adds a data engine and its metadata to the workspace.

        Args:
            data_engine (UnifiedDataEngine): The data engine to add.
        """
        self._data_engines[data_engine.runtime_id] = data_engine
        self._logger.debug(f"Data engine '{self._data_engines[data_engine.runtime_id].short_id}' added to workspace")

    @command
    def remove_data_engine(self, name: str) -> None:
        """
        Removes a data engine and its metadata from the workspace.

        Args:
            name (str): The name of the data engine to remove.
        """
        if name in self._data_engines:
            self._data_engines[name].close()
            del self._data_engines[name]
        if name in self._dependencies:
            del self._dependencies[name]
        for deps in self._dependencies.values():
            if name in deps:
                deps.remove(name)

        self._logger.debug(f"Data engine '{name}' removed from workspace")

    @command
    def get_data_engine(self, name: str) -> UnifiedDataEngine or None:
        """
        Retrieves a data engine by name.

        Args:
            name (str): The name of the data engine to retrieve.

        Returns:
            UnifiedDataEngine: The requested data engine.
        """
        return self._data_engines.get(name, None)

    @command
    def get_default_data_engine(self) -> UnifiedDataEngine or None:
        """
        Retrieves the default data engine.

        Returns:
            UnifiedDataEngine: The default data engine.
        """
        return next(iter(self._data_engines.values()), None)

    @command
    async def create_workspace(self, workspace_directory: str, workspace_name: str) -> Workspace:
        """
        Creates a new workspace with the specified parameters.

        Args:
            workspace_directory (str): The directory where Workspace files will be located.
            workspace_name (str): The name of the Workspace.

        Returns:
            Workspace: The newly created workspace
        """
        self._config.BASE_DIR = os.path.normpath(os.path.join(workspace_directory, "../"))
        self._config.WORKSPACE_NAME = workspace_name
        data_engine = UnifiedDataEngine()
        self.add_data_engine(data_engine=data_engine)
        self._logger.info(f"Workspace created at {os.path.normpath(workspace_directory)}")
        try:
            new_workspace = await self.save_current_workspace()
            return await self.load_workspace(os.path.normpath(os.path.join(f"{new_workspace}", 'config.json')))
        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    @command
    async def save_current_workspace(self) -> str:
        """
        Saves the current workspace to the directory specified in the configuration.

        Returns:
            The path to the saved workspace directory.
        """
        try:
            os.makedirs(
                os.path.join(self._config.BASE_DIR, "workspaces", self._config.WORKSPACE_NAME), exist_ok=True)
            os.makedirs(
                os.path.join(self._config.BASE_DIR, "workspaces", self._config.WORKSPACE_NAME, self._config.DATA_DIR),
                exist_ok=True)
            os.makedirs(
                os.path.join(self._config.BASE_DIR, "workspaces", self._config.WORKSPACE_NAME, self._config.LOG_DIR),
                exist_ok=True)
            os.makedirs(
                os.path.join(self._config.BASE_DIR, "workspaces", self._config.WORKSPACE_NAME,
                             self._config.WORKSPACE_DIR), exist_ok=True)
            os.makedirs(
                os.path.join(self._config.BASE_DIR, "workspaces", self._config.WORKSPACE_NAME,
                             self._config.WORKSPACE_OPERATIONS_DIR), exist_ok=True)
            os.makedirs(
                os.path.join(self._config.BASE_DIR, "workspaces", self._config.WORKSPACE_NAME, self._config.BACKUP_DIR),
                exist_ok=True)
            os.makedirs(
                os.path.join(self._config.BASE_DIR, "workspaces", self._config.WORKSPACE_NAME, self._config.ENGINE_DIR),
                exist_ok=True)

            for runtime_id, data_engine in self._data_engines.items():
                engine_path = os.path.join(self._config.BASE_DIR, "workspaces", self._config.WORKSPACE_NAME,
                                           self._config.ENGINE_DIR,
                                           data_engine.engine_id)
                os.makedirs(engine_path, exist_ok=True)
                await data_engine.save_engine(
                    os.path.join(self._config.BASE_DIR, "workspaces", self._config.WORKSPACE_NAME))

            await self.save_memory_manager(os.path.normpath(
                os.path.join(self._config.BASE_DIR, "workspaces", self._config.WORKSPACE_NAME, 'user_variables.db')))
            config_path = os.path.normpath(
                os.path.join(self._config.BASE_DIR, "workspaces", self._config.WORKSPACE_NAME, 'config.json'))
            await self._config.save_to_file(config_path)
            _path = os.path.normpath(os.path.join(self._config.BASE_DIR, "workspaces", self._config.WORKSPACE_NAME))
            return f"{_path}"

        except Exception as e:
            self._logger.error(Exception(f"Failed to save current workspace: {e}"), self.__class__.__name__)
            return ""

    @command
    async def load_workspace(self, workspace_path: str) -> Workspace or None:
        """
        Loads a workspace from the specified directory.

        Args:
            workspace_path (str): The path to the workspace directory.

        Returns:
            Workspace: The loaded workspace.
        """
        try:
            if not os.path.exists(workspace_path):
                self._logger.error(FileNotFoundError(f"Workspace directory not found: {workspace_path}"),
                                   self.__class__.__name__)
                return None

            if workspace_path.endswith('config.json'):
                workspace_path = os.path.dirname(workspace_path)

            # Clear existing data
            self._clear_existing_data()

            self._config = await self._config.reload_from_file(os.path.join(workspace_path, 'config.json'))

            if not self._config:
                self._logger.error(ValueError(f"Failed to load configuration from {workspace_path}"),
                                   self.__class__.__name__)
                return None

            self.__init__()
            await self.initialize(config=self._config)

            engine_dir = os.path.join(workspace_path, self._config.ENGINE_DIR)
            for engine_id in os.listdir(f"{engine_dir}"):
                data_engine = await UnifiedDataEngine.load_engine(engine_dir, engine_id)
                self.add_data_engine(data_engine)

            await self._library_manifest.load_user_library()
            await self.restore_memory_manager(os.path.join(workspace_path, self._config.DATA_DIR, 'memory_manager.db'))
            self._logger.info(f"Workspace loaded from {workspace_path}")
            return self

        except Exception as e:
            self._logger.error(Exception(f"Failed to load workspace: {e}"), self.__class__.__name__)

    def _clear_existing_data(self) -> None:
        """
        Clears existing data in the workspace to ensure a clean load.
        """
        self._data_engines = {}
        self._dependencies = defaultdict(list)
        self._initialized = False

    @command
    async def save_memory_manager(self, file_path: str) -> None:  # pragma: no cover
        """
        Saves the user variables database to the specified file.

        Args:
            file_path (str): The path to the save file.
        """
        ...

    @command
    async def restore_memory_manager(self, file_path: str) -> None:  # pragma: no cover
        """
        Restores a serialized MemorySlotCollection object from the specified save file.

        Args:
            file_path (str): The path to the save file.
        """
        ...

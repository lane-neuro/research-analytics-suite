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
from pathlib import Path
from typing import Optional

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
    _active_workspace_path: Optional[Path] = None

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
        self._logger.debug(f"Data engine '{data_engine.short_id}' added to workspace")

    @command
    def remove_data_engine(self, runtime_id: str) -> None:
        """
        Removes a data engine and its metadata from the workspace.

        Args:
            runtime_id (str): The name of the data engine to remove.
        """
        self._data_engines.pop(runtime_id, None)

        # Remove from dependency lists
        if runtime_id in self._dependencies:
            del self._dependencies[runtime_id]
        for deps in self._dependencies.values():
            if runtime_id in deps:
                deps.remove(runtime_id)

        self._logger.debug(f"Data engine '{runtime_id}' removed from workspace")

    @command
    def get_data_engine(self, runtime_id: str) -> Optional[UnifiedDataEngine]:
        """
        Retrieves a data engine by it's runtime ID.

        Args:
            runtime_id (str): The runtime ID of the data engine to retrieve.

        Returns:
            UnifiedDataEngine: The requested data engine.
        """
        return self._data_engines.get(runtime_id)

    @command
    def get_default_data_engine(self) -> Optional[UnifiedDataEngine]:
        """
        Retrieves the default data engine.

        Returns:
            UnifiedDataEngine: The default data engine.
        """
        return next(iter(self._data_engines.values()), None)

    @command
    async def create_workspace(self, workspace_directory: str, workspace_name: str, overwrite: bool = False) -> "Workspace":
        """
        Create a workspace on disk, then 'switches' to it.

        Args:
            workspace_directory (str): The directory where Workspace files will be located.
            workspace_name (str): The name of the Workspace.
            overwrite (bool): Whether to overwrite an existing workspace. Defaults to False.

        Returns:
            Workspace: The newly created workspace
        """
        base_dir = Path(workspace_directory).resolve().parent
        # Build a prospective config dict based on the current Config snapshot
        cfg_dict = self._config.copy_with(
            BASE_DIR=str(base_dir),
            WORKSPACE_NAME=workspace_name,
        )

        work_root = Path(cfg_dict["BASE_DIR"]) / "workspaces" / cfg_dict["WORKSPACE_NAME"]
        if work_root.exists() and not overwrite:
            raise FileExistsError(f"Workspace '{workspace_name}' already exists at {work_root}")

        # Create directory layout from the staged dict
        for folder in (
                cfg_dict.get("DATA_DIR", "data"),
                cfg_dict.get("LOG_DIR", "logs"),
                cfg_dict.get("WORKSPACE_DIR", "workspace"),
                os.path.normpath(os.path.join(cfg_dict.get("WORKSPACE_DIR", "workspace"), "operations")),
                cfg_dict.get("BACKUP_DIR", "backup"),
                cfg_dict.get("EXPORT_DIR", "export"),
                cfg_dict.get("ENGINE_DIR", "engine"),
        ):
            (work_root / folder).mkdir(parents=True, exist_ok=True)

        # Persist the staged config to disk
        config_path = work_root / "config.json"
        await Config.save_dict_to_file(str(config_path), cfg_dict)

        try:
            default_engine = UnifiedDataEngine()
            await default_engine.save_engine(str(work_root))
        except Exception as e:
            self._logger.warning(f"Failed to create default engine for new workspace: {e}")

        # Switch workspaces
        await self.switch_to_workspace(str(config_path))
        self._logger.info(f"Workspace created at {work_root}")
        return self

    @command
    async def save_current_workspace(self) -> str:
        """
        Save current workspace to disk using self._config. Assumes an active workspace.
        """
        try:
            base_dir = Path(self._config.BASE_DIR)
            work_root = base_dir / "workspaces" / self._config.WORKSPACE_NAME

            # Ensure expected directories exist
            for d in (
                self._config.DATA_DIR, self._config.LOG_DIR, self._config.WORKSPACE_DIR,
                self._config.WORKSPACE_OPERATIONS_DIR, self._config.BACKUP_DIR,
                self._config.EXPORT_DIR, self._config.ENGINE_DIR
            ):
                (work_root / d).mkdir(parents=True, exist_ok=True)

            # Persist engines
            for _, data_engine in self._data_engines.items():
                await data_engine.save_engine(work_root)

            # Persist config
            await self._config.save_to_file(str(work_root / 'config.json'))
            return str(work_root)

        except Exception as e:
            self._logger.error(Exception(f"Failed to save current workspace: {e}"), self.__class__.__name__)
            return ""

    @command
    async def load_workspace(self, workspace_path: str) -> Optional["Workspace"]:
        """
        Load an existing workspace from disk.

        Args:
            workspace_path (str): Path to the workspace directory or its config.json file.

        Returns:
            Workspace: The loaded workspace instance, or None if loading failed.
        """
        try:
            wp = Path(workspace_path)
            if not wp.exists():
                self._logger.error(FileNotFoundError(f"Workspace path not found: {workspace_path}"),
                                   self.__class__.__name__)
                return None

            # Allow passing either .../config.json or the workspace dir
            if wp.name == 'config.json':
                work_root = wp.parent
            else:
                work_root = wp

            # Reset in-memory state safely
            self._reset_workspace()

            # Load a *fresh* Config from disk
            cfg_path = work_root / 'config.json'
            if not cfg_path.exists():
                self._logger.error(ValueError(f"Missing config.json in {work_root}"),
                                   self.__class__.__name__)
                return None

            self._config = await self._config.reload_from_file(str(cfg_path))
            if not self._config:
                self._logger.error(ValueError(f"Failed to load configuration from {cfg_path}"),
                                   self.__class__.__name__)
                return None


            # Initialize logger
            if not hasattr(self, "_logger"):
                self._logger = CustomLogger()
            await self._logger.initialize()
            self._logger.reconfigure_for_workspace(self._config)

            from research_analytics_suite.library_manifest.LibraryManifest import LibraryManifest
            self._library_manifest = LibraryManifest()

            self._logger.debug(f"Loading memory manager for workspace at {work_root}")

            from research_analytics_suite.data_engine.memory import MemoryManager as MM
            self._memory_manager = MM()  # get the singleton (same instance)
            await self._memory_manager.initialize()
            self._memory_manager.set_config(self._config)  # ensure it points at the *current* Config
            mm_db_path = str(work_root / self._config.DATA_DIR / "memory_manager.db")
            await self._memory_manager.rebind_to_db(mm_db_path)

            await self.initialize(config=self._config)

            # Load engines from disk
            engine_dir = work_root / self._config.ENGINE_DIR
            if engine_dir.exists():
                for engine_id in os.listdir(str(engine_dir)):
                    data_engine = await UnifiedDataEngine.load_engine(str(engine_dir), engine_id)
                    self.add_data_engine(data_engine)

            await self._library_manifest.load_user_library()

            self._active_workspace_path = work_root
            self._logger.info(f"Workspace loaded from {work_root}")
            return self

        except Exception as e:
            self._logger.error(Exception(f"Failed to load workspace: {e}"), self.__class__.__name__)
            return None

    @command
    async def switch_to_workspace(self, config_or_dir: str) -> "Workspace":
        """
        Close the current workspace (if any) and then load the target workspace.
        """
        await self.close()
        return await self.load_workspace(config_or_dir)

    def _reset_workspace(self) -> None:
        """
        Clears existing data in the workspace to ensure a clean load.
        """
        self._data_engines = {}
        self._dependencies = defaultdict(list)
        self._initialized = False

    async def close(self) -> None:
        """
        Gracefully close the current workspace: stop engines, flush state, and
        release resources. After this, the Workspace is 'inactive' until initialize/load is called.
        """
        try:
            # Close engines
            for eng in list(self._data_engines.values()):
                try:
                    await eng.save_engine(self._active_workspace_path)
                except Exception as e:
                    self._logger.warning(f"Failed to save data engine {getattr(eng,'short_id', '')}: {e}")

            self._data_engines.clear()
            self._dependencies.clear()
            self._active_workspace_path = None
            self._initialized = False
            self._logger.debug("Workspace closed.")

            # Detach file handlers for the old workspace so they don't keep writing
            if hasattr(self, "_logger") and self._logger:
                self._logger.clear_file_handlers()

        except Exception as e:
            self._logger.error(Exception(f"Failed during workspace close: {e}"), self.__class__.__name__)

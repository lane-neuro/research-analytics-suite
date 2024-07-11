"""
Workspace Module

This module defines the Workspace class, which manages multiple data engines and provides advanced data operations,
including caching, dependency management, and handling live data inputs within the Research Analytics Suite.

Author: Lane
"""
import asyncio
import os
import json
import uuid
from typing import Tuple, Optional, Any

import aiofiles
from collections import defaultdict

from research_analytics_suite.commands import register_commands, command
from research_analytics_suite.library_manifest import LibraryManifest
from research_analytics_suite.utils.Config import Config
from research_analytics_suite.data_engine.memory.DataCache import DataCache
from research_analytics_suite.data_engine.engine.DataEngineOptimized import DataEngineOptimized
from research_analytics_suite.data_engine.engine.UnifiedDataEngine import UnifiedDataEngine
from research_analytics_suite.utils.CustomLogger import CustomLogger
from research_analytics_suite.data_engine.memory import MemoryManager
from research_analytics_suite.data_engine.memory.MemorySlot import MemorySlot
from research_analytics_suite.data_engine.memory.MemorySlotCollection import MemorySlotCollection


@register_commands
class Workspace:
    """
    A class to manage multiple data engines, allowing flexible interaction with specific datasets.
    """
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """
        Initializes the Workspace instance.
        """
        if not hasattr(self, '_initialized'):
            self._logger = CustomLogger()
            self._config = Config()
            self._library_manifest = LibraryManifest()
            self._memory_manager = MemoryManager()
            self._data_cache = DataCache()

            self._data_engines = {}
            self._dependencies = defaultdict(list)

            self._distributed = None
            self._storage_type = "memory"
            self._db_path = None

            self._initialized = False

    async def initialize(self, config=None):
        """
        Initializes the workspace.

        This method is called automatically when the workspace is first accessed.
        """
        if not self._initialized:
            async with Workspace._lock:
                if not self._initialized:
                    if config:
                        self._config = config
                    self._data_engines = dict()
                    self._dependencies = defaultdict(list)

                    self._logger.debug("Workspace initialized successfully")
                    self._initialized = True

    @command
    def add_data_engine(self, data_engine):
        """
        Adds a data engine and its metadata to the workspace.

        Args:
            data_engine (DataEngineOptimized): The data engine to add.
        """
        self._data_engines[data_engine.runtime_id] = data_engine
        self._logger.debug(f"Data engine '{self._data_engines[data_engine.runtime_id].short_id}' added to workspace")

    @command
    def remove_data_engine(self, name):
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
    def get_data_engine(self, name):
        """
        Retrieves a data engine by name.

        Args:
            name (str): The name of the data engine to retrieve.

        Returns:
            DataEngineOptimized: The requested data engine.
        """
        return self._data_engines.get(name, None)

    @command
    def get_default_data_engine(self):
        """
        Retrieves the default data engine.

        Returns:
            DataEngineOptimized: The default data engine.
        """
        return next(iter(self._data_engines.values()), None)

    @command
    async def create_workspace(self, workspace_directory, workspace_name):
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
        data_engine = DataEngineOptimized()
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
    async def load_workspace(self, workspace_path) -> 'Workspace' or None:
        """
        Loads a workspace from the specified directory.

        Args:
            workspace_path: The path to the workspace directory.

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
            await self.restore_memory_manager(os.path.join(workspace_path, 'user_variables.db'))
            self._logger.info(f"Workspace loaded from {workspace_path}")
            return self

        except Exception as e:
            self._logger.error(Exception(f"Failed to load workspace: {e}"), self.__class__.__name__)

    def _clear_existing_data(self):
        """
        Clears existing data in the workspace to ensure a clean load.
        """
        self._data_engines = {}
        self._dependencies = defaultdict(list)
        self._initialized = False

    # Methods to interact with MemorySlotCollections
    @command
    def add_memory_collection(self, collection: MemorySlotCollection):
        """
        Adds a new MemorySlotCollection to the workspace.

        Args:
            collection (MemorySlotCollection): The collection to add.
        """
        try:
            self._memory_manager.add_collection(collection=collection)
        except Exception as e:
            self._logger.error(Exception(f"Failed to add MemorySlotCollection: {e}"), self.__class__.__name__)

    @command
    async def get_memory_collection(self, collection_id: str) -> MemorySlotCollection or None:
        """
        Retrieves a MemorySlotCollection by its ID from the workspace.

        Args:
            collection_id (str): The ID of the collection to retrieve.

        Returns:
            MemorySlotCollection: The retrieved collection.
        """
        try:
            return self._memory_manager.get_collection(collection_id=collection_id)
        except Exception as e:
            self._logger.error(Exception(f"Failed to get MemorySlotCollection: {e}"), self.__class__.__name__)
            return None

    @command
    async def remove_memory_collection(self, collection_id: str):
        """
        Removes a MemorySlotCollection by its ID from the workspace.

        Args:
            collection_id (str): The ID of the collection to remove.
        """
        try:
            await self._memory_manager.remove_collection(collection_id=collection_id)
        except Exception as e:
            self._logger.error(Exception(f"Failed to remove MemorySlotCollection: {e}"), self.__class__.__name__)

    @command
    async def list_memory_collections(self) -> dict:
        """
        Lists all MemorySlotCollections in the workspace.

        Returns:
            dict: A dictionary of MemorySlotCollections.
        """
        try:
            return await self._memory_manager.list_collections()
        except Exception as e:
            self._logger.error(Exception(f"Failed to list MemorySlotCollections: {e}"), self.__class__.__name__)
            return {}

    @command
    async def add_variable_to_collection(self, collection_id: str, name: str, value: Any, data_type: type,
                                         memory_slot_id: Optional[str] = None) -> Tuple[str, dict] or None:
        collection_id = collection_id or self._memory_manager.get_default_collection_id()
        try:
            collection = self._memory_manager.get_collection(collection_id)
            if collection:
                if memory_slot_id:
                    slot = collection.get_slot(memory_slot_id)
                    if not slot:
                        self._logger.error(ValueError(f"MemorySlot with ID {memory_slot_id} not found"),
                                           self.__class__.__name__)
                        return None
                else:
                    slot = MemorySlot(memory_id=str(uuid.uuid4()), name=name, operation_required=True, data={})
                    collection.add_slot(slot)

                await slot.set_data_by_key(name, value, data_type)
                return slot.memory_id, {name: value}
            else:
                self._logger.error(ValueError(f"Collection with ID {collection_id} not found"), self.__class__.__name__)
                return None
        except Exception as e:
            self._logger.error(Exception(f"Failed to add variable '{name}' to collection '{collection_id}': {e}"),
                               self.__class__.__name__)
            return None

    @command
    async def get_variable_from_collection(self, collection_id: str, name: str,
                                           memory_slot_id: Optional[str] = None) -> Any:
        collection_id = collection_id or self._memory_manager.get_default_collection_id()
        try:
            collection = self._memory_manager.get_collection(collection_id)
            if collection:
                if memory_slot_id:
                    slot = collection.get_slot(memory_slot_id)
                    if slot:
                        return await slot.get_data_by_key(name)
                    self._logger.error(KeyError(f"Variable '{name}' not found in MemorySlot '{memory_slot_id}'"),
                                       self.__class__.__name__)
                    return
                else:
                    if collection.list_slots():
                        for slot in collection.list_slots():
                            if await slot.has_key(name):
                                return await slot.get_data_by_key(name)
                    else:
                        self._logger.error(KeyError(f"Variable '{name}' not found in collection '{collection_id}'"),
                                           self.__class__.__name__)
                        return
            else:
                self._logger.error(ValueError(f"Collection with ID {collection_id} not found"), self.__class__.__name__)
                return
        except Exception as e:
            self._logger.error(Exception(f"Failed to get variable '{name}' from collection '{collection_id}': {e}"),
                               self.__class__.__name__)

    @command
    async def remove_variable_from_collection(self, collection_id: str, name: str,
                                              memory_slot_id: Optional[str] = None):
        collection_id = collection_id or self._memory_manager.get_default_collection_id()
        try:
            collection = self._memory_manager.get_collection(collection_id)
            if collection:
                if memory_slot_id:
                    slot = collection.get_slot(memory_slot_id)
                    if slot:
                        await slot.remove_data_by_key(name)
                        return
                    self._logger.error(KeyError(f"Variable '{name}' not found in MemorySlot '{memory_slot_id}'"),
                                       self.__class__.__name__)
                    return
                else:
                    if collection.list_slots():
                        for slot in collection.list_slots():
                            if await slot.has_key(name):
                                await slot.remove_data_by_key(name)
                                return
                            else:
                                self._logger.error(KeyError(f"Variable '{name}' not found in collection "
                                                            f"'{collection_id}', MemorySlot '{slot.memory_id}'"),
                                                   self.__class__.__name__)
                                return
                    else:
                        self._logger.error(KeyError(f"Variable '{name}' not found in collection '{collection_id}'"),
                                           self.__class__.__name__)
                        return
            else:
                self._logger.error(ValueError(f"Collection with ID {collection_id} not found"), self.__class__.__name__)
                return
        except Exception as e:
            self._logger.error(Exception(f"Failed to remove variable '{name}' from collection '{collection_id}': {e}"),
                               self.__class__.__name__)

    @command
    async def save_memory_manager(self, file_path):
        """
        Saves the user variables database to the specified file.

        Args:
            file_path: The path to the save file.
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            collections = await self._memory_manager.list_collections()

            async with aiofiles.open(file_path, 'w') as dst:
                collections_data = {cid: await col.to_dict() for cid, col in collections.items()}

                # Remove any slots that start with 'gui_' or 'sys_'
                collections_data = {
                    k: v for k, v in collections_data.items() if not (v['name'].startswith('gui_') or
                                                                      v['name'].startswith('sys_'))
                }

                # Remove any modules that are not serializable
                collections_data = remove_non_serializable(collections_data)

                await dst.write(json.dumps(collections_data, indent=4))

            self._logger.info(f"Memory Management saved to {file_path}")

        except Exception as e:
            self._logger.error(Exception(f"Failed to save Memory Management: {e}"), self.__class__.__name__)

    @command
    async def restore_memory_manager(self, file_path):
        """
        Restores a serialized MemorySlotCollection object from the specified save file.

        Args:
            file_path: The path to the save file.
        """
        try:
            if not os.path.exists(file_path):
                self._logger.error(FileNotFoundError(f"Memory bank file not found: {file_path}"),
                                   self.__class__.__name__)
                return

            async with aiofiles.open(file_path, 'r') as src:
                collections_data = json.loads(await src.read())

                for collection_id, collection_dict in collections_data.items():
                    self.add_memory_collection(await MemorySlotCollection.from_dict(collection_dict))

            self._logger.info(f"Memory restored from {file_path}")
        except Exception as e:
            self._logger.error(Exception(f"Failed to restore memory bank: {e}"), self.__class__.__name__)


@command
def remove_non_serializable(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            if isinstance(v, dict):  # Each value should be a dictionary
                slots = v.get('slots')  # Get the list of slots
                for slot in slots if slots else {}:
                    slot_data = slot.get('data')  # Get the data dictionary for each slot
                    for name, value in list(slot_data.items()):  # Create a copy of items
                        if (isinstance(value, tuple) and not is_serializable(value[1])) or not is_serializable(value):
                            del slot_data[name]
    elif isinstance(obj, list):
        return [remove_non_serializable(item) for item in obj if is_serializable(item)]
    else:
        return obj if is_serializable(obj) else None
    return obj


@command
def is_serializable(obj):
    try:
        json.dumps(obj, indent=4)
        return True
    except (TypeError, OverflowError):
        return False

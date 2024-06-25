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
from typing import LiteralString, Tuple, Optional, Any

import aiofiles
from collections import defaultdict
from research_analytics_suite.data_engine.utils.Config import Config
from research_analytics_suite.data_engine.utils.DataCache import DataCache
from research_analytics_suite.data_engine.engine.DataEngineOptimized import DataEngineOptimized
from research_analytics_suite.data_engine.engine.UnifiedDataEngine import UnifiedDataEngine
from research_analytics_suite.utils.CustomLogger import CustomLogger
from research_analytics_suite.data_engine.memory import MemoryManager, SQLiteStorage, MemoryStorage
from research_analytics_suite.data_engine.memory.MemorySlot import MemorySlot
from research_analytics_suite.data_engine.memory.MemorySlotCollection import MemorySlotCollection


class Workspace:
    """
    A class to manage multiple data engines, allowing flexible interaction with specific datasets.
    """
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, distributed=False, storage_type='memory', db_path=None):
        """
        Initializes the Workspace instance.

        Args:
            distributed (bool): Whether to use distributed computing. Default is False.
            storage_type (str): The type of storage to use ('sqlite' or 'memory'). Default is 'memory'.
            db_path (str): The path to the SQLite database file (required if storage_type is 'sqlite').
        """
        if not hasattr(self, '_initialized'):
            self._logger = CustomLogger()
            self._config = Config()
            self._memory_manager = MemoryManager()

            self._data_engines = None
            self._dependencies = None
            self._data_cache = None

            self._distributed = distributed
            self._storage_type = storage_type
            self._db_path = db_path

            self._storage = None

            self._initialized = False

    async def initialize(self):
        """
        Initializes the workspace.

        This method is called automatically when the workspace is first accessed.
        """
        if not self._initialized:
            async with Workspace._lock:
                if not self._initialized:
                    self._data_engines = dict()
                    self._dependencies = defaultdict(list)
                    self._data_cache = DataCache()

                    if self._db_path is None:
                        self._db_path = os.path.join(self._config.BASE_DIR, self._config.WORKSPACE_NAME,
                                                     'user_variables.db')
                        self._logger.info(f"Using default database path: {self._db_path}")
                    if self._storage_type == 'sqlite':
                        self._storage = SQLiteStorage(db_path=self._db_path)
                    elif self._storage_type == 'memory':
                        self._storage = MemoryStorage(db_path=self._db_path)
                        await self._storage.setup()
                    else:
                        self._logger.error(ValueError(f"Unsupported storage type: {self._storage_type}"), self)

                    self._logger.info("Workspace initialized successfully")
                    self._initialized = True

    def add_data_engine(self, data_engine):
        """
        Adds a data engine and its metadata to the workspace.

        Args:
            data_engine (DataEngineOptimized): The data engine to add.
        """
        self._data_engines[data_engine.runtime_id] = data_engine
        self._logger.info(f"Data engine '{self._data_engines[data_engine.runtime_id].short_id}' added to workspace")

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

        self._logger.info(f"Data engine '{name}' removed from workspace")

    def get_data_engine(self, name):
        """
        Retrieves a data engine by name.

        Args:
            name (str): The name of the data engine to retrieve.

        Returns:
            DataEngineOptimized: The requested data engine.
        """
        return self._data_engines.get(name, None)

    async def create_workspace(self, workspace_directory, workspace_name):
        """
        Creates a new workspace with the specified parameters.

        Args:
            workspace_directory (str): The directory where Workspace files will be located.
            workspace_name (str): The name of the Workspace.

        Returns:
            Workspace: The newly created workspace
        """
        self._config.BASE_DIR = workspace_directory
        self._config.WORKSPACE_NAME = workspace_name
        data_engine = DataEngineOptimized()
        self.add_data_engine(data_engine=data_engine)
        self._logger.info(f"Workspace created at {workspace_directory}")
        new_workspace = await self.save_current_workspace()
        new_workspace = os.path.join(f"{new_workspace}", 'config.json')
        return await self.load_workspace(new_workspace)

    async def save_current_workspace(self) -> LiteralString | str | bytes:
        """
        Saves the current workspace to the directory specified in the configuration.

        Returns:
            The path to the saved workspace directory.
        """
        try:
            os.makedirs(os.path.join(self._config.BASE_DIR, self._config.WORKSPACE_NAME), exist_ok=True)
            os.makedirs(os.path.join(self._config.BASE_DIR, self._config.WORKSPACE_NAME, self._config.DATA_DIR),
                        exist_ok=True)
            os.makedirs(os.path.join(self._config.BASE_DIR, self._config.WORKSPACE_NAME, self._config.LOG_DIR),
                        exist_ok=True)
            os.makedirs(os.path.join(self._config.BASE_DIR, self._config.WORKSPACE_NAME, self._config.WORKSPACE_DIR),
                        exist_ok=True)
            os.makedirs(
                os.path.join(self._config.BASE_DIR, self._config.WORKSPACE_NAME, self._config.WORKSPACE_OPERATIONS_DIR),
                exist_ok=True)
            os.makedirs(os.path.join(self._config.BASE_DIR, self._config.WORKSPACE_NAME, self._config.BACKUP_DIR),
                        exist_ok=True)
            os.makedirs(os.path.join(self._config.BASE_DIR, self._config.WORKSPACE_NAME, self._config.ENGINE_DIR),
                        exist_ok=True)

            for runtime_id, data_engine in self._data_engines.items():
                engine_path = os.path.join(self._config.BASE_DIR, self._config.WORKSPACE_NAME, self._config.ENGINE_DIR,
                                           data_engine.engine_id)
                os.makedirs(engine_path, exist_ok=True)
                await data_engine.save_engine(os.path.join(self._config.BASE_DIR, self._config.WORKSPACE_NAME))

            await self.save_memory_manager(
                os.path.join(self._config.BASE_DIR, self._config.WORKSPACE_NAME, 'user_variables.db'))
            config_path = os.path.join(self._config.BASE_DIR, self._config.WORKSPACE_NAME, 'config.json')
            await self._config.save_to_file(config_path)
            self._logger.info(f"Workspace folder saved in directory:\t{self._config.BASE_DIR}")
            return os.path.join(self._config.BASE_DIR, self._config.WORKSPACE_NAME)

        except Exception as e:
            self._logger.error(Exception(f"Failed to save current workspace: {e}"), self)

    async def load_workspace(self, workspace_path) -> 'Workspace':
        """
        Loads a workspace from the specified directory.

        Args:
            workspace_path: The path to the workspace directory.

        Returns:
            Workspace: The loaded workspace.
        """
        try:
            if not os.path.exists(workspace_path):
                if os.path.exists(os.path.join(workspace_path, 'config.json')):
                    workspace_path = os.path.join(workspace_path, 'config.json')
                else:
                    raise FileNotFoundError(f"Workspace directory not found: {workspace_path}")

            self._config = await self._config.reload_from_file(workspace_path)

            if workspace_path.endswith('config.json'):
                workspace_path = os.path.dirname(workspace_path)

            workspace = Workspace(self._config.DISTRIBUTED)

            for engine_id in os.listdir(os.path.join(workspace_path, f"{self._config.ENGINE_DIR}")):
                data_engine = await UnifiedDataEngine.load_engine(workspace_path, engine_id)
                workspace.add_data_engine(data_engine)

            await self.restore_memory_manager(os.path.join(workspace_path, 'user_variables.db'))
            return workspace
        except Exception as e:
            self._logger.error(Exception(f"Failed to load workspace: {e}"), self)

    def _get_config_settings(self):
        """
        Retrieves the current self._configuration settings.

        Returns:
            str: The self._configuration settings in JSON format.
        """
        return json.dumps({
            'workspace_name': self._config.WORKSPACE_NAME,
            'base_dir': self._config.BASE_DIR,
            'data_dir': self._config.DATA_DIR,
            'log_dir': self._config.LOG_DIR,
            'workspace_dir': self._config.WORKSPACE_DIR,
            'backup_dir': self._config.BACKUP_DIR,
            'engine_dir': self._config.ENGINE_DIR,

            'memory_limit': self._config.MEMORY_LIMIT,

            'log_level': self._config.LOG_LEVEL,
            'log_file': self._config.LOG_FILE,
            'log_rotation': self._config.LOG_ROTATION,
            'log_retention': self._config.LOG_RETENTION,

            'cache_size': self._config.CACHE_SIZE,
            'num_threads': self._config.NUM_THREADS,

            'db_host': self._config.DB_HOST,
            'db_port': self._config.DB_PORT,
            'db_user': self._config.DB_USER,
            'db_password': self._config.DB_PASSWORD,
            'db_name': self._config.DB_NAME,

            'api_base_url': self._config.API_BASE_URL,
            'api_key': self._config.API_KEY,

            'email_host': self._config.EMAIL_HOST,
            'email_port': self._config.EMAIL_PORT,
            'email_user': self._config.EMAIL_USER,
            'email_password': self._config.EMAIL_PASSWORD,
            'email_use_tls': self._config.EMAIL_USE_TLS,
            'email_use_ssl': self._config.EMAIL_USE_SSL,

            'theme': self._config.THEME,
            'language': self._config.LANGUAGE,

            'encryption_key': self._config.ENCRYPTION_KEY,
            'authentication_method': self._config.AUTHENTICATION_METHOD,

            'batch_size': self._config.BATCH_SIZE,
            'transformations': self._config.TRANSFORMATIONS,

            'scheduler_interval': self._config.SCHEDULER_INTERVAL,
        }, indent=4)

    # Methods to interact with MemorySlotCollections
    def add_memory_collection(self, collection: MemorySlotCollection):
        """
        Adds a new MemorySlotCollection to the workspace.

        Args:
            collection (MemorySlotCollection): The collection to add.
        """
        try:
            self._memory_manager.add_collection(collection=collection)
        except Exception as e:
            self._logger.error(Exception(f"Failed to add MemorySlotCollection: {e}"), self)

    async def get_memory_collection(self, collection_id: str) -> MemorySlotCollection:
        """
        Retrieves a MemorySlotCollection by its ID from the workspace.

        Args:
            collection_id (str): The ID of the collection to retrieve.

        Returns:
            MemorySlotCollection: The retrieved collection.
        """
        try:
            return await self._memory_manager.get_collection(collection_id=collection_id)
        except Exception as e:
            self._logger.error(Exception(f"Failed to get MemorySlotCollection: {e}"), self)

    async def remove_memory_collection(self, collection_id: str):
        """
        Removes a MemorySlotCollection by its ID from the workspace.

        Args:
            collection_id (str): The ID of the collection to remove.
        """
        try:
            await self._memory_manager.remove_collection(collection_id=collection_id)
        except Exception as e:
            self._logger.error(Exception(f"Failed to remove MemorySlotCollection: {e}"), self)

    async def list_memory_collections(self) -> dict:
        """
        Lists all MemorySlotCollections in the workspace.

        Returns:
            dict: A dictionary of MemorySlotCollections.
        """
        try:
            return await self._memory_manager.list_collections()
        except Exception as e:
            self._logger.error(Exception(f"Failed to list MemorySlotCollections: {e}"), self)

    async def add_variable_to_collection(self, collection_id: str, name: str, value: Any,
                                         memory_slot_id: Optional[str] = None) -> Tuple[str, dict]:
        collection_id = collection_id or await self._memory_manager.get_default_collection_id()
        try:
            collection = await self._memory_manager.get_collection(collection_id)
            if collection:
                if memory_slot_id:
                    slot = collection.get_slot(memory_slot_id)
                    if not slot:
                        raise ValueError(f"MemorySlot with ID {memory_slot_id} not found")
                else:
                    slot = MemorySlot(memory_id=str(uuid.uuid4()), name=name, operation_required=True, data={})
                    await collection.add_slot(slot)

                await slot.set_data_by_key(name, value)
                return slot.memory_id, {name: value}
            else:
                raise ValueError(f"Collection with ID {collection_id} not found")
        except Exception as e:
            self._logger.error(Exception(f"Failed to add variable '{name}' to collection '{collection_id}': {e}"), self)

    async def get_variable_from_collection(self, collection_id: str, name: str,
                                           memory_slot_id: Optional[str] = None) -> Any:
        collection_id = collection_id or await self._memory_manager.get_default_collection_id()
        try:
            collection = await self._memory_manager.get_collection(collection_id)
            if collection:
                if memory_slot_id:
                    slot = collection.get_slot(memory_slot_id)
                    if slot:
                        return await slot.get_data_by_key(name)
                    raise KeyError(f"Variable '{name}' not found in MemorySlot '{memory_slot_id}'")
                else:
                    if collection.list_slots():
                        for slot in collection.list_slots():
                            if await slot.has_key(name):
                                return await slot.get_data_by_key(name)
                    else:
                        raise KeyError(f"Variable '{name}' not found in collection '{collection_id}'")
            else:
                raise ValueError(f"Collection with ID {collection_id} not found")
        except Exception as e:
            self._logger.error(Exception(f"Failed to get variable '{name}' from collection '{collection_id}': {e}"),
                               self)

    async def remove_variable_from_collection(self, collection_id: str, name: str,
                                              memory_slot_id: Optional[str] = None):
        collection_id = collection_id or await self._memory_manager.get_default_collection_id()
        try:
            collection = await self._memory_manager.get_collection(collection_id)
            if collection:
                if memory_slot_id:
                    slot = collection.get_slot(memory_slot_id)
                    if slot:
                        await slot.remove_data_by_key(name)
                        return
                    raise KeyError(f"Variable '{name}' not found in MemorySlot '{memory_slot_id}'")
                else:
                    if collection.list_slots():
                        for slot in collection.list_slots():
                            if await slot.has_key(name):
                                await slot.remove_data_by_key(name)
                                return
                            else:
                                raise KeyError(f"Variable '{name}' not found in collection '{collection_id}'"
                                               f", MemorySlot '{slot.memory_id}'")
                    else:
                        raise KeyError(f"Variable '{name}' not found in collection '{collection_id}'")
            else:
                raise ValueError(f"Collection with ID {collection_id} not found")
        except Exception as e:
            self._logger.error(Exception(f"Failed to remove variable '{name}' from collection '{collection_id}': {e}"),
                               self)

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

                # Remove any slots that are not serializable
                collections_data = remove_non_serializable(collections_data)

                # Remove any slots that start with 'gui_' or 'sys_'
                collections_data = {
                    k: v for k, v in collections_data.items() if not v['name'].startswith('gui_') and
                    not v['name'].startswith('sys_')
                }

                await dst.write(json.dumps(collections_data))

            self._logger.info(f"Memory Management saved to {file_path}")

        except Exception as e:
            self._logger.error(Exception(f"Failed to save Memory Management: {e}"), self)

    async def restore_memory_manager(self, file_path):
        """
        Restores a serialized MemorySlotCollection object from the specified save file.

        Args:
            file_path: The path to the save file.
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Memory bank file not found: {file_path}")

            async with aiofiles.open(file_path, 'r') as src:
                collections_data = json.loads(await src.read())

                for collection_id, collection_dict in collections_data.items():
                    await MemorySlotCollection.from_dict(collection_dict)

            self._logger.info(f"Memory restored from {file_path}")
        except Exception as e:
            self._logger.error(Exception(f"Failed to restore memory bank: {e}"), self)


def remove_non_serializable(obj):
    if isinstance(obj, dict):
        return {k: remove_non_serializable(v) for k, v in obj.items() if is_serializable(v)}
    elif isinstance(obj, list):
        return [remove_non_serializable(item) for item in obj if is_serializable(item)]
    else:
        return obj if is_serializable(obj) else None


def is_serializable(obj):
    try:
        json.dumps(obj)
        return True
    except (TypeError, OverflowError):
        return False

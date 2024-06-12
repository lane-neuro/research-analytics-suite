"""
Workspace Module

This module defines the Workspace class, which manages multiple data engines and provides advanced data operations,
including caching, dependency management, and handling live data inputs within the Research Analytics Suite.

Author: Lane
"""

import os
import json
import aiofiles
from collections import defaultdict
from research_analytics_suite.data_engine.Config import Config
from research_analytics_suite.data_engine.DataCache import DataCache
from research_analytics_suite.data_engine.DataEngineOptimized import DataEngineOptimized
from research_analytics_suite.data_engine.UnifiedDataEngine import UnifiedDataEngine
from research_analytics_suite.utils.CustomLogger import CustomLogger
from research_analytics_suite.data_engine.variable_management import UserVariablesManager, SQLiteStorage, MemoryStorage


class Workspace:
    """
    A class to manage multiple data engines, allowing flexible interaction with specific datasets.
    """

    def __init__(self, distributed=False, storage_type='memory', db_path=None):
        """
        Initializes the Workspace instance.

        Args:
            distributed (bool): Whether to use distributed computing. Default is False.
            storage_type (str): The type of storage to use ('sqlite' or 'memory'). Default is 'memory'.
            db_path (str): The path to the SQLite database file (required if storage_type is 'sqlite').
        """
        self._data_engines = {}
        self._dependencies = defaultdict(list)
        self._data_cache = DataCache()
        self._distributed = distributed
        self._logger = CustomLogger()
        self._config = Config()

        storage = None
        if storage_type == 'sqlite':
            if db_path is None:
                db_path = os.path.join(self._config.BASE_DIR, 'user_variables.db')
            storage = SQLiteStorage(db_path)
        elif storage_type == 'memory':
            storage = MemoryStorage()
        else:
            self._logger.error(ValueError(f"Unsupported storage type: {storage_type}"), self)

        self._user_variables = UserVariablesManager(storage)
        self._logger.info("Workspace initialized successfully")

    def add_data_engine(self, data_engine):
        """
        Adds a data engine and its metadata to the workspace.

        Args:
            data_engine (DataEngineOptimized): The data engine to add.
        """
        self._data_engines[data_engine.engine_id] = data_engine
        self._logger.info(f"Data engine '{data_engine.engine_id}' added to workspace")

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

    def create_project(self, project_directory, user_name, data_name, framerate, data_path):
        """
        Creates a new project with the specified parameters.

        Args:
            project_directory (str): The directory where project files will be located.
            user_name (str): The name of the user/experimenter.
            data_name (str): The name of the data.
            framerate (int): The framerate of the data.
            data_path (str): The path to the data files.

        Returns:
            DataEngineOptimized: The initialized data engine for the new project.
        """
        data_engine = DataEngineOptimized(workspace=self)
        self.add_data_engine(data_engine=data_engine)
        self._logger.info(f"Project created at {project_directory}")
        return data_engine

    async def save_current_workspace(self):
        try:
            os.makedirs(self._config.BASE_DIR, exist_ok=True)
            os.makedirs(self._config.DATA_DIR, exist_ok=True)
            os.makedirs(self._config.LOG_DIR, exist_ok=True)
            os.makedirs(self._config.WORKSPACE_DIR, exist_ok=True)
            os.makedirs(self._config.BACKUP_DIR, exist_ok=True)
            os.makedirs(self._config.ENGINE_DIR, exist_ok=True)

            for engine_id, data_engine in self._data_engines.items():
                engine_path = os.path.join(self._config.ENGINE_DIR, f'{engine_id}')
                os.makedirs(engine_path, exist_ok=True)
                await data_engine.save_engine(self._config.BASE_DIR)

            config_path = os.path.join(self._config.BASE_DIR, 'config.json')
            async with aiofiles.open(config_path, 'w') as config_file:
                await config_file.write(self._get_config_settings())

            self._logger.info(f"Workspace saved at {self._config.BASE_DIR}")
        except Exception as e:
            self._logger.error(Exception(f"Failed to save current workspace: {e}"), self)

    async def load_workspace(self, workspace_path) -> 'Workspace':
        try:
            async with aiofiles.open(os.path.join(workspace_path), 'r') as config_file:
                config = json.loads(await config_file.read())

            workspace_path = os.path.dirname(workspace_path)
            workspace = Workspace(config.get('distributed', False))

            for engine_id in os.listdir(os.path.join(workspace_path, 'engines')):
                data_engine = await UnifiedDataEngine.load_engine(workspace_path, engine_id)
                workspace.add_data_engine(data_engine)

            workspace._logger.info("Workspace loaded successfully")
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

    # Methods to interact with UserVariables
    async def add_user_variable(self, name, value):
        try:
            await self._user_variables.add_variable(name, value)
        except Exception as e:
            self._logger.error(Exception(f"Failed to add user variable '{name}': {e}"), self)

    async def get_user_variable(self, name):
        try:
            return await self._user_variables.get_variable(name)
        except Exception as e:
            self._logger.error(Exception(f"Failed to get user variable '{name}': {e}"), self)

    async def remove_user_variable(self, name):
        try:
            await self._user_variables.remove_variable(name)
        except Exception as e:
            self._logger.error(Exception(f"Failed to remove user variable '{name}': {e}"), self)

    async def list_user_variables(self):
        try:
            return await self._user_variables.list_variables()
        except Exception as e:
            self._logger.error(Exception(f"Failed to list user variables: {e}"), self)

    # Methods to backup and restore UserVariables
    async def backup_user_variables(self, backup_path):
        """
        Backups the user variables database to the specified path.

        Args:
            backup_path (str): The path to save the backup file.
        """
        try:
            async with aiofiles.open(self._user_variables.storage.db_path, 'rb') as src, aiofiles.open(backup_path, 'wb') as dst:
                await dst.write(await src.read())
            self._logger.info(f"User variables backed up to {backup_path}")
        except Exception as e:
            self._logger.error(Exception(f"Failed to backup user variables: {e}"), self)

    async def restore_user_variables(self, backup_path):
        """
        Restores the user variables database from the specified backup file.

        Args:
            backup_path (str): The path of the backup file to restore from.
        """
        try:
            async with (aiofiles.open(backup_path, 'rb') as src,
                        aiofiles.open(self._user_variables.storage.db_path, 'wb') as dst):
                await dst.write(await src.read())
            self._logger.info(f"User variables restored from {backup_path}")
        except Exception as e:
            self._logger.error(Exception(f"Failed to restore user variables: {e}"), self)

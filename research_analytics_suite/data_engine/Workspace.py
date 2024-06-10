"""
Workspace Module

This module defines the Workspace class, which manages multiple data engines and provides advanced data operations,
including caching, dependency management, and handling live data inputs within the research analytics suite.

Author: Lane
"""

import json
import os
from collections import defaultdict

from research_analytics_suite.data_engine.Config import Config
from research_analytics_suite.data_engine.DataCache import DataCache
from research_analytics_suite.data_engine.DataEngineOptimized import DataEngineOptimized
from research_analytics_suite.data_engine.UnifiedDataEngine import UnifiedDataEngine
from research_analytics_suite.utils.CustomLogger import CustomLogger


class Workspace:
    """
    A class to manage multiple data engines, allowing flexible interaction with specific datasets.
    """

    def __init__(self, distributed=False):
        """
        Initializes the Workspace instance.

        Args:
            distributed (bool): Whether to use distributed computing. Default is False.
        """
        self._data_engines = {}
        self._dependencies = defaultdict(list)
        self._data_cache = DataCache()
        self._distributed = distributed
        self._logger = CustomLogger()
        self._config = Config()

    def add_data_engine(self, data_engine):
        """
        Adds a data engine and its metadata to the workspace.

        Args:
            data_engine (DataEngineOptimized): The data engine to add.
        """
        self._data_engines[data_engine.engine_id] = data_engine

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
        return data_engine

    def save_current_workspace(self):
        os.makedirs(self._config.BASE_DIR, exist_ok=True)
        os.makedirs(self._config.DATA_DIR, exist_ok=True)
        os.makedirs(self._config.LOG_DIR, exist_ok=True)
        os.makedirs(self._config.WORKSPACE_DIR, exist_ok=True)
        os.makedirs(self._config.BACKUP_DIR, exist_ok=True)
        os.makedirs(self._config.ENGINE_DIR, exist_ok=True)

        for engine_id, data_engine in self._data_engines.items():
            engine_path = os.path.join(self._config.ENGINE_DIR, f'{engine_id}')
            os.makedirs(engine_path, exist_ok=True)
            data_engine.save_engine(self._config.BASE_DIR)

        config_path = os.path.join(self._config.BASE_DIR, 'config.json')
        with open(config_path, 'w') as config_file:
            config_file.write(self._get_config_settings())

        self._logger.info(f"Workspace saved at {self._config.BASE_DIR}")

    @staticmethod
    def load_workspace(workspace_path):
        with open(os.path.join(workspace_path), 'r') as config_file:
            config = json.load(config_file)

        workspace_path = os.path.dirname(workspace_path)
        workspace = Workspace(config.get('distributed', False))

        for engine_id in os.listdir(os.path.join(workspace_path, 'engines')):
            data_engine = UnifiedDataEngine.load_engine(workspace_path, engine_id)
            workspace.add_data_engine(data_engine)

        workspace._logger.info("Workspace loaded successfully")
        return workspace

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

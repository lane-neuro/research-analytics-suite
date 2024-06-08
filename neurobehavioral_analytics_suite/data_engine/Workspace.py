"""
Workspace Module

This module defines the Workspace class, which manages multiple data engines and provides advanced data operations,
including caching, dependency management, and handling live data inputs within the neurobehavioral analytics suite.

Author: Lane
"""

import os
import json
from collections import defaultdict
from neurobehavioral_analytics_suite.data_engine.Config import Config
from neurobehavioral_analytics_suite.data_engine.DataCache import DataCache
from neurobehavioral_analytics_suite.data_engine.UnifiedDataEngine import UnifiedDataEngine
from neurobehavioral_analytics_suite.utils.CustomLogger import CustomLogger
from neurobehavioral_analytics_suite.data_engine.DataEngineOptimized import DataEngineOptimized
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler


class Workspace:
    """
    A class to manage multiple data engines, allowing flexible interaction with specific datasets.
    """

    def __init__(self, logger: CustomLogger, error_handler: ErrorHandler, distributed=False):
        """
        Initializes the Workspace instance.

        Args:
            logger (CustomLogger): CustomLogger for logging information and errors.
            distributed (bool): Whether to use distributed computing. Default is False.
        """
        self._data_engines = {}
        self._dependencies = defaultdict(list)
        self._data_cache = DataCache()
        self._distributed = distributed
        self.logger = logger
        self._error_handler = error_handler

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
        data_engine = DataEngineOptimized(logger=self.logger, workspace=self)
        self.add_data_engine(data_engine=data_engine)
        return data_engine

    def save_current_workspace(self):
        os.makedirs(Config.BASE_DIR, exist_ok=True)
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        os.makedirs(Config.LOG_DIR, exist_ok=True)
        os.makedirs(Config.WORKSPACE_DIR, exist_ok=True)
        os.makedirs(Config.BACKUP_DIR, exist_ok=True)
        os.makedirs(Config.ENGINE_DIR, exist_ok=True)

        for engine_id, data_engine in self._data_engines.items():
            engine_path = os.path.join(Config.ENGINE_DIR, f'{engine_id}')
            os.makedirs(engine_path, exist_ok=True)
            data_engine.save_engine(Config.BASE_DIR)

        config_path = os.path.join(Config.BASE_DIR, 'config.json')
        with open(config_path, 'w') as config_file:
            config_file.write(self._get_config_settings())

        self.logger.info(f"Workspace saved at {Config.BASE_DIR}")

    @staticmethod
    def load_workspace(workspace_path):
        with open(os.path.join(workspace_path), 'r') as config_file:
            config = json.load(config_file)

        workspace_path = os.path.dirname(workspace_path)

        logger = CustomLogger()
        error_handler = ErrorHandler()
        workspace = Workspace(logger, error_handler, config.get('distributed', False))

        for engine_id in os.listdir(os.path.join(workspace_path, 'engines')):
            data_engine = UnifiedDataEngine.load_engine(workspace_path, engine_id)
            workspace.add_data_engine(data_engine)

        workspace.logger.info("Workspace loaded successfully")
        return workspace

    def _get_config_settings(self):
        """
        Retrieves the current configuration settings.

        Returns:
            str: The configuration settings in JSON format.
        """
        return json.dumps({
            'workspace_name': Config.WORKSPACE_NAME,
            'base_dir': Config.BASE_DIR,
            'data_dir': Config.DATA_DIR,
            'log_dir': Config.LOG_DIR,
            'workspace_dir': Config.WORKSPACE_DIR,
            'backup_dir': Config.BACKUP_DIR,
            'engine_dir': Config.ENGINE_DIR,

            'memory_limit': Config.MEMORY_LIMIT,

            'log_level': Config.LOG_LEVEL,
            'log_file': Config.LOG_FILE,
            'log_rotation': Config.LOG_ROTATION,
            'log_retention': Config.LOG_RETENTION,

            'cache_size': Config.CACHE_SIZE,
            'num_threads': Config.NUM_THREADS,

            'db_host': Config.DB_HOST,
            'db_port': Config.DB_PORT,
            'db_user': Config.DB_USER,
            'db_password': Config.DB_PASSWORD,
            'db_name': Config.DB_NAME,

            'api_base_url': Config.API_BASE_URL,
            'api_key': Config.API_KEY,

            'email_host': Config.EMAIL_HOST,
            'email_port': Config.EMAIL_PORT,
            'email_user': Config.EMAIL_USER,
            'email_password': Config.EMAIL_PASSWORD,
            'email_use_tls': Config.EMAIL_USE_TLS,
            'email_use_ssl': Config.EMAIL_USE_SSL,

            'theme': Config.THEME,
            'language': Config.LANGUAGE,

            'encryption_key': Config.ENCRYPTION_KEY,
            'authentication_method': Config.AUTHENTICATION_METHOD,

            'batch_size': Config.BATCH_SIZE,
            'transformations': Config.TRANSFORMATIONS,

            'scheduler_interval': Config.SCHEDULER_INTERVAL,
        }, indent=4)

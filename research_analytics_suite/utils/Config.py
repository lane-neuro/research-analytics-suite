"""
Configuration Module

This module defines the configuration settings for the Research Analytics Suite. It includes settings for data
paths, memory limits, logging, and other necessary parameters.

Author: Lane
"""
from __future__ import annotations
import asyncio
import json
import os
import aiofiles
import psutil

from research_analytics_suite.commands import command, link_class_commands


@link_class_commands
class Config:
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs) -> Config:
        """
        Creates a new instance of the Config class if one does not already exist.

        Returns:
            Config: The Config instance.
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initializes the Config class with NoneType attributes."""
        if not hasattr(self, '_initialized'):
            self.WORKSPACE_NAME = None
            self.BASE_DIR = None
            self.DATA_DIR = None
            self.LOG_DIR = None
            self.WORKSPACE_DIR = None
            self.WORKSPACE_OPERATIONS_DIR = None
            self.BACKUP_DIR = None
            self.EXPORT_DIR = None
            self.ENGINE_DIR = None
            self.CACHE_DIR = None
            self.DISTRIBUTED = None
            self.MEMORY_LIMIT = None
            self.DEBUG_CONSOLE = None
            self.LOG_FILE = None
            self.LOG_ROTATION = None
            self.LOG_RETENTION = None
            self.CACHE_SIZE = None
            self.NUM_THREADS = None
            self.DB_HOST = None
            self.DB_PORT = None
            self.DB_USER = None
            self.DB_PASSWORD = None
            self.DB_NAME = None
            self.API_BASE_URL = None
            self.API_KEY = None
            self.EMAIL_HOST = None
            self.EMAIL_PORT = None
            self.EMAIL_USER = None
            self.EMAIL_PASSWORD = None
            self.EMAIL_USE_TLS = None
            self.EMAIL_USE_SSL = None
            self.THEME = None
            self.LANGUAGE = None
            self.ENCRYPTION_KEY = None
            self.AUTHENTICATION_METHOD = None
            self.BATCH_SIZE = None
            self.TRANSFORMATIONS = None
            self.SCHEDULER_INTERVAL = None

            self._initialized = False

    async def initialize(self):
        """Initializes the configuration settings."""
        if not self._initialized:
            async with Config._lock:
                if not self._initialized:
                    self.reset_to_defaults()
                    self._initialized = True

    @command
    def reset_to_defaults(self):
        """Resets the configuration settings to their default values."""
        # Workspace settings
        self.WORKSPACE_NAME = 'default_workspace'
        self.BASE_DIR = os.path.normpath(os.path.abspath(
            os.path.join(os.path.expanduser('~'), 'Research-Analytics-Suite')))

        # Paths
        self.DATA_DIR = 'data'
        self.LOG_DIR = 'logs'
        self.WORKSPACE_DIR = 'workspace'
        self.WORKSPACE_OPERATIONS_DIR = os.path.normpath(os.path.join(self.WORKSPACE_DIR, 'operations'))
        self.BACKUP_DIR = 'backup'
        self.EXPORT_DIR = 'export'
        self.ENGINE_DIR = 'engine'
        self.CACHE_DIR = 'cache'

        # Memory settings
        self.MEMORY_LIMIT = psutil.virtual_memory().total * 0.5  # 50% of available memory

        # Logging settings
        self.DEBUG_CONSOLE = False
        self.LOG_ROTATION = 1  # Rotate logs every week
        self.LOG_RETENTION = 4  # Retain logs for 4 weeks

        # Data engine settings
        self.DISTRIBUTED = True  # Use distributed memory management by default
        self.CACHE_SIZE = 2e9  # 2GB cache size by default
        self.NUM_THREADS = 4  # Number of threads for processing

        # Database settings
        self.DB_HOST = 'localhost'
        self.DB_PORT = 5432
        self.DB_USER = 'user'
        self.DB_PASSWORD = 'password'
        self.DB_NAME = 'database'

        # API settings
        self.API_BASE_URL = 'https://api.example.com'
        self.API_KEY = 'your_api_key_here'

        # Notification settings
        self.EMAIL_HOST = 'smtp.example.com'
        self.EMAIL_PORT = 587
        self.EMAIL_USER = 'user@example.com'
        self.EMAIL_PASSWORD = 'password'
        self.EMAIL_USE_TLS = True
        self.EMAIL_USE_SSL = False

        # UI settings
        self.THEME = 'light'  # Options: 'light', 'dark'
        self.LANGUAGE = 'en'  # Default language

        # Security settings
        self.ENCRYPTION_KEY = 'your_encryption_key_here'
        self.AUTHENTICATION_METHOD = 'token'  # Options: 'token', 'oauth', 'basic'

        # Performance settings
        self.BATCH_SIZE = 100  # Default batch size for processing

        # Data transformation settings
        self.TRANSFORMATIONS = {
            'normalize': True,
            'standardize': False,
            'remove_outliers': True
        }

        # Scheduler settings
        self.SCHEDULER_INTERVAL = 'daily'  # Options: 'hourly', 'daily', 'weekly'

    @command
    async def update_setting(self, key: str, value: any) -> None:
        """
        Updates a configuration setting with a new value.

        Args:
            key (str): The configuration setting to update.
            value: The new value for the configuration setting.
        """
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise AttributeError(f"Config has no attribute '{key}'")

    async def reload(self, new_config) -> Config:
        """
        Reloads the configuration settings from a dictionary.

        Args:
            new_config (dict): The new configuration settings.

        Returns:
            Config: The updated configuration settings.
        """
        from research_analytics_suite.utils import CustomLogger
        custom_logger = CustomLogger()
        custom_logger.info("Reloading configuration settings...")

        for key, value in new_config.items() if isinstance(new_config, dict) else {}:
            await self.update_setting(key, value)

        custom_logger.info("Configuration settings reloaded.")
        custom_logger.debug(f"New configuration settings: {new_config}")
        custom_logger.add_file_handlers()
        return self

    @command
    async def reload_from_file(self, file_path: str) -> Config:
        """
        Reloads the configuration settings from a JSON file.

        Args:
            file_path (str): The path to the configuration file.

        Returns:
            Config: The updated configuration settings.
        """
        # Check if the file is a configuration file
        if not file_path.endswith('.json'):
            file_path = os.path.normpath(os.path.join(file_path, 'config.json'))

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        async with aiofiles.open(file_path, 'r') as f:
            try:
                return await self.reload(json.loads(await f.read()))
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON format in configuration file: {file_path}")

    @command
    async def save_to_file(self, file_path) -> None:
        """
        Saves the configuration settings to a JSON file.

        Args:
            file_path (str): The path to save the configuration file.
        """
        async with aiofiles.open(file_path, 'w') as f:
            _copy = self.__dict__.copy()
            del _copy['_initialized']
            try:
                await f.write(json.dumps(_copy, indent=4))
            except Exception as e:
                raise e

    def repr_path(self, folder_name: str) -> str:
        """
        Returns the absolute path for a given folder name within the workspace.

        Args:
            folder_name (str): The name of the folder.

        Returns:
            str: The absolute path to the folder.
        """
        if not self.WORKSPACE_DIR:
            raise ValueError("WORKSPACE_DIR is not set. Please initialize the configuration first.")
        return os.path.normpath(os.path.join(self.BASE_DIR, 'workspaces', self.WORKSPACE_NAME, folder_name))

"""
Configuration Module

This module defines the configuration settings for the NeuroBehavioral Analytics Suite. It includes settings for data
paths, memory limits, logging, and other necessary parameters.

Author: Lane
"""

import os
import psutil


class Config:
    # Workspace settings
    WORKSPACE_NAME = "default_workspace"
    BASE_DIR = os.path.abspath(os.path.join(os.path.expanduser('~'), 'Documents', 'NBAS Workspaces', WORKSPACE_NAME))

    # Paths
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    WORKSPACE_DIR = os.path.join(BASE_DIR, 'workspace')
    BACKUP_DIR = os.path.join(BASE_DIR, 'backup')
    ENGINE_DIR = os.path.join(BASE_DIR, 'engines')

    # Memory settings
    MEMORY_LIMIT = psutil.virtual_memory().total * 0.5  # 50% of available memory

    # Logging settings
    LOG_LEVEL = 'INFO'
    LOG_FILE = os.path.join(LOG_DIR, 'app.log')
    LOG_ROTATION = '1 week'  # Rotate logs every week
    LOG_RETENTION = '4 weeks'  # Retain logs for 4 weeks

    # Data engine settings
    CACHE_SIZE = 2e9  # 2GB cache size by default
    NUM_THREADS = 4  # Number of threads for processing

    # Database settings
    DB_HOST = 'localhost'
    DB_PORT = 5432
    DB_USER = 'user'
    DB_PASSWORD = 'password'
    DB_NAME = 'database'

    # API settings
    API_BASE_URL = 'https://api.example.com'
    API_KEY = 'your_api_key_here'

    # Notification settings
    EMAIL_HOST = 'smtp.example.com'
    EMAIL_PORT = 587
    EMAIL_USER = 'user@example.com'
    EMAIL_PASSWORD = 'password'
    EMAIL_USE_TLS = True
    EMAIL_USE_SSL = False

    # UI settings
    THEME = 'light'  # Options: 'light', 'dark'
    LANGUAGE = 'en'  # Default language

    # Security settings
    ENCRYPTION_KEY = 'your_encryption_key_here'
    AUTHENTICATION_METHOD = 'token'  # Options: 'token', 'oauth', 'basic'

    # Performance settings
    BATCH_SIZE = 100  # Default batch size for processing

    # Data transformation settings
    TRANSFORMATIONS = {
        'normalize': True,
        'standardize': False,
        'remove_outliers': True
    }

    # Scheduler settings
    SCHEDULER_INTERVAL = 'daily'  # Options: 'hourly', 'daily', 'weekly'

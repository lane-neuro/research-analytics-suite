"""
SettingsDialog Module

This module defines the SettingsDialog class, which provides a GUI for managing the configuration settings of the
NeuroBehavioral Analytics Suite.

Author: Lane
"""

import dearpygui.dearpygui as dpg
from neurobehavioral_analytics_suite.data_engine.Config import Config
from neurobehavioral_analytics_suite.utils.CustomLogger import CustomLogger


class SettingsDialog:
    """Class to create and manage the settings dialog for configuration variables."""

    def __init__(self, logger: CustomLogger):
        """
        Initializes the SettingsDialog instance.

        Args:
            logger (CustomLogger): CustomLogger for logging information and errors.
        """
        self.logger = logger

    def show(self):
        """Shows the settings dialog."""
        with dpg.window(label="Settings", modal=True, tag="settings_dialog", width=500):
            dpg.add_text("Configuration Settings")

            # Paths
            dpg.add_input_text(label="Workspace Name", default_value=Config.WORKSPACE_NAME, tag="workspace_name")
            dpg.add_input_text(label="Data Directory", default_value=Config.DATA_DIR, tag="data_dir")
            dpg.add_input_text(label="Log Directory", default_value=Config.LOG_DIR, tag="log_dir")
            dpg.add_input_text(label="Workspace Directory", default_value=Config.WORKSPACE_DIR, tag="workspace_dir")
            dpg.add_input_text(label="Backup Directory", default_value=Config.BACKUP_DIR, tag="backup_dir")

            # Memory settings
            dpg.add_input_float(label="Memory Limit", default_value=Config.MEMORY_LIMIT, tag="memory_limit")

            # Logging settings
            dpg.add_input_text(label="Log File", default_value=Config.LOG_FILE, tag="log_file")
            dpg.add_input_text(label="Log Rotation", default_value=Config.LOG_ROTATION, tag="log_rotation")
            dpg.add_input_text(label="Log Retention", default_value=Config.LOG_RETENTION, tag="log_retention")
            dpg.add_combo(label="Log Level", items=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                          default_value=Config.LOG_LEVEL, tag="log_level")

            # Data engine settings
            dpg.add_input_int(label="Cache Size", default_value=Config.CACHE_SIZE, tag="cache_size")
            dpg.add_input_int(label="Number of Threads", default_value=Config.NUM_THREADS, tag="num_threads")

            # Database settings
            dpg.add_input_text(label="DB Host", default_value=Config.DB_HOST, tag="db_host")
            dpg.add_input_int(label="DB Port", default_value=Config.DB_PORT, tag="db_port")
            dpg.add_input_text(label="DB User", default_value=Config.DB_USER, tag="db_user")
            dpg.add_input_text(label="DB Password", default_value=Config.DB_PASSWORD, tag="db_password", password=True)
            dpg.add_input_text(label="DB Name", default_value=Config.DB_NAME, tag="db_name")

            # API settings
            dpg.add_input_text(label="API Base URL", default_value=Config.API_BASE_URL, tag="api_base_url")
            dpg.add_input_text(label="API Key", default_value=Config.API_KEY, tag="api_key", password=True)

            # Notification settings
            dpg.add_input_text(label="Email Host", default_value=Config.EMAIL_HOST, tag="email_host")
            dpg.add_input_int(label="Email Port", default_value=Config.EMAIL_PORT, tag="email_port")
            dpg.add_input_text(label="Email User", default_value=Config.EMAIL_USER, tag="email_user")
            dpg.add_input_text(label="Email Password", default_value=Config.EMAIL_PASSWORD, tag="email_password",
                               password=True)
            dpg.add_checkbox(label="Email Use TLS", default_value=Config.EMAIL_USE_TLS, tag="email_use_tls")
            dpg.add_checkbox(label="Email Use SSL", default_value=Config.EMAIL_USE_SSL, tag="email_use_ssl")

            # UI settings
            dpg.add_combo(label="Theme", items=["light", "dark"], default_value=Config.THEME, tag="theme")
            dpg.add_input_text(label="Language", default_value=Config.LANGUAGE, tag="language")

            # Security settings
            dpg.add_input_text(label="Encryption Key", default_value=Config.ENCRYPTION_KEY, tag="encryption_key",
                               password=True)
            dpg.add_combo(label="Authentication Method", items=["token", "oauth", "basic"],
                          default_value=Config.AUTHENTICATION_METHOD, tag="authentication_method")

            # Performance settings
            dpg.add_input_int(label="Batch Size", default_value=Config.BATCH_SIZE, tag="batch_size")

            # Data transformation settings
            dpg.add_checkbox(label="Normalize", default_value=Config.TRANSFORMATIONS['normalize'], tag="normalize")
            dpg.add_checkbox(label="Standardize", default_value=Config.TRANSFORMATIONS['standardize'],
                             tag="standardize")
            dpg.add_checkbox(label="Remove Outliers", default_value=Config.TRANSFORMATIONS['remove_outliers'],
                             tag="remove_outliers")

            # Scheduler settings
            dpg.add_combo(label="Scheduler Interval", items=["hourly", "daily", "weekly"],
                          default_value=Config.SCHEDULER_INTERVAL, tag="scheduler_interval")

            dpg.add_button(label="Save", callback=self.save_settings)
            dpg.add_button(label="Close", callback=lambda: dpg.delete_item("settings_dialog"))

    def save_settings(self):
        """Saves the updated settings."""
        Config.WORKSPACE_NAME = dpg.get_value("workspace_name")

        Config.DATA_DIR = dpg.get_value("data_dir")
        Config.LOG_DIR = dpg.get_value("log_dir")
        Config.WORKSPACE_DIR = dpg.get_value("workspace_dir")
        Config.BACKUP_DIR = dpg.get_value("backup_dir")
        Config.ENGINE_DIR = dpg.get_value("engine_dir")

        Config.MEMORY_LIMIT = dpg.get_value("memory_limit")

        Config.LOG_LEVEL = dpg.get_value("log_level")
        Config.LOG_FILE = dpg.get_value("log_file")
        Config.LOG_ROTATION = dpg.get_value("log_rotation")
        Config.LOG_RETENTION = dpg.get_value("log_retention")

        Config.CACHE_SIZE = dpg.get_value("cache_size")
        Config.NUM_THREADS = dpg.get_value("num_threads")

        Config.DB_HOST = dpg.get_value("db_host")
        Config.DB_PORT = dpg.get_value("db_port")
        Config.DB_USER = dpg.get_value("db_user")
        Config.DB_PASSWORD = dpg.get_value("db_password")
        Config.DB_NAME = dpg.get_value("db_name")

        Config.API_BASE_URL = dpg.get_value("api_base_url")
        Config.API_KEY = dpg.get_value("api_key")

        Config.EMAIL_HOST = dpg.get_value("email_host")
        Config.EMAIL_PORT = dpg.get_value("email_port")
        Config.EMAIL_USER = dpg.get_value("email_user")
        Config.EMAIL_PASSWORD = dpg.get_value("email_password")
        Config.EMAIL_USE_TLS = dpg.get_value("email_use_tls")
        Config.EMAIL_USE_SSL = dpg.get_value("email_use_ssl")

        Config.THEME = dpg.get_value("theme")
        Config.LANGUAGE = dpg.get_value("language")

        Config.ENCRYPTION_KEY = dpg.get_value("encryption_key")
        Config.AUTHENTICATION_METHOD = dpg.get_value("authentication_method")

        Config.BATCH_SIZE = dpg.get_value("batch_size")
        Config.TRANSFORMATIONS['normalize'] = dpg.get_value("normalize")
        Config.TRANSFORMATIONS['standardize'] = dpg.get_value("standardize")
        Config.TRANSFORMATIONS['remove_outliers'] = dpg.get_value("remove_outliers")

        Config.SCHEDULER_INTERVAL = dpg.get_value("scheduler_interval")

        self.logger.info("Settings updated successfully.")
        dpg.delete_item("settings_dialog")

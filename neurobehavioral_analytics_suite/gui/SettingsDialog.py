"""
SettingsDialog Module

This module defines the SettingsDialog class, which provides a GUI for managing the self._configuration settings of the
NeuroBehavioral Analytics Suite.

Author: Lane
"""
import dearpygui.dearpygui as dpg
from neurobehavioral_analytics_suite.data_engine.Config import Config
from neurobehavioral_analytics_suite.utils.CustomLogger import CustomLogger


class SettingsDialog:
    """Class to create and manage the settings dialog for self._configuration variables."""

    def __init__(self):
        """
        Initializes the SettingsDialog instance.
        """
        self._logger = CustomLogger()
        self._config = Config()

    def show(self):
        """Shows the settings dialog."""
        with dpg.window(label="Settings", modal=True, tag="settings_dialog", width=500):
            dpg.add_text("Configuration Settings", color=(255, 255, 0))

            # Paths
            dpg.add_input_text(label="Workspace Name", default_value=self._config.WORKSPACE_NAME, tag="workspace_name")
            dpg.add_input_text(label="Data Directory", default_value=self._config.DATA_DIR, tag="data_dir")
            dpg.add_input_text(label="Log Directory", default_value=self._config.LOG_DIR, tag="log_dir")
            dpg.add_input_text(label="Workspace Directory", default_value=self._config.WORKSPACE_DIR,
                               tag="workspace_dir")
            dpg.add_input_text(label="Backup Directory", default_value=self._config.BACKUP_DIR, tag="backup_dir")

            dpg.add_separator()

            # Memory settings
            dpg.add_input_float(label="Memory Limit", default_value=self._config.MEMORY_LIMIT, tag="memory_limit")

            dpg.add_separator()

            # Logging settings
            dpg.add_input_text(label="Log File", default_value=self._config.LOG_FILE, tag="log_file")
            dpg.add_input_text(label="Log Rotation", default_value=self._config.LOG_ROTATION, tag="log_rotation")
            dpg.add_input_text(label="Log Retention", default_value=self._config.LOG_RETENTION, tag="log_retention")
            dpg.add_combo(label="Log Level", items=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                          default_value=self._config.LOG_LEVEL, tag="log_level")

            dpg.add_separator()

            # Data engine settings
            dpg.add_input_int(label="Cache Size", default_value=self._config.CACHE_SIZE, tag="cache_size")
            dpg.add_input_int(label="Number of Threads", default_value=self._config.NUM_THREADS, tag="num_threads")

            dpg.add_separator()

            # Database settings
            dpg.add_input_text(label="DB Host", default_value=self._config.DB_HOST, tag="db_host")
            dpg.add_input_int(label="DB Port", default_value=self._config.DB_PORT, tag="db_port")
            dpg.add_input_text(label="DB User", default_value=self._config.DB_USER, tag="db_user")
            dpg.add_input_text(label="DB Password", default_value=self._config.DB_PASSWORD, tag="db_password",
                               password=True)
            dpg.add_input_text(label="DB Name", default_value=self._config.DB_NAME, tag="db_name")

            dpg.add_separator()

            # API settings
            dpg.add_input_text(label="API Base URL", default_value=self._config.API_BASE_URL, tag="api_base_url")
            dpg.add_input_text(label="API Key", default_value=self._config.API_KEY, tag="api_key", password=True)

            dpg.add_separator()

            # Notification settings
            dpg.add_input_text(label="Email Host", default_value=self._config.EMAIL_HOST, tag="email_host")
            dpg.add_input_int(label="Email Port", default_value=self._config.EMAIL_PORT, tag="email_port")
            dpg.add_input_text(label="Email User", default_value=self._config.EMAIL_USER, tag="email_user")
            dpg.add_input_text(label="Email Password", default_value=self._config.EMAIL_PASSWORD, tag="email_password",
                               password=True)
            dpg.add_checkbox(label="Email Use TLS", default_value=self._config.EMAIL_USE_TLS, tag="email_use_tls")
            dpg.add_checkbox(label="Email Use SSL", default_value=self._config.EMAIL_USE_SSL, tag="email_use_ssl")

            dpg.add_separator()

            # UI settings
            dpg.add_combo(label="Theme", items=["light", "dark"], default_value=self._config.THEME, tag="theme")
            dpg.add_input_text(label="Language", default_value=self._config.LANGUAGE, tag="language")

            dpg.add_separator()

            # Security settings
            dpg.add_input_text(label="Encryption Key", default_value=self._config.ENCRYPTION_KEY, tag="encryption_key",
                               password=True)
            dpg.add_combo(label="Authentication Method", items=["token", "oauth", "basic"],
                          default_value=self._config.AUTHENTICATION_METHOD, tag="authentication_method")

            dpg.add_separator()

            # Performance settings
            dpg.add_input_int(label="Batch Size", default_value=self._config.BATCH_SIZE, tag="batch_size")

            dpg.add_separator()

            # Data transformation settings
            dpg.add_checkbox(label="Normalize", default_value=self._config.TRANSFORMATIONS['normalize'],
                             tag="normalize")
            dpg.add_checkbox(label="Standardize", default_value=self._config.TRANSFORMATIONS['standardize'],
                             tag="standardize")
            dpg.add_checkbox(label="Remove Outliers", default_value=self._config.TRANSFORMATIONS['remove_outliers'],
                             tag="remove_outliers")

            dpg.add_separator()

            # Scheduler settings
            dpg.add_combo(label="Scheduler Interval", items=["hourly", "daily", "weekly"],
                          default_value=self._config.SCHEDULER_INTERVAL, tag="scheduler_interval")

            dpg.add_button(label="Save", callback=self.save_settings)
            dpg.add_button(label="Close", callback=lambda: dpg.delete_item("settings_dialog"))

    def save_settings(self):
        """Saves the updated settings."""
        self._config.WORKSPACE_NAME = dpg.get_value("workspace_name")

        self._config.DATA_DIR = dpg.get_value("data_dir")
        self._config.LOG_DIR = dpg.get_value("log_dir")
        self._config.WORKSPACE_DIR = dpg.get_value("workspace_dir")
        self._config.BACKUP_DIR = dpg.get_value("backup_dir")
        self._config.ENGINE_DIR = dpg.get_value("engine_dir")

        self._config.MEMORY_LIMIT = dpg.get_value("memory_limit")

        self._config.LOG_LEVEL = dpg.get_value("log_level")
        self._config.LOG_FILE = dpg.get_value("log_file")
        self._config.LOG_ROTATION = dpg.get_value("log_rotation")
        self._config.LOG_RETENTION = dpg.get_value("log_retention")

        self._config.CACHE_SIZE = dpg.get_value("cache_size")
        self._config.NUM_THREADS = dpg.get_value("num_threads")

        self._config.DB_HOST = dpg.get_value("db_host")
        self._config.DB_PORT = dpg.get_value("db_port")
        self._config.DB_USER = dpg.get_value("db_user")
        self._config.DB_PASSWORD = dpg.get_value("db_password")
        self._config.DB_NAME = dpg.get_value("db_name")

        self._config.API_BASE_URL = dpg.get_value("api_base_url")
        self._config.API_KEY = dpg.get_value("api_key")

        self._config.EMAIL_HOST = dpg.get_value("email_host")
        self._config.EMAIL_PORT = dpg.get_value("email_port")
        self._config.EMAIL_USER = dpg.get_value("email_user")
        self._config.EMAIL_PASSWORD = dpg.get_value("email_password")
        self._config.EMAIL_USE_TLS = dpg.get_value("email_use_tls")
        self._config.EMAIL_USE_SSL = dpg.get_value("email_use_ssl")

        self._config.THEME = dpg.get_value("theme")
        self._config.LANGUAGE = dpg.get_value("language")

        self._config.ENCRYPTION_KEY = dpg.get_value("encryption_key")
        self._config.AUTHENTICATION_METHOD = dpg.get_value("authentication_method")

        self._config.BATCH_SIZE = dpg.get_value("batch_size")
        self._config.TRANSFORMATIONS['normalize'] = dpg.get_value("normalize")
        self._config.TRANSFORMATIONS['standardize'] = dpg.get_value("standardize")
        self._config.TRANSFORMATIONS['remove_outliers'] = dpg.get_value("remove_outliers")

        self._config.SCHEDULER_INTERVAL = dpg.get_value("scheduler_interval")

        self._logger.info("Settings updated successfully.")
        dpg.delete_item("settings_dialog")

"""
CustomLogger Module

This module contains the CustomLogger class, which is used to handle logging within the research analytics suite. The
CustomLogger class sets up a logger with a specific format, handles different log levels, and queues log messages for
asynchronous processing. The CustomLogger class is a singleton class, meaning that only one instance of the class can
exist at a time. This is to ensure that all log messages are handled by the same logger instance.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

import asyncio
import logging
import os
import traceback
from typing import List
from logging.handlers import TimedRotatingFileHandler


class CustomLogger:
    """
    A class to handle logging within the research analytics suite.

    This class sets up a logger with a specific format, handles different log levels, and queues log messages for
    asynchronous processing.
    """
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        """
        Creates a new instance of the CustomLogger class. If an instance already exists,
        returns the existing instance.
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initializes the CustomLogger with a specified log level.
        """
        if not hasattr(self, '_initialized'):
            self._config = None

            self._info_logger = None
            self._error_logger = None
            self._debug_logger = None
            self._warning_logger = None
            self._critical_logger = None
            self.log_message_queue = None

            self._initialized = False

    async def initialize(self) -> None:
        """
        Sets up the logger with a timestamp formatter and a stream handler.
        """
        if not self._initialized:
            async with CustomLogger._lock:
                if not self._initialized:
                    from research_analytics_suite.utils import Config
                    self._config = Config()

                    # Set up the loggers
                    self._info_logger = logging.getLogger('RAS - INFO')
                    self._info_logger.setLevel(logging.INFO)

                    self._error_logger = logging.getLogger('RAS - ERROR')
                    self._error_logger.setLevel(logging.ERROR)

                    self._debug_logger = logging.getLogger('RAS - DEBUG')
                    self._debug_logger.setLevel(logging.DEBUG)

                    self._warning_logger = logging.getLogger('RAS - WARNING')
                    self._warning_logger.setLevel(logging.WARNING)

                    self._critical_logger = logging.getLogger('RAS - CRITICAL')
                    self._critical_logger.setLevel(logging.CRITICAL)

                    # Set up the log message queue
                    self.log_message_queue = asyncio.Queue()
                    stream_handler = logging.StreamHandler()
                    formatter = logging.Formatter(
                        '(%(asctime)s) [[%(name)s]]: %(message)s',
                        datefmt='%y-%m-%d %H:%M:%S'
                    )
                    stream_handler.setFormatter(formatter)

                    for logger in [
                        self._info_logger,
                        self._error_logger,
                        self._debug_logger,
                        self._warning_logger,
                        self._critical_logger
                    ]:
                        if logger.level != logging.DEBUG or self._config.DEBUG_CONSOLE is True:
                            logger.addHandler(stream_handler)
                        logger.addFilter(self._log_message)

                    self._info_logger.info(f"[{self._info_logger.name}] logging initialized")
                    self._error_logger.error(f"[{self._error_logger.name}] logging initialized")
                    self._debug_logger.debug(f"[{self._debug_logger.name}] logging initialized")
                    self._warning_logger.warning(f"[{self._warning_logger.name}] logging initialized")
                    self._critical_logger.critical(f"[{self._critical_logger.name}] logging initialized")

                    self._initialized = True

    def add_file_handlers(self):
        """
        Adds file handlers to the loggers if LOG_DIR is a valid directory.
        """
        if not self._config:
            from research_analytics_suite.utils import Config
            self._config = Config()

        try:
            log_dir = os.path.normpath(os.path.join(self._config.BASE_DIR, 'workspaces', self._config.WORKSPACE_NAME,
                                                    self._config.LOG_DIR))
        except Exception as e:
            log_dir = None

        if log_dir and os.path.exists(log_dir):
            formatter = logging.Formatter(
                '(%(asctime)s) [[%(name)s]]: %(message)s',
                datefmt='%y-%m-%d %H:%M:%S'
            )
            for logger_name, logger in [('info', self._info_logger), ('error', self._error_logger),
                                        ('debug', self._debug_logger), ('warning', self._warning_logger),
                                        ('critical', self._critical_logger)]:
                file_handler = TimedRotatingFileHandler(
                    os.path.join(log_dir, f'{logger_name}.log'),
                    when='W0',
                    interval=self._config.LOG_ROTATION,
                    backupCount=self._config.LOG_RETENTION
                )
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
                self._info_logger.info(f"[{logger.name}] file logging initialized")
        else:
            self._info_logger.warning("Log directory not found. File logging not enabled for this session.")

    def _log_message(self, record: logging.LogRecord) -> bool:
        """
        Sends a log message to the queue.

        Args:
            record (logging.LogRecord): The log record to send to the queue.
        """
        message = f"{record.levelname}: {record.getMessage()}"
        self.log_message_queue.put_nowait(message)
        return True

    async def _process_log_queue(self):
        """
        Processes the log message queue asynchronously.
        """
        while True:
            message = await self.log_message_queue.get()
            print(message)

    def info(self, message: str or list, context: str = None) -> None:
        """
        Logs an info message.

        Args:
            message: The message to log.
            context: The context in which the message occurred. Defaults to None.
        """
        if not self._info_logger:
            print(f"{message}")
            # Attempt to log the message as a debug message
            self.debug(f"Logger not initialized: {message}")
            return

        if isinstance(message, List):
            for msg in message:
                self._info_logger.info(f"{context}: {msg}" if context else msg)
        elif isinstance(message, str):
            for part in message.split('\n'):
                part = part.replace('\n', '')
                self._info_logger.info(f"{context}: {part}" if context else part)
        else:
            self._info_logger.info(f"{context}: {message}" if context else message)

    def debug(self, message: str, context: str = None) -> None:
        """
        Logs a debug message.

        Args:
            message (str): The message to log.
            context: The context in which the message occurred. Defaults to None.
        """
        if not self._debug_logger:
            print(f"{message}")
            return

        if isinstance(message, List):
            for msg in message:
                self._debug_logger.debug(f"{context}: {msg}" if context else msg)
        elif isinstance(message, str):
            for part in message.split('\n'):
                part = part.replace('\n', '')
                self._debug_logger.debug(f"{context}: {part}" if context else part)
        else:
            self._debug_logger.debug(f"{context}: {message}" if context else message)

    def error(self, exception: Exception, context: str = None):
        """
        Logs an error message.

        Args:
            exception (Exception): The exception to log.
            context: The context in which the error occurred.
        """
        if not self._error_logger:
            print(f"Error: {exception} in {context}")
            return

        error_info = traceback.format_exc()
        error_message = f"An error occurred in {context}: {exception}"
        if error_info != 'NoneType: None\n':
            error_message += f"\n{error_info}"
        self._error_logger.error(error_message)

    def warning(self, message: str) -> None:
        """
        Logs a warning message.

        Args:
            message (str): The message to log.
        """
        if not self._warning_logger:
            print(f"{message}")
            return

        if isinstance(message, List):
            for msg in message:
                self._warning_logger.warning(msg)
        elif isinstance(message, str):
            for part in message.split('\n'):
                part = part.replace('\n', '')
                self._warning_logger.warning(part)
        else:
            self._warning_logger.warning(message)

    def critical(self, message: str) -> None:
        """
        Logs a critical message.

        Args:
            message (str): The message to log.
        """
        if not self._critical_logger:
            print(f"{message}")
            return

        if isinstance(message, List):
            for msg in message:
                self._critical_logger.critical(msg)
        elif isinstance(message, str):
            for part in message.split('\n'):
                part = part.replace('\n', '')
                self._critical_logger.critical(part)
        else:
            self._critical_logger.critical(message)

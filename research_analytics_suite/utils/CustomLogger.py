"""
CustomLogger Module

This module defines the CustomLogger class, which is responsible for logging messages within the research analytics
suite. It sets up a logger with a specific format, handles different log levels, and queues log messages for asynchronous
processing.

Author: Lane
"""

import asyncio
import logging
import traceback
from typing import List


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
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """
        Initializes the CustomLogger with a specified log level.
        """
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger('RAS')
            self._logger.setLevel(logging.INFO)
            self.log_message_queue = asyncio.Queue()

            self.setup_logger()
            self.info(f"[{self._logger.name}] CustomLogger initialized")

    def setup_logger(self) -> None:
        """
        Sets up the logger with a timestamp formatter and a stream handler.
        """
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[(%(asctime)s) %(name)s - %(levelname)s]: %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)
        self._logger.addFilter(self._log_message)

    def _log_message(self, record: logging.LogRecord) -> bool:
        """
        Sends a log message to the queue.

        Args:
            record (logging.LogRecord): The log record to send to the queue.
        """
        message = record.getMessage()
        self.log_message_queue.put_nowait(message)
        # print(message)
        return True  # Allow the log record to be logged

    def info(self, message) -> None:
        """
        Logs an info message.

        Args:
            message: The message to log.
        """
        if isinstance(message, List):
            for msg in message:
                self._logger.info(msg)
        else:
            self._logger.info(message)

    def debug(self, message: str) -> None:
        """
        Logs a debug message.

        Args:
            message (str): The message to log.
        """
        self._logger.debug(message)

    def error(self, exception, context=None):
        """
        Logs an error message.

        Args:
            exception (Exception): The exception to log.
            context: The context in which the error occurred.
        """
        error_info = traceback.format_exc()
        error_message = f"An error occurred in {context}: {exception}\n{error_info}"
        self._logger.error(error_message)

    def warning(self, message: str) -> None:
        """
        Logs a warning message.

        Args:
            message (str): The message to log.
        """
        self._logger.warning(message)

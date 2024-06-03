"""
Logger Module.

This module defines the Logger class, which is responsible for logging messages within the neurobehavioral analytics
suite. It sets up a logger with a specific format, handles different log levels, & queues log messages for asynchronous
processing.

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


class Logger:
    """
    A class to handle logging within the neurobehavioral analytics suite.

    This class sets up a logger with a specific format, handles different log levels, and queues log messages for
    asynchronous processing.
    """

    def __init__(self, log_level=logging.INFO):
        """
        Initializes the Logger with a specified log level.

        Args:
            log_level (int): The logging level (e.g., logging.INFO, logging.DEBUG).
        """
        self.logger = logging.getLogger('NBAS')
        self.logger.setLevel(log_level)
        self.log_message_queue = asyncio.Queue()

        self.setup_logger()

    def setup_logger(self) -> None:
        """
        Sets up the logger with a timestamp formatter and a stream handler.
        """
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[(%(asctime)s) %(name)s - %(levelname)s]:   %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.addFilter(lambda record: self.log_message(record.getMessage()))

    def log_message(self, message: str) -> None:
        """
        Sends a log message to the queue.

        Args:
            message (str): The log message to send to the queue.
        """
        self.log_message_queue.put_nowait(message)
        print(message)

    def info(self, message: str) -> None:
        """
        Logs an info message.

        Args:
            message (str): The message to log.
        """
        self.logger.info(message)

    def debug(self, message: str) -> None:
        """
        Logs a debug message.

        Args:
            message (str): The message to log.
        """
        self.logger.debug(message)

    def error(self, message: str) -> None:
        """
        Logs an error message.

        Args:
            message (str): The message to log.
        """
        self.logger.error(message)
        print(message)

    def warning(self, message: str) -> None:
        """
        Logs a warning message.

        Args:
            message (str): The message to log.
        """
        self.logger.warning(message)

"""
Module description.

Longer description.

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
    def __init__(self, log_level=logging.INFO):
        self.logger = logging.getLogger('NBAS')
        self.logger.setLevel(log_level)
        self.log_message_queue = asyncio.Queue()

        self.setup_logger()

    def setup_logger(self):
        """
        Sets up the logger with a timestamp.
        """
        # Create a handler
        handler = logging.StreamHandler()

        # Create a formatter and add it to the handler
        formatter = logging.Formatter('[(%(asctime)s) %(name)s - %(levelname)s]:   %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)

        # Add the handler to the self.logger
        self.logger.addHandler(handler)

        # Add a log message to the queue whenever a new log is generated
        self.logger.addFilter(lambda record: self.log_message(record.getMessage()))

    def log_message(self, message):
        """Send a log message to the queue."""
        self.log_message_queue.put_nowait(message)

    def info(self, message):
        self.logger.info(message)

    def debug(self, message):
        self.logger.debug(message)

    def error(self, message):
        self.logger.error(message)

    def warning(self, message):
        self.logger.warning(message)

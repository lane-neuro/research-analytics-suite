"""
LoggerStream

This module contains a class that can be used to redirect the output of the print function to a logger object.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""


class LoggerStream:
    def __init__(self, logger):
        self.logger = logger

    def write(self, message):
        if message != '\n':  # Avoid logging empty messages
            self.logger.info(message.strip())

    def flush(self):
        pass  # No need to implement flush for logger

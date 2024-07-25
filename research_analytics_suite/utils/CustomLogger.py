import asyncio
import logging
import traceback
from typing import List

from research_analytics_suite.commands.CommandDecorators import command, link_class_commands


@link_class_commands
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
            self._logger = None
            self.log_message_queue = None
            self._initialized = False

    async def initialize(self) -> None:
        """
        Sets up the logger with a timestamp formatter and a stream handler.
        """
        if not self._initialized:
            async with CustomLogger._lock:
                if not self._initialized:
                    self._logger = logging.getLogger('RAS')
                    self._logger.setLevel(logging.INFO)  # Default logger level is INFO

                    self.log_message_queue = asyncio.Queue()
                    handler = logging.StreamHandler()
                    formatter = logging.Formatter(
                        '[(%(asctime)s) %(name)s - %(levelname)s]: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S'
                    )
                    handler.setFormatter(formatter)
                    self._logger.addHandler(handler)
                    self._logger.addFilter(self._log_message)

                    self.debug(f"[{self._logger.name}] CustomLogger initialized")
                    self._initialized = True

    def _log_message(self, record: logging.LogRecord) -> bool:
        """
        Sends a log message to the queue.

        Args:
            record (logging.LogRecord): The log record to send to the queue.
        """
        message = f"{record.levelname}: {record.getMessage()}"
        self.log_message_queue.put_nowait(message)
        return True  # Allow the log record to be logged

    @command
    def info(self, message: str or list) -> None:
        """
        Logs an info message.

        Args:
            message: The message to log.
        """
        if not self._logger:
            print(f"Logger not initialized: {message}")
            return

        if isinstance(message, List):
            for msg in message:
                self._logger.info(msg)
        elif isinstance(message, str):
            for part in message.split('\n'):
                self._logger.info(part.replace('\n', ''))
        else:
            self._logger.info(message)

    def debug(self, message: str) -> None:
        """
        Logs a debug message.

        Args:
            message (str): The message to log.
        """
        if not self._logger:
            print(f"Logger not initialized: {message}")
            return

        self._logger.debug(message)

    @command
    def error(self, exception: Exception, context: str = None):
        """
        Logs an error message.

        Args:
            exception (Exception): The exception to log.
            context: The context in which the error occurred.
        """
        if not self._logger:
            print(f"Logger not initialized: {exception}")
            return

        error_info = traceback.format_exc()
        error_message = f"An error occurred in {context}: {exception}"
        if error_info != 'NoneType: None\n':
            error_message += f"\n{error_info}"
        self._logger.error(error_message)

    def warning(self, message: str) -> None:
        """
        Logs a warning message.

        Args:
            message (str): The message to log.
        """
        if not self._logger:
            print(f"Logger not initialized: {message}")
            return

        self._logger.warning(message)

import asyncio
import logging
import os
import shutil
import tempfile
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from research_analytics_suite.utils import CustomLogger, Config


class TestCustomLogger:
    @pytest_asyncio.fixture(autouse=True)
    async def setup_class(self):
        # Create a temporary directory
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = os.path.join(self.temp_dir, 'logs')

        # Mock the Config class
        self.config_mock = AsyncMock(spec=Config)
        self.config_mock.BASE_DIR = self.temp_dir
        self.config_mock.WORKSPACE_NAME = 'mocked_workspace'
        self.config_mock.LOG_DIR = 'logs'
        self.config_mock.LOG_ROTATION = 1
        self.config_mock.LOG_RETENTION = 4
        self.config_mock.DEBUG_CONSOLE = False

        with patch('research_analytics_suite.utils.Config', return_value=self.config_mock):
            self.logger = CustomLogger()
            await self.logger.initialize()

        # Clear the queue before each test to avoid interference between tests
        while not self.logger.log_message_queue.empty():
            await self.logger.log_message_queue.get()

        # Add a debug-level stream handler for testing
        self.debug_handler = logging.StreamHandler()
        self.debug_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '[(%(asctime)s) %(name)s - %(levelname)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.debug_handler.setFormatter(formatter)
        self.logger._info_logger.addHandler(self.debug_handler)
        self.logger._debug_logger.addHandler(self.debug_handler)
        self.logger._warning_logger.addHandler(self.debug_handler)
        self.logger._error_logger.addHandler(self.debug_handler)
        self.logger._critical_logger.addHandler(self.debug_handler)

        # Set log level based on environment variable
        log_level = os.getenv('PYTHON_LOG_LEVEL', 'DEBUG').upper()
        self.logger._info_logger.setLevel(getattr(logging, log_level))
        self.logger._debug_logger.setLevel(getattr(logging, log_level))
        self.logger._warning_logger.setLevel(getattr(logging, log_level))
        self.logger._error_logger.setLevel(getattr(logging, log_level))
        self.logger._critical_logger.setLevel(getattr(logging, log_level))

    @pytest_asyncio.fixture(autouse=True)
    async def teardown_class(self):
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)

    def test_initialize_logger(self):
        assert self.logger._info_logger is not None
        assert self.logger._info_logger.level == logging.DEBUG
        assert len(self.logger._info_logger.handlers) > 0
        assert isinstance(self.logger._info_logger.handlers[0], logging.StreamHandler)
        assert self.logger._initialized

    @pytest.mark.asyncio
    async def test_singleton_behavior(self):
        logger2 = CustomLogger()
        await logger2.initialize()
        assert self.logger is logger2

    @pytest.mark.asyncio
    async def test_logging_levels(self):
        try:
            raise ValueError("Test error")
        except ValueError as e:
            self.logger.error(e, "test_logging_levels")

        self.logger.debug("Test debug message", "test_logging_levels")
        self.logger.info("Test info message", "test_logging_levels")
        self.logger.warning("Test warning message")
        self.logger.critical("Test critical message")

        await asyncio.sleep(0.1)  # Ensure messages are processed
        queue_contents = []
        while not self.logger.log_message_queue.empty():
            queue_contents.append(await self.logger.log_message_queue.get())

        assert any("ERROR: An error occurred in test_logging_levels: Test error" in msg for msg in queue_contents)
        assert "DEBUG: test_logging_levels: Test debug message" in queue_contents
        assert "INFO: test_logging_levels: Test info message" in queue_contents
        assert "WARNING: Test warning message" in queue_contents
        assert "CRITICAL: Test critical message" in queue_contents

    @pytest.mark.asyncio
    async def test_logging_queue(self):
        self.logger.info("Test queue message")
        self.logger.debug("Test queue message debug")

        await asyncio.sleep(0.001)  # Ensure messages are processed
        queue_contents = []
        while not self.logger.log_message_queue.empty():
            queue_contents.append(await self.logger.log_message_queue.get())

        assert "INFO: Test queue message" in queue_contents
        assert "DEBUG: Test queue message debug" in queue_contents

    @pytest.mark.asyncio
    async def test_error_logging(self):
        try:
            raise ValueError("Test error")
        except ValueError as e:
            self.logger.error(e, "test_error_logging")

        await asyncio.sleep(0.001)  # Ensure messages are processed
        assert not self.logger.log_message_queue.empty()
        error_message = await self.logger.log_message_queue.get()
        assert "ERROR: An error occurred in test_error_logging: Test error" in error_message

    @pytest.mark.asyncio
    async def test_empty_message_logging(self):
        self.logger.info("")
        self.logger.debug("")

        await asyncio.sleep(0.001)  # Ensure messages are processed
        queue_contents = []
        while not self.logger.log_message_queue.empty():
            queue_contents.append(await self.logger.log_message_queue.get())

        assert "INFO: " in queue_contents
        assert "DEBUG: " in queue_contents

    @pytest.mark.asyncio
    async def test_concurrent_logging(self):
        async def log_messages():
            for i in range(10):
                self.logger.info(f"Concurrent log {i}")
                self.logger.debug(f"Concurrent debug {i}")

        await asyncio.gather(log_messages(), log_messages(), log_messages())

        await asyncio.sleep(0.001)  # Ensure messages are processed
        queue_contents = []
        while not self.logger.log_message_queue.empty():
            queue_contents.append(await self.logger.log_message_queue.get())

        # Check if a few messages are present in the queue
        assert any(f"INFO: Concurrent log {i}" in msg for i in range(10) for msg in queue_contents)
        assert any(f"DEBUG: Concurrent debug {i}" in msg for i in range(10) for msg in queue_contents)

    @pytest.mark.asyncio
    async def test_logging_with_list_input(self):
        messages = ["First message", "Second message", "Third message"]
        self.logger.info(messages, "test_logging_with_list_input")

        await asyncio.sleep(0.001)  # Ensure messages are processed
        queue_contents = []
        while not self.logger.log_message_queue.empty():
            queue_contents.append(await self.logger.log_message_queue.get())

        for msg in messages:
            assert f"INFO: test_logging_with_list_input: {msg}" in queue_contents

    @pytest.mark.asyncio
    async def test_logging_with_multiline_string(self):
        message = "First line\nSecond line\nThird line"
        self.logger.info(message, "test_logging_with_multiline_string")

        await asyncio.sleep(0.001)  # Ensure messages are processed
        queue_contents = []
        while not self.logger.log_message_queue.empty():
            queue_contents.append(await self.logger.log_message_queue.get())

        for line in message.split('\n'):
            assert f"INFO: test_logging_with_multiline_string: {line}" in queue_contents

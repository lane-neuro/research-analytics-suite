import asyncio
import pytest
import logging
import os

import pytest_asyncio

from research_analytics_suite.utils import CustomLogger


class TestCustomLogger:
    @pytest_asyncio.fixture(autouse=True)
    async def setup_class(self):
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
        self.logger._logger.addHandler(self.debug_handler)

        # Set log level based on environment variable
        log_level = os.getenv('PYTHON_LOG_LEVEL', 'DEBUG').upper()
        self.logger._logger.setLevel(getattr(logging, log_level))

    def test_initialize_logger(self):
        assert self.logger._logger is not None
        assert self.logger._logger.level == logging.DEBUG
        assert len(self.logger._logger.handlers) > 0
        assert isinstance(self.logger._logger.handlers[0], logging.StreamHandler)
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

        self.logger.debug("Test debug message")
        self.logger.info("Test info message")
        self.logger.warning("Test warning message")

        await asyncio.sleep(0.1)  # Ensure messages are processed
        queue_contents = []
        while not self.logger.log_message_queue.empty():
            queue_contents.append(await self.logger.log_message_queue.get())

        assert any("ERROR: An error occurred in test_logging_levels: Test error" in msg for msg in queue_contents)
        assert "DEBUG: Test debug message" in queue_contents
        assert "INFO: Test info message" in queue_contents
        assert "WARNING: Test warning message" in queue_contents

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

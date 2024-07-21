from typing import List, Dict
import pytest
from unittest.mock import MagicMock
from research_analytics_suite.hardware_manager.interface.BaseInterface import BaseInterface


class SimulatedHardware:
    """Simulate a hardware environment for integration testing."""

    @staticmethod
    def execute_command(command):
        if 'dummy_detect_command' in command:
            return 'Bus 001 Device 002: ID 1234:5678 Simulated Device'
        elif 'dummy_read_command' in command:
            return 'Simulated Read Data'
        elif 'dummy_write_command' in command:
            return ''
        elif 'dummy_stream_command' in command:
            return 'Simulated Streamed Data'
        elif 'dummy_configure_command' in command:
            return ''
        return 'Unknown Command'


class TestableBaseInterface(BaseInterface):
    def _get_command(self, action: str, identifier: str = '', data: str = '', settings=None):
        if settings is None:
            settings = {}
        if action == 'detect':
            return ['dummy_detect_command']
        elif action == 'read':
            return ['dummy_read_command', identifier]
        elif action == 'write':
            return ['dummy_write_command', identifier, data]
        elif action == 'stream':
            return ['dummy_stream_command', identifier]
        elif action == 'configure':
            return ['dummy_configure_command', identifier] + [f"{k}={v}" for k, v in settings.items()]
        return []

    def _execute_command(self, command: List[str]) -> str:
        return SimulatedHardware.execute_command(command)

    def _parse_output(self, output: str) -> List[Dict[str, str]]:
        if 'Bus' in output and 'Device' in output:
            return [{'device': 'Simulated Device', 'id': '1234:5678'}]
        return [{"dummy_key": "dummy_value"}]  # Dummy implementation for testing


class TestBaseInterfaceIntegration:
    def test_detect(self):
        logger = MagicMock()
        interface = TestableBaseInterface(logger)
        devices = interface.detect()
        assert devices == [{'device': 'Simulated Device', 'id': '1234:5678'}]

    def test_read(self):
        logger = MagicMock()
        interface = TestableBaseInterface(logger)
        data = interface.read('test_identifier')
        assert data == 'Simulated Read Data'

    def test_write(self):
        logger = MagicMock()
        interface = TestableBaseInterface(logger)
        success = interface.write('test_identifier', 'test_data')
        assert success

    def test_stream(self):
        logger = MagicMock()
        interface = TestableBaseInterface(logger)
        data = interface.stream('test_identifier')
        assert data == 'Simulated Streamed Data'

    def test_configure(self):
        logger = MagicMock()
        interface = TestableBaseInterface(logger)
        success = interface.configure('test_identifier', {'setting1': 'value1', 'setting2': 'value2'})
        assert success

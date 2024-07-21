import subprocess

import pytest
from unittest.mock import MagicMock, patch
from research_analytics_suite.hardware_manager.interface.BaseInterface import BaseInterface


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

    def _parse_output(self, output: str):
        return [{"dummy_key": "dummy_value"}]  # Dummy implementation for testing


class TestBaseInterface:
    @pytest.mark.parametrize("os_name", ["Linux", "Darwin", "Windows"])
    @patch('subprocess.run')
    def test_detect(self, mock_subprocess_run, os_name):
        with patch('platform.system', return_value=os_name):
            logger = MagicMock()
            interface = TestableBaseInterface(logger)
            mock_subprocess_run.return_value.stdout = 'Bus 001 Device 002: ID 1234:5678 Test Device'
            devices = interface.detect()
            assert devices == [{"dummy_key": "dummy_value"}]

    @pytest.mark.parametrize("os_name", ["Linux", "Darwin", "Windows"])
    @patch('subprocess.run')
    def test_read(self, mock_subprocess_run, os_name):
        with patch('platform.system', return_value=os_name):
            logger = MagicMock()
            interface = TestableBaseInterface(logger)
            mock_subprocess_run.return_value.stdout = 'Read data'
            data = interface.read('test_identifier')
            assert data == 'Read data'

    @pytest.mark.parametrize("os_name", ["Linux", "Darwin", "Windows"])
    @patch('subprocess.run')
    def test_write(self, mock_subprocess_run, os_name):
        with patch('platform.system', return_value=os_name):
            logger = MagicMock()
            interface = TestableBaseInterface(logger)
            mock_subprocess_run.return_value.stdout = ''
            success = interface.write('test_identifier', 'test_data')
            assert success

    @pytest.mark.parametrize("os_name", ["Linux", "Darwin", "Windows"])
    @patch('subprocess.run')
    def test_stream(self, mock_subprocess_run, os_name):
        with patch('platform.system', return_value=os_name):
            logger = MagicMock()
            interface = TestableBaseInterface(logger)
            mock_subprocess_run.return_value.stdout = 'Streamed data'
            data = interface.stream('test_identifier')
            assert data == 'Streamed data'

    @pytest.mark.parametrize("os_name", ["Linux", "Darwin", "Windows"])
    @patch('subprocess.run')
    def test_configure(self, mock_subprocess_run, os_name):
        with patch('platform.system', return_value=os_name):
            logger = MagicMock()
            interface = TestableBaseInterface(logger)
            mock_subprocess_run.return_value.stdout = ''
            success = interface.configure('test_identifier', {'setting1': 'value1', 'setting2': 'value2'})
            assert success

    @pytest.mark.parametrize("os_name", ["Linux", "Darwin", "Windows"])
    @patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'cmd'))
    def test_detect_error(self, mock_subprocess_run, os_name):
        with patch('platform.system', return_value=os_name):
            logger = MagicMock()
            interface = TestableBaseInterface(logger)
            devices = interface.detect()
            assert devices == []

    @pytest.mark.parametrize("os_name", ["Linux", "Darwin", "Windows"])
    @patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'cmd'))
    def test_read_error(self, mock_subprocess_run, os_name):
        with patch('platform.system', return_value=os_name):
            logger = MagicMock()
            interface = TestableBaseInterface(logger)
            data = interface.read('test_identifier')
            assert data == ''

    @pytest.mark.parametrize("os_name", ["Linux", "Darwin", "Windows"])
    @patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'cmd'))
    def test_write_error(self, mock_subprocess_run, os_name):
        with patch('platform.system', return_value=os_name):
            logger = MagicMock()
            interface = TestableBaseInterface(logger)
            success = interface.write('test_identifier', 'test_data')
            assert not success

    @pytest.mark.parametrize("os_name", ["Linux", "Darwin", "Windows"])
    @patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'cmd'))
    def test_stream_error(self, mock_subprocess_run, os_name):
        with patch('platform.system', return_value=os_name):
            logger = MagicMock()
            interface = TestableBaseInterface(logger)
            data = interface.stream('test_identifier')
            assert data == ''

    @pytest.mark.parametrize("os_name", ["Linux", "Darwin", "Windows"])
    @patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'cmd'))
    def test_configure_error(self, mock_subprocess_run, os_name):
        with patch('platform.system', return_value=os_name):
            logger = MagicMock()
            interface = TestableBaseInterface(logger)
            success = interface.configure('test_identifier', {'setting1': 'value1', 'setting2': 'value2'})
            assert not success

    def test_parse_output(self):
        interface = TestableBaseInterface(MagicMock())
        output = interface._parse_output("some output")
        assert output == [{"dummy_key": "dummy_value"}]

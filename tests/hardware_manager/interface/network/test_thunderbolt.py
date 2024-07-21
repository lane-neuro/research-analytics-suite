import subprocess

import pytest
from unittest.mock import patch, MagicMock
from research_analytics_suite.hardware_manager.interface.network.Thunderbolt import Thunderbolt


@pytest.fixture
def logger():
    return MagicMock()


@pytest.fixture
@patch('platform.system', return_value='Linux')
def thunderbolt_interface(mock_platform_system, logger):
    return Thunderbolt(logger)


class TestThunderbolt:
    @patch('platform.system', return_value='Linux')
    def test_detect_os_linux(self, mock_platform_system, logger):
        interface = Thunderbolt(logger)
        assert interface.os_info == 'linux'

    @patch('platform.system', return_value='Windows')
    def test_detect_os_windows(self, mock_platform_system, logger):
        interface = Thunderbolt(logger)
        assert interface.os_info == 'windows'

    @patch('platform.system', return_value='UnsupportedOS')
    def test_detect_os_unsupported(self, mock_platform_system, logger):
        interface = Thunderbolt(logger)
        assert interface.os_info == 'unsupported'
        interface.logger.error.assert_called_with('Unsupported OS: UnsupportedOS')

    @patch('subprocess.run')
    @patch('platform.system', return_value='Linux')
    def test_detect_success(self, mock_platform_system, mock_subprocess_run, logger):
        mock_subprocess_run.return_value = MagicMock(stdout='00:01.0 Thunderbolt', stderr='')
        interface = Thunderbolt(logger)
        devices = interface.detect()
        assert devices == [{'interface': '00:01.0', 'description': 'Thunderbolt Network Interface'}]
        interface.logger.debug.assert_any_call('Executing command: lspci -nn -D')
        interface.logger.debug.assert_any_call('Command output: 00:01.0 Thunderbolt')
        interface.logger.debug.assert_any_call('Command stderr: ')

    @patch('subprocess.run')
    @patch('platform.system', return_value='Linux')
    def test_detect_failure(self, mock_platform_system, mock_subprocess_run, logger):
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=['lspci', '-nn', '-D'], output='error', stderr='error'
        )
        interface = Thunderbolt(logger)
        with pytest.raises(subprocess.CalledProcessError):
            interface.detect()
        interface.logger.error.assert_any_call("Command 'lspci -nn -D' failed with error: Command '['lspci', '-nn', '-D']' returned non-zero exit status 1.")
        interface.logger.error.assert_any_call('Command stdout: error')
        interface.logger.error.assert_any_call('Command stderr: error')

    @patch('platform.system', return_value='Linux')
    def test_get_command_linux(self, mock_platform_system, logger):
        interface = Thunderbolt(logger)
        command = interface._get_command('list')
        assert command == ['lspci', '-nn', '-D']

    @patch('platform.system', return_value='Windows')
    def test_get_command_windows(self, mock_platform_system, logger):
        interface = Thunderbolt(logger)
        command = interface._get_command('list')
        assert command == ['powershell', 'Get-PnpDevice -Class Net']

    @patch('platform.system', return_value='Darwin')
    def test_get_command_darwin(self, mock_platform_system, logger):
        interface = Thunderbolt(logger)
        command = interface._get_command('list')
        assert command == ['system_profiler', 'SPThunderboltDataType']

    def test_parse_output_linux(self, logger):
        interface = Thunderbolt(logger)
        interface.os_info = 'linux'
        output = "00:01.0 Thunderbolt"
        parsed = interface._parse_output(output)
        assert parsed == [
            {'interface': '00:01.0', 'description': 'Thunderbolt Network Interface'}
        ]

    def test_parse_output_windows(self, logger):
        interface = Thunderbolt(logger)
        interface.os_info = 'windows'
        output = "Name           Thunderbolt\nInstance ID:   PCI\\VEN_8086&DEV_15D2&SUBSYS_383217AA&REV_02"
        parsed = interface._parse_output(output)
        assert parsed == [
            {'interface': 'Name', 'description': 'Thunderbolt Network Interface'}
        ]

    def test_parse_output_darwin(self, logger):
        interface = Thunderbolt(logger)
        interface.os_info = 'darwin'
        output = "Port:\n  Address: 00:11:22:33:44:55\n"
        parsed = interface._parse_output(output)
        assert parsed == [
            {'interface': '00:11:22:33:44:55', 'description': 'Thunderbolt Network Interface'}
        ]

    def test_parse_output_empty(self, logger):
        interface = Thunderbolt(logger)
        interface.os_info = 'windows'
        output = ""
        parsed = interface._parse_output(output)
        assert parsed == []

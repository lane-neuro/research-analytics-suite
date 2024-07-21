import pytest
from unittest.mock import patch, MagicMock
import subprocess
from typing import List, Dict, Any

from research_analytics_suite.hardware_manager.interface.network.NetworkInterface import NetworkInterface


class ConcreteNetworkInterface(NetworkInterface):
    def detect(self) -> List[Dict[str, str]]:
        return []

    def _get_command(self, action: str, identifier: str = '', data: str = '', settings: Any = None) -> List[str]:
        return []

    def _parse_output(self, output: str) -> List[Dict[str, str]]:
        return []


@pytest.fixture
def logger():
    return MagicMock()


@pytest.fixture
def network_interface(logger):
    return ConcreteNetworkInterface(logger)


class TestNetworkInterface:
    @patch('platform.system')
    def test_detect_os_linux(self, mock_platform_system, network_interface):
        mock_platform_system.return_value = 'Linux'
        os_info = network_interface._detect_os()
        assert os_info == 'linux'

    @patch('platform.system')
    def test_detect_os_windows(self, mock_platform_system, network_interface):
        mock_platform_system.return_value = 'Windows'
        os_info = network_interface._detect_os()
        assert os_info == 'windows'

    @patch('platform.system')
    def test_detect_os_unsupported(self, mock_platform_system, network_interface):
        mock_platform_system.return_value = 'UnsupportedOS'
        os_info = network_interface._detect_os()
        assert os_info == 'unsupported'
        network_interface.logger.error.assert_called_with('Unsupported OS: UnsupportedOS')

    @patch('subprocess.run')
    def test_execute_command_success(self, mock_subprocess_run, network_interface):
        mock_subprocess_run.return_value = MagicMock(stdout='output', stderr='')
        result = network_interface._execute_command(['echo', 'test'])
        assert result == 'output'
        network_interface.logger.debug.assert_any_call('Executing command: echo test')
        network_interface.logger.debug.assert_any_call('Command output: output')
        network_interface.logger.debug.assert_any_call('Command stderr: ')

    @patch('subprocess.run')
    def test_execute_command_failure(self, mock_subprocess_run, network_interface):
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=['echo', 'test'], output='error', stderr='error'
        )
        with pytest.raises(subprocess.CalledProcessError):
            network_interface._execute_command(['echo', 'test'])
        network_interface.logger.error.assert_any_call("Command 'echo test' failed with error: Command '['echo', 'test']' returned non-zero exit status 1.")
        network_interface.logger.error.assert_any_call('Command stdout: error')
        network_interface.logger.error.assert_any_call('Command stderr: error')

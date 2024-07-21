import pytest
from unittest.mock import patch, MagicMock
import subprocess
from typing import List, Dict, Any

from research_analytics_suite.hardware_manager.interface.BaseInterface import BaseInterface


class ConcreteBaseInterface(BaseInterface):
    def detect(self) -> List[Dict[str, str]]:
        return []

    def _get_command(self, action: str, identifier: str = '', data: str = '', settings: Any = None) -> List[str]:
        return []

    def _parse_output(self, output: str) -> List[Dict[str, str]]:
        return []

    def _get_command_linux(self, action: str, identifier: str = '', data: str = '', settings=None) -> List[str]:
        return []

    def _get_command_windows(self, action: str, identifier: str = '', data: str = '', settings=None) -> List[str]:
        return []

    def _get_command_darwin(self, action: str, identifier: str = '', data: str = '', settings=None) -> List[str]:
        return []


@pytest.fixture
def logger():
    return MagicMock()


@pytest.fixture
def base_interface(logger):
    return ConcreteBaseInterface(logger)


class TestBaseInterface:
    @patch('platform.system')
    def test_detect_os_linux(self, mock_platform_system, base_interface):
        mock_platform_system.return_value = 'Linux'
        os_info = base_interface._detect_os()
        assert os_info == 'linux'

    @patch('platform.system')
    def test_detect_os_windows(self, mock_platform_system, base_interface):
        mock_platform_system.return_value = 'Windows'
        os_info = base_interface._detect_os()
        assert os_info == 'windows'

    @patch('platform.system')
    def test_detect_os_unsupported(self, mock_platform_system, base_interface):
        mock_platform_system.return_value = 'UnsupportedOS'
        os_info = base_interface._detect_os()
        assert os_info == 'unsupported'
        base_interface.logger.error.assert_called_with('Unsupported OS: UnsupportedOS')

    @patch('subprocess.run')
    def test_execute_command_success(self, mock_subprocess_run, base_interface):
        mock_subprocess_run.return_value = MagicMock(stdout='output', stderr='')
        result = base_interface._execute_command(['echo', 'test'])
        assert result == 'output'
        base_interface.logger.debug.assert_any_call('Executing command: echo test')
        base_interface.logger.debug.assert_any_call('Command output: output')
        base_interface.logger.debug.assert_any_call('Command stderr: ')

    @patch('subprocess.run')
    def test_execute_command_failure(self, mock_subprocess_run, base_interface):
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=['echo', 'test'], output='error', stderr='error'
        )
        with pytest.raises(subprocess.CalledProcessError):
            base_interface._execute_command(['echo', 'test'])
        base_interface.logger.error.assert_any_call("Command 'echo test' failed with error: Command '['echo', 'test']' returned non-zero exit status 1.")
        base_interface.logger.error.assert_any_call('Command stdout: error')
        base_interface.logger.error.assert_any_call('Command stderr: error')

import subprocess

import pytest
from unittest.mock import patch, MagicMock

from tests.hardware_manager.interface.display.concrete_display_interface import ConcreteDisplayInterface


@pytest.fixture
def logger():
    return MagicMock()


@pytest.fixture
def display_interface(logger):
    return ConcreteDisplayInterface(logger)


class TestDisplayInterface:
    @patch('platform.system', return_value='Linux')
    def test_detect_os_linux(self, mock_platform_system, display_interface):
        os_info = display_interface._detect_os()
        assert os_info == 'linux'

    @patch('platform.system', return_value='Windows')
    def test_detect_os_windows(self, mock_platform_system, display_interface):
        os_info = display_interface._detect_os()
        assert os_info == 'windows'

    @patch('platform.system', return_value='UnsupportedOS')
    def test_detect_os_unsupported(self, mock_platform_system, display_interface):
        os_info = display_interface._detect_os()
        assert os_info == 'unsupported'
        display_interface.logger.error.assert_called_with('Unsupported OS: UnsupportedOS')

    @patch('subprocess.run')
    def test_execute_command_success(self, mock_subprocess_run, display_interface):
        mock_subprocess_run.return_value = MagicMock(stdout='output', stderr='')
        result = display_interface._execute_command(['echo', 'test'])
        assert result == 'output'
        display_interface.logger.debug.assert_any_call('Executing command: echo test')
        display_interface.logger.debug.assert_any_call('Command output: output')
        display_interface.logger.debug.assert_any_call('Command stderr: ')

    @patch('subprocess.run')
    def test_execute_command_failure(self, mock_subprocess_run, display_interface):
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=['echo', 'test'], output='error', stderr='error'
        )
        with pytest.raises(subprocess.CalledProcessError):
            display_interface._execute_command(['echo', 'test'])
        display_interface.logger.error.assert_any_call("Command 'echo test' failed with error: Command '['echo', 'test']' returned non-zero exit status 1.")
        display_interface.logger.error.assert_any_call('Command stdout: error')
        display_interface.logger.error.assert_any_call('Command stderr: error')

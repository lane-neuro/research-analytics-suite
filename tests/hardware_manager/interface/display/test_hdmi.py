import subprocess

import pytest
from unittest.mock import patch, MagicMock
from research_analytics_suite.hardware_manager.interface.display.HDMI import HDMI


@pytest.fixture
def logger():
    return MagicMock()


@pytest.fixture
@patch('platform.system', return_value='Linux')
def hdmi_interface(mock_platform_system, logger):
    return HDMI(logger)


class TestHDMI:
    @patch('platform.system', return_value='Linux')
    def test_detect_os_linux(self, mock_platform_system, logger):
        interface = HDMI(logger)
        assert interface.os_info == 'linux'

    @patch('platform.system', return_value='Windows')
    def test_detect_os_windows(self, mock_platform_system, logger):
        interface = HDMI(logger)
        assert interface.os_info == 'windows'

    @patch('platform.system', return_value='UnsupportedOS')
    def test_detect_os_unsupported(self, mock_platform_system, logger):
        interface = HDMI(logger)
        assert interface.os_info == 'unsupported'
        interface.logger.error.assert_called_with('Unsupported OS: UnsupportedOS')

    @patch('subprocess.run')
    @patch('platform.system', return_value='Linux')
    def test_detect_success(self, mock_platform_system, mock_subprocess_run, logger):
        mock_subprocess_run.return_value = MagicMock(stdout='HDMI-1 connected\nHDMI-2 disconnected', stderr='')
        interface = HDMI(logger)
        devices = interface.detect()
        assert devices == [{'interface': 'HDMI-1', 'description': 'HDMI Interface'}]
        interface.logger.debug.assert_any_call('Executing command: xrandr')
        interface.logger.debug.assert_any_call('Command output: HDMI-1 connected\nHDMI-2 disconnected')
        interface.logger.debug.assert_any_call('Command stderr: ')

    @patch('subprocess.run')
    @patch('platform.system', return_value='Linux')
    def test_detect_failure(self, mock_platform_system, mock_subprocess_run, logger):
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=['xrandr'], output='error', stderr='error'
        )
        interface = HDMI(logger)
        with pytest.raises(subprocess.CalledProcessError):
            interface.detect()
        interface.logger.error.assert_any_call("Command 'xrandr' failed with error: Command '['xrandr']' returned non-zero exit status 1.")
        interface.logger.error.assert_any_call('Command stdout: error')
        interface.logger.error.assert_any_call('Command stderr: error')

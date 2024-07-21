import subprocess

import pytest
from unittest.mock import patch, MagicMock
from research_analytics_suite.hardware_manager.interface.network.Wireless import Wireless


@pytest.fixture
def logger():
    return MagicMock()


@pytest.fixture
@patch('platform.system', return_value='Linux')
def wireless_interface(mock_platform_system, logger):
    return Wireless(logger)


class TestWireless:
    @patch('platform.system', return_value='Linux')
    def test_detect_os_linux(self, mock_platform_system, logger):
        interface = Wireless(logger)
        assert interface.os_info == 'linux'

    @patch('platform.system', return_value='Windows')
    def test_detect_os_windows(self, mock_platform_system, logger):
        interface = Wireless(logger)
        assert interface.os_info == 'windows'

    @patch('platform.system', return_value='UnsupportedOS')
    def test_detect_os_unsupported(self, mock_platform_system, logger):
        interface = Wireless(logger)
        assert interface.os_info == 'unsupported'
        interface.logger.error.assert_called_with('Unsupported OS: UnsupportedOS')

    @patch('subprocess.run')
    @patch('platform.system', return_value='Linux')
    def test_detect_success(self, mock_platform_system, mock_subprocess_run, logger):
        mock_subprocess_run.return_value = MagicMock(stdout='wlan0     IEEE 802.11  ESSID:"test"', stderr='')
        interface = Wireless(logger)
        devices = interface.detect()
        assert devices == [{'interface': 'wlan0', 'description': 'Wireless Interface'}]
        interface.logger.debug.assert_any_call('Executing command: iwconfig')
        interface.logger.debug.assert_any_call('Command output: wlan0     IEEE 802.11  ESSID:"test"')
        interface.logger.debug.assert_any_call('Command stderr: ')

    @patch('subprocess.run')
    @patch('platform.system', return_value='Linux')
    def test_detect_failure(self, mock_platform_system, mock_subprocess_run, logger):
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=['iwconfig'], output='error', stderr='error'
        )
        interface = Wireless(logger)
        with pytest.raises(subprocess.CalledProcessError):
            interface.detect()
        interface.logger.error.assert_any_call("Command 'iwconfig' failed with error: Command '['iwconfig']' returned non-zero exit status 1.")
        interface.logger.error.assert_any_call('Command stdout: error')
        interface.logger.error.assert_any_call('Command stderr: error')

    @patch('platform.system', return_value='Linux')
    def test_get_command_linux(self, mock_platform_system, logger):
        interface = Wireless(logger)
        command = interface._get_command('list')
        assert command == ['iwconfig']

    @patch('platform.system', return_value='Windows')
    def test_get_command_windows(self, mock_platform_system, logger):
        interface = Wireless(logger)
        command = interface._get_command('list')
        assert command == ['powershell', 'Get-NetAdapter -InterfaceDescription *Wi-Fi*']

    @patch('platform.system', return_value='Darwin')
    def test_get_command_darwin(self, mock_platform_system, logger):
        interface = Wireless(logger)
        command = interface._get_command('list')
        assert command == ['networksetup', '-listallhardwareports']

    @patch('platform.system', return_value='Linux')
    def test_connect_linux(self, mock_platform_system, logger):
        interface = Wireless(logger)
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout='', stderr='')
            interface.connect('wlan0', 'test_ssid', 'test_password')
            mock_run.assert_called_with(['nmcli', 'dev', 'wifi', 'connect', 'test_ssid', 'password', 'test_password'], capture_output=True, text=True, shell=False, check=True)

    @patch('platform.system', return_value='Windows')
    def test_connect_windows(self, mock_platform_system, logger):
        interface = Wireless(logger)
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout='', stderr='')
            interface.connect('Wi-Fi', 'test_ssid', 'test_password')
            mock_run.assert_called_with(['powershell', 'netsh wlan connect name=test_ssid key=test_password'], capture_output=True, text=True, shell=True, check=True)

    @patch('platform.system', return_value='Darwin')
    def test_connect_darwin(self, mock_platform_system, logger):
        interface = Wireless(logger)
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout='', stderr='')
            interface.connect('en0', 'test_ssid', 'test_password')
            mock_run.assert_called_with(['networksetup', '-setairportnetwork', 'en0', 'test_ssid', 'test_password'], capture_output=True, text=True, shell=False, check=True)

    @patch('platform.system', return_value='Linux')
    def test_send_data_linux(self, mock_platform_system, logger):
        interface = Wireless(logger)
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout='', stderr='')
            interface.send_data('wlan0', 'test data')
            mock_run.assert_called_with(['echo', 'test data', '>', '/dev/wlan0'], capture_output=True, text=True, shell=False, check=True)

    @patch('platform.system', return_value='Windows')
    def test_send_data_windows(self, mock_platform_system, logger):
        interface = Wireless(logger)
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout='', stderr='')
            interface.send_data('Wi-Fi', 'test data')
            mock_run.assert_called_with(['powershell', 'echo test data > Wi-Fi'], capture_output=True, text=True, shell=True, check=True)

    @patch('platform.system', return_value='Darwin')
    def test_send_data_darwin(self, mock_platform_system, logger):
        interface = Wireless(logger)
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout='', stderr='')
            interface.send_data('en0', 'test data')
            mock_run.assert_called_with(['sh', '-c', 'echo test data > en0'], capture_output=True, text=True, shell=False, check=True)

    @patch('platform.system', return_value='Linux')
    def test_receive_data_linux(self, mock_platform_system, logger):
        interface = Wireless(logger)
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout='test data', stderr='')
            data = interface.receive_data('wlan0')
            assert data == 'test data'
            mock_run.assert_called_with(['cat', '/dev/wlan0'], capture_output=True, text=True, shell=False, check=True)

    @patch('platform.system', return_value='Windows')
    def test_receive_data_windows(self, mock_platform_system, logger):
        interface = Wireless(logger)
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout='test data', stderr='')
            data = interface.receive_data('Wi-Fi')
            assert data == 'test data'
            mock_run.assert_called_with(['powershell', 'Get-Content Wi-Fi'], capture_output=True, text=True, shell=True, check=True)

    @patch('platform.system', return_value='Darwin')
    def test_receive_data_darwin(self, mock_platform_system, logger):
        interface = Wireless(logger)
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout='test data', stderr='')
            data = interface.receive_data('en0')
            assert data == 'test data'
            mock_run.assert_called_with(['sh', '-c', 'cat en0'], capture_output=True, text=True, shell=False, check=True)

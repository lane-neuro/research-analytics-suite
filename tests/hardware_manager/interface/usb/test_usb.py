import pytest
from unittest.mock import patch, MagicMock
import subprocess

from research_analytics_suite.hardware_manager.interface.usb.USB import USB


@pytest.fixture
def logger():
    return MagicMock()


@pytest.fixture
@patch('platform.system', return_value='Linux')
def usb_interface(mock_platform_system, logger):
    return USB(logger)


class TestUSB:
    @patch('platform.system', return_value='Linux')
    def test_detect_os_linux(self, mock_platform_system, logger):
        interface = USB(logger)
        assert interface.os_info == 'linux'

    @patch('platform.system', return_value='Windows')
    def test_detect_os_windows(self, mock_platform_system, logger):
        interface = USB(logger)
        assert interface.os_info == 'windows'

    @patch('platform.system', return_value='UnsupportedOS')
    def test_detect_os_unsupported(self, mock_platform_system, logger):
        interface = USB(logger)
        assert interface.os_info == 'unsupported'
        interface.logger.error.assert_called_with('Unsupported OS: UnsupportedOS')

    @patch('subprocess.run')
    @patch('platform.system', return_value='Linux')
    def test_detect_success(self, mock_platform_system, mock_subprocess_run, logger):
        mock_subprocess_run.return_value = MagicMock(stdout='Bus 001 Device 002: ID 8087:0024 Intel Corp.', stderr='')
        interface = USB(logger)
        devices = interface.detect()
        assert devices == [{'bus': '001', 'device': '002', 'vendor_id': '8087', 'product_id': '0024', 'description': 'Intel Corp.'}]

    @patch('subprocess.run')
    @patch('platform.system', return_value='Linux')
    def test_detect_failure(self, mock_platform_system, mock_subprocess_run, logger):
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=['lsusb'], output='error', stderr='error'
        )
        interface = USB(logger)
        with pytest.raises(subprocess.CalledProcessError):
            interface.detect()
        interface.logger.error.assert_any_call("Command 'lsusb' failed with error: Command '['lsusb']' returned non-zero exit status 1.")
        interface.logger.error.assert_any_call('Command stdout: error')
        interface.logger.error.assert_any_call('Command stderr: error')

    @patch('platform.system', return_value='Linux')
    def test_get_command_linux(self, mock_platform_system, logger):
        interface = USB(logger)
        command = interface._get_command('list')
        assert command == ['lsusb']

    @patch('platform.system', return_value='Windows')
    def test_get_command_windows(self, mock_platform_system, logger):
        interface = USB(logger)
        command = interface._get_command('list')
        assert command == ['powershell', '-Command', 'Get-PnpDevice -Class USB | Format-Table -AutoSize -Wrap']

    @patch('platform.system', return_value='Darwin')
    def test_get_command_darwin(self, mock_platform_system, logger):
        interface = USB(logger)
        command = interface._get_command('list')
        assert command == ['system_profiler', 'SPUSBDataType']

    def test_parse_output_linux(self, logger):
        interface = USB(logger)
        interface.os_info = 'linux'
        output = "Bus 001 Device 002: ID 8087:0024 Intel Corp.\nBus 002 Device 003: ID 1234:5678 Test Device"
        parsed = interface._parse_output(output)
        assert parsed == [
            {'bus': '001', 'device': '002', 'vendor_id': '8087', 'product_id': '0024', 'description': 'Intel Corp.'},
            {'bus': '002', 'device': '003', 'vendor_id': '1234', 'product_id': '5678', 'description': 'Test Device'}
        ]

    def test_parse_output_windows(self, logger):
        interface = USB(logger)
        interface.os_info = 'windows'
        output = "Status     Class           FriendlyName        InstanceId\n" \
                 "------     -----           ------------        ----------\n" \
                 "OK         USB             USB Composite Device USB\\VID_1234&PID_5678\\12345678\n" \
                 "Unknown    USB             Unknown USB Device  USB\\VID_8765&PID_4321\\87654321"
        parsed = interface._parse_output(output)
        assert parsed == [
            {'status': 'OK', 'class': 'USB', 'friendly_name': 'USB Composite Device',
             'instance_id': 'USB\\VID_1234&PID_5678\\12345678'},
            {'status': 'Unknown', 'class': 'USB', 'friendly_name': 'Unknown USB Device',
             'instance_id': 'USB\\VID_8765&PID_4321\\87654321'}
        ]

    def test_parse_output_windows_truncated_lines(self, logger):
        interface = USB(logger)
        interface.os_info = 'windows'
        output = "Status     Class           FriendlyName        InstanceId\n" \
                 "------     -----           ------------        ----------\n" \
                 "OK         USB             USB Composite Device USB\\VID_1234&PID_5678\\12345678\n" \
                 "                                                                               9E1CF5001BC3\n" \
                 "                                                                               00\\3&11583659&0&A0\n" \
                 "                                                                               A1\\4&38AB2860&0&0308"
        parsed = interface._parse_output(output)
        assert parsed == [
            {'status': 'OK', 'class': 'USB', 'friendly_name': 'USB Composite Device',
             'instance_id': 'USB\\VID_1234&PID_5678\\123456789E1CF5001BC300\\3&11583659&0&A0A1\\4&38AB2860&0&0308'}
        ]

    def test_parse_output_darwin(self, logger):
        interface = USB(logger)
        interface.os_info = 'darwin'
        output = "USB:\n\n    USB 3.0 Bus:\n\n        Host Controller Driver: AppleUSBXHCITR\n" \
                 "        PCI Device ID: 0x1e31 \n        PCI Revision ID: 0x0004 \n        PCI Vendor ID: 0x8086 \n" \
                 "            USB 2.0 Hub:\n\n              Product ID: 0x0024\n              Vendor ID: 0x8087  (Intel Corporation)\n" \
                 "              Version: 0.05\n              Speed: Up to 480 Mb/sec\n              Location ID: 0x1a120000 / 2\n" \
                 "              Current Available (mA): 500\n              Current Required (mA): 0\n              Extra Operating Current (mA): 0\n"
        parsed = interface._parse_output(output)
        assert parsed == [
            {'product_id': '0x0024', 'vendor_id': '0x8087', 'vendor_name': '(Intel Corporation)', 'location_id': '0x1a120000 / 2', 'speed': 'Up to 480 Mb/sec'}
        ]

    def test_parse_output_empty(self, logger):
        interface = USB(logger)
        interface.os_info = 'windows'
        output = ""
        parsed = interface._parse_output(output)
        assert parsed == []

    @patch('platform.system', return_value='Linux')
    def test_read_stream_data_linux(self, mock_platform_system, logger):
        interface = USB(logger)
        device_identifier = 'ttyUSB0'
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout='stream data', stderr='')
            output = interface.read_stream_data(device_identifier)
            assert output == 'stream data'
            mock_run.assert_called_with(['cat', f'/dev/{device_identifier}'], capture_output=True, text=True, shell=False, check=True)

    @patch('platform.system', return_value='Windows')
    def test_read_stream_data_windows(self, mock_platform_system, logger):
        interface = USB(logger)
        device_identifier = 'COM1'
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout='stream data', stderr='')
            output = interface.read_stream_data(device_identifier)
            assert output == 'stream data'
            mock_run.assert_called_with(['powershell', '-Command', f'Get-Content -Path \\\\.\\{device_identifier}'], capture_output=True, text=True, shell=True, check=True)

    @patch('platform.system', return_value='Darwin')
    def test_read_stream_data_darwin(self, mock_platform_system, logger):
        interface = USB(logger)
        device_identifier = 'tty.usbserial'
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout='stream data', stderr='')
            output = interface.read_stream_data(device_identifier)
            assert output == 'stream data'
            mock_run.assert_called_with(['cat', f'/dev/{device_identifier}'], capture_output=True, text=True, shell=False, check=True)

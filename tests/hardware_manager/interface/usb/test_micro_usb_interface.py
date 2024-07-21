import pytest
from unittest.mock import patch, MagicMock
import subprocess
from typing import List, Dict, Any

from research_analytics_suite.hardware_manager.interface.usb.MicroUSBInterface import MicroUSBInterface


@pytest.fixture
def logger():
    return MagicMock()


@pytest.fixture
@patch('platform.system', return_value='Linux')
def microusb_interface(mock_platform_system, logger):
    return MicroUSBInterface(logger)


class TestMicroUSBInterface:
    @patch('platform.system', return_value='Linux')
    def test_detect_os_linux(self, mock_platform_system, logger):
        interface = MicroUSBInterface(logger)
        assert interface.os_info == 'linux'

    @patch('platform.system', return_value='Windows')
    def test_detect_os_windows(self, mock_platform_system, logger):
        interface = MicroUSBInterface(logger)
        assert interface.os_info == 'windows'

    @patch('platform.system', return_value='UnsupportedOS')
    def test_detect_os_unsupported(self, mock_platform_system, logger):
        interface = MicroUSBInterface(logger)
        assert interface.os_info == 'unsupported'
        interface.logger.error.assert_called_with('Unsupported OS: UnsupportedOS')

    @patch('subprocess.run')
    @patch('platform.system', return_value='Linux')
    def test_detect_success(self, mock_platform_system, mock_subprocess_run, logger):
        mock_subprocess_run.return_value = MagicMock(stdout='Bus 001 Device 002: ID 8087:0024 Intel Corp. Micro-USB Device', stderr='')
        interface = MicroUSBInterface(logger)
        devices = interface.detect()
        assert devices == [{'bus': '001', 'device': '002', 'vendor_id': '8087', 'product_id': '0024', 'description': 'Intel Corp. Micro-USB Device'}]
        interface.logger.debug.assert_any_call('Executing command: lsusb')
        interface.logger.debug.assert_any_call('Command output: Bus 001 Device 002: ID 8087:0024 Intel Corp. Micro-USB Device')
        interface.logger.debug.assert_any_call('Command stderr: ')

    @patch('subprocess.run')
    @patch('platform.system', return_value='Linux')
    def test_detect_failure(self, mock_platform_system, mock_subprocess_run, logger):
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=['lsusb'], output='error', stderr='error'
        )
        interface = MicroUSBInterface(logger)
        with pytest.raises(subprocess.CalledProcessError):
            interface.detect()
        interface.logger.error.assert_any_call("Command 'lsusb' failed with error: Command '['lsusb']' returned non-zero exit status 1.")
        interface.logger.error.assert_any_call('Command stdout: error')
        interface.logger.error.assert_any_call('Command stderr: error')

    @patch('platform.system', return_value='Linux')
    def test_get_command_linux(self, mock_platform_system, logger):
        interface = MicroUSBInterface(logger)
        command = interface._get_command('list')
        assert command == ['lsusb']

    @patch('platform.system', return_value='Windows')
    def test_get_command_windows(self, mock_platform_system, logger):
        interface = MicroUSBInterface(logger)
        command = interface._get_command('list')
        assert command == ['powershell', 'Get-PnpDevice -Class USB']

    @patch('platform.system', return_value='Darwin')
    def test_get_command_darwin(self, mock_platform_system, logger):
        interface = MicroUSBInterface(logger)
        command = interface._get_command('list')
        assert command == ['system_profiler', 'SPUSBDataType']

    def test_parse_output_linux(self, logger):
        interface = MicroUSBInterface(logger)
        interface.os_info = 'linux'
        output = "Bus 001 Device 002: ID 8087:0024 Intel Corp. Micro-USB Device\nBus 002 Device 003: ID 1234:5678 Test Micro-USB Device"
        parsed = interface._parse_output(output)
        assert parsed == [
            {'bus': '001', 'device': '002', 'vendor_id': '8087', 'product_id': '0024', 'description': 'Intel Corp. Micro-USB Device'},
            {'bus': '002', 'device': '003', 'vendor_id': '1234', 'product_id': '5678', 'description': 'Test Micro-USB Device'}
        ]

    def test_parse_output_windows(self, logger):
        interface = MicroUSBInterface(logger)
        interface.os_info = 'windows'
        output = "Status     Class           FriendlyName        InstanceId\n" \
                 "------     -----           ------------        ----------\n" \
                 "OK         USB             Micro-USB Device    USB\\VID_1234&PID_5678\\12345678"
        parsed = interface._parse_output(output)
        assert parsed == [
            {'status': 'OK', 'class': 'USB', 'friendly_name': 'Micro-USB Device', 'instance_id': 'USB\\VID_1234&PID_5678\\12345678'}
        ]

    def test_parse_output_darwin(self, logger):
        interface = MicroUSBInterface(logger)
        interface.os_info = 'darwin'
        output = "USB:\n\n    USB 3.0 Bus:\n\n        Host Controller Driver: AppleUSBXHCITR\n" \
                 "        PCI Device ID: 0x1e31 \n        PCI Revision ID: 0x0004 \n        PCI Vendor ID: 0x8086 \n" \
                 "            Micro-USB Hub:\n\n              Product ID: 0x0024\n              Vendor ID: 0x8087  (Intel Corporation)\n" \
                 "              Version: 0.05\n              Speed: Up to 480 Mb/sec\n              Location ID: 0x1a120000 / 2\n" \
                 "              Current Available (mA): 500\n              Current Required (mA): 0\n              Extra Operating Current (mA): 0\n"
        parsed = interface._parse_output(output)
        assert parsed == [
            {'product_id': '0x0024', 'vendor_id': '0x8087', 'vendor_name': '(Intel Corporation)', 'location_id': '0x1a120000 / 2', 'speed': 'Up to 480 Mb/sec'}
        ]

    def test_parse_output_empty(self, logger):
        interface = MicroUSBInterface(logger)
        interface.os_info = 'windows'
        output = ""
        parsed = interface._parse_output(output)
        assert parsed == []

    @patch('platform.system', return_value='Linux')
    def test_read_stream_data_linux(self, mock_platform_system, logger):
        interface = MicroUSBInterface(logger)
        device_identifier = 'ttyUSB0'
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout='stream data', stderr='')
            output = interface.read_stream_data(device_identifier)
            assert output == 'stream data'
            mock_run.assert_called_with(['cat', f'/dev/{device_identifier}'], capture_output=True, text=True, shell=False, check=True)

    @patch('platform.system', return_value='Windows')
    def test_read_stream_data_windows(self, mock_platform_system, logger):
        interface = MicroUSBInterface(logger)
        device_identifier = 'COM1'
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout='stream data', stderr='')
            output = interface.read_stream_data(device_identifier)
            assert output == 'stream data'
            mock_run.assert_called_with(['powershell', f'Get-Content -Path \\\\.\\{device_identifier}'], capture_output=True, text=True, shell=True, check=True)

    @patch('platform.system', return_value='Darwin')
    def test_read_stream_data_darwin(self, mock_platform_system, logger):
        interface = MicroUSBInterface(logger)
        device_identifier = 'tty.usbserial'
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout='stream data', stderr='')
            output = interface.read_stream_data(device_identifier)
            assert output == 'stream data'
            mock_run.assert_called_with(['cat', f'/dev/{device_identifier}'], capture_output=True, text=True, shell=False, check=True)

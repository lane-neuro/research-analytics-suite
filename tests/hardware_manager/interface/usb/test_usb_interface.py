import pytest
from unittest import mock
import subprocess
from research_analytics_suite.hardware_manager.interface.usb.USBInterface import USBInterface


def sort_dicts_by_keys(list_of_dicts):
    return [dict(sorted(d.items())) for d in list_of_dicts]


class TestUSBInterface:
    @pytest.fixture
    def logger(self):
        with mock.patch('research_analytics_suite.utils.CustomLogger') as logger:
            yield logger

    @pytest.fixture
    def usb_interface(self, logger):
        with mock.patch('platform.system', return_value='Linux'):
            return USBInterface(logger)

    @pytest.mark.parametrize("os_name,command_output,expected_result", [
        ('Linux', "Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub\n",
         [{'bus': '001', 'device': '001', 'id': '1d6b:0002', 'description': 'Linux Foundation 2.0 root hub'}]),
        ('Windows', "Status OK USB Composite Device\nStatus OK USB Root Hub\n",
         [{'name': 'USB Composite Device', 'status': 'Status OK'}, {'name': 'USB Root Hub', 'status': 'Status OK'}]),
        ('Darwin', "USB:\n\n    USB 3.0 Bus:\n\n        USB 2.0 Hub:\n\n            Product ID: 0x1234\n",
         [{'description': 'USB 2.0 Hub', 'Product ID': '0x1234'}])
    ])
    def test_detect_usb_success(self, os_name, command_output, expected_result, logger):
        with mock.patch('platform.system', return_value=os_name):
            usb_interface = USBInterface(logger)
            with mock.patch('subprocess.run', return_value=mock.Mock(stdout=command_output, returncode=0)):
                result = usb_interface.detect()
                assert sort_dicts_by_keys(result) == sort_dicts_by_keys(expected_result)
                logger.info.assert_any_call(f"Detected devices: {result}")

    @pytest.mark.parametrize("os_name", ['Linux', 'Windows', 'Darwin'])
    def test_detect_usb_failure(self, os_name, logger):
        with mock.patch('platform.system', return_value=os_name):
            usb_interface = USBInterface(logger)
            with mock.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'cmd')):
                result = usb_interface.detect()
                assert result == []
                logger.error.assert_any_call(f"Failed to detect devices: Command 'cmd' returned non-zero exit status 1.")

    @pytest.mark.parametrize("os_name,command_output,expected_result", [
        ('Linux', "Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub\n",
         [{'bus': '001', 'device': '001', 'id': '1d6b:0002', 'description': 'Linux Foundation 2.0 root hub'}]),
        ('Windows', "Status OK USB Composite Device\nStatus OK USB Root Hub\n",
         [{'name': 'USB Composite Device', 'status': 'Status OK'}, {'name': 'USB Root Hub', 'status': 'Status OK'}]),
        ('Darwin', "USB:\n\n    USB 3.0 Bus:\n\n        USB 2.0 Hub:\n\n            Product ID: 0x1234\n",
         [{'description': 'USB 2.0 Hub', 'Product ID': '0x1234'}])
    ])
    def test_parse_output(self, os_name, command_output, expected_result, logger):
        with mock.patch('platform.system', return_value=os_name):
            usb_interface = USBInterface(logger)
            result = usb_interface._parse_output(command_output)
            assert sort_dicts_by_keys(result) == sort_dicts_by_keys(expected_result)

    def test_unsupported_os(self, logger):
        with mock.patch('platform.system', return_value='unsupportedos'):
            usb_interface = USBInterface(logger)
            result = usb_interface.detect()
            assert result == []
            logger.error.assert_any_call("Unsupported OS: unsupportedos")

    def test_initialization(self, usb_interface, logger):
        assert usb_interface.logger == logger
        assert usb_interface.os_info == 'linux'

    @pytest.mark.parametrize("os_name,command_output,identifier,expected_result", [
        ('Linux', "Product Description", "1-1", "Product Description"),
        ('Windows', "FriendlyName", "1-1", "FriendlyName"),
        ('Darwin', "Product Description", "1-1", "Product Description")
    ])
    def test_read_success(self, os_name, command_output, identifier, expected_result, logger):
        with mock.patch('platform.system', return_value=os_name):
            usb_interface = USBInterface(logger)
            with mock.patch('subprocess.run', return_value=mock.Mock(stdout=command_output, returncode=0)):
                result = usb_interface.read(identifier)
                assert result == expected_result

    @pytest.mark.parametrize("os_name,identifier", [
        ('Linux', "1-1"),
        ('Windows', "1-1"),
        ('Darwin', "1-1")
    ])
    def test_read_failure(self, os_name, identifier, logger):
        with mock.patch('platform.system', return_value=os_name):
            usb_interface = USBInterface(logger)
            with mock.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'cmd')):
                result = usb_interface.read(identifier)
                assert result == ""

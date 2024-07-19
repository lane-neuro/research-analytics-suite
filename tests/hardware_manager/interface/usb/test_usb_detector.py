import pytest
from unittest import mock
import platform
import subprocess

from research_analytics_suite.hardware_manager.interface.usb import USBDetector


class TestUSBDetector:
    @pytest.fixture
    def logger(self):
        with mock.patch('research_analytics_suite.utils.CustomLogger') as logger:
            yield logger

    @pytest.fixture
    def usb_detector(self, logger):
        with mock.patch('platform.system', return_value='linux'):
            return USBDetector(logger)

    def test_initialization(self, usb_detector, logger):
        assert usb_detector.logger == logger
        assert usb_detector.os_info == 'linux'

    def test_detect_usb_linux(self, usb_detector, logger):
        with mock.patch('platform.system', return_value='linux'):
            with mock.patch.object(usb_detector, '_detect_usb_linux', return_value=[{'name': 'USB Device', 'id': '1234'}]):
                result = usb_detector.detect_usb()
                assert result == [{'name': 'USB Device', 'id': '1234'}]
                logger.info.assert_any_call("Detecting USB devices...")

    def test_detect_usb_windows(self, logger):
        with mock.patch('platform.system', return_value='windows'):
            usb_detector = USBDetector(logger)
            with mock.patch.object(usb_detector, '_detect_usb_windows', return_value=[{'name': 'USB Device', 'id': '5678'}]):
                result = usb_detector.detect_usb()
                assert result == [{'name': 'USB Device', 'id': '5678'}]
                logger.info.assert_any_call("Detecting USB devices...")

    def test_detect_usb_macos(self, logger):
        with mock.patch('platform.system', return_value='darwin'):
            usb_detector = USBDetector(logger)
            with mock.patch.object(usb_detector, '_detect_usb_macos', return_value=[{'name': 'USB Device', 'id': '91011'}]):
                result = usb_detector.detect_usb()
                assert result == [{'name': 'USB Device', 'id': '91011'}]
                logger.info.assert_any_call("Detecting USB devices...")

    def test_detect_usb_unsupported_os(self, logger):
        with mock.patch('platform.system', return_value='unsupportedos'):
            usb_detector = USBDetector(logger)
            result = usb_detector.detect_usb()
            assert result == []
            logger.error.assert_any_call("Unsupported operating system: unsupportedos")

    def test_detect_usb_linux_success(self, usb_detector, logger):
        lsusb_output = "Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub\n"
        expected_result = [{'bus': '001', 'device': '001', 'id': '1d6b:0002', 'description': 'Linux Foundation 2.0 root hub'}]

        with mock.patch('subprocess.run', return_value=mock.Mock(stdout=lsusb_output, returncode=0)):
            result = usb_detector._detect_usb_linux()
            assert result == expected_result
            logger.info.assert_any_call(f"Detected USB devices: {expected_result}")

    def test_detect_usb_linux_failure(self, usb_detector, logger):
        with mock.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'lsusb')):
            result = usb_detector._detect_usb_linux()
            assert result == []
            logger.error.assert_any_call("Failed to detect USB devices on Linux: Command 'lsusb' returned non-zero exit status 1.")

    def test_parse_lsusb_output(self, usb_detector):
        lsusb_output = "Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub\n"
        expected_result = [{'bus': '001', 'device': '001', 'id': '1d6b:0002', 'description': 'Linux Foundation 2.0 root hub'}]
        result = usb_detector._parse_lsusb_output(lsusb_output)
        assert result == expected_result

    def test_detect_usb_windows_success(self, logger):
        powershell_output = "Status OK USB Composite Device\nStatus OK USB Root Hub\n"
        expected_result = [{'name': 'USB Composite Device', 'status': 'Status OK'},
                           {'name': 'USB Root Hub', 'status': 'Status OK'}]

        with mock.patch('platform.system', return_value='windows'):
            usb_detector = USBDetector(logger)
            with mock.patch('subprocess.run', return_value=mock.Mock(stdout=powershell_output, returncode=0)):
                result = usb_detector._detect_usb_windows()
                assert result == expected_result
                logger.info.assert_any_call(f"Detected USB devices: {expected_result}")

    def test_detect_usb_windows_failure(self, logger):
        with mock.patch('platform.system', return_value='windows'):
            usb_detector = USBDetector(logger)
            with mock.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'powershell')):
                result = usb_detector._detect_usb_windows()
                assert result == []
                logger.error.assert_any_call("Failed to detect USB devices on Windows: Command 'powershell' returned non-zero exit status 1.")

    def test_parse_windows_output(self, usb_detector):
        powershell_output = "Status OK USB Composite Device\nStatus OK USB Root Hub\n"
        expected_result = [{'name': 'USB Composite Device', 'status': 'Status OK'},
                           {'name': 'USB Root Hub', 'status': 'Status OK'}]
        result = usb_detector._parse_windows_output(powershell_output)
        assert result == expected_result

    def test_detect_usb_macos_failure(self, logger):
        with mock.patch('platform.system', return_value='darwin'):
            usb_detector = USBDetector(logger)
            with mock.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'system_profiler')):
                result = usb_detector._detect_usb_macos()
                assert result == []
                logger.error.assert_any_call("Failed to detect USB devices on macOS: Command 'system_profiler' returned non-zero exit status 1.")

    def test_detect_usb_macos_success(self, logger):
        system_profiler_output = "USB:\n\n    USB 3.0 Bus:\n\n        USB 2.0 Hub:\n\n            Product ID: 0x1234\n"
        expected_result = [{'description': 'USB 2.0 Hub', 'Product ID': '0x1234'}]

        with mock.patch('platform.system', return_value='darwin'):
            usb_detector = USBDetector(logger)
            with mock.patch('subprocess.run', return_value=mock.Mock(stdout=system_profiler_output, returncode=0)):
                result = usb_detector._detect_usb_macos()
                assert result == expected_result

    def test_parse_macos_output(self, usb_detector):
        system_profiler_output = "USB:\n\n    USB 3.0 Bus:\n\n        USB 2.0 Hub:\n\n            Product ID: 0x1234\n"
        expected_result = [{'description': 'USB 2.0 Hub', 'Product ID': '0x1234'}]
        result = usb_detector._parse_macos_output(system_profiler_output)
        assert result == expected_result


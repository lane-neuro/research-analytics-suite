import pytest
from unittest import mock
import platform
import subprocess

from research_analytics_suite.hardware_manager.interface.usb import USBcDetector


class TestUSBcDetector:
    @pytest.fixture
    def logger(self):
        with mock.patch('research_analytics_suite.utils.CustomLogger') as logger:
            yield logger

    def test_detect_usb_c_linux_success(self, logger):
        with mock.patch('platform.system', return_value='Linux'):
            usb_c_detector = USBcDetector(logger)
            lsusb_output = "    |__ Port 1: Dev 2, If 0, Class=Hub, Driver=hub/5p, 5000M\n        |__ Port 4: Dev 3, If 0, Class=Hub, Driver=hub/4p, 5000M\n            |__ Port 1: Dev 4, If 0, Class=Mass Storage, Driver=usb-storage, 5000M\n                |__ Port 1: Dev 5, If 0, Class=Vendor Specific Class, Driver=, 5000M Type-C\n"
            expected_result = ["                |__ Port 1: Dev 5, If 0, Class=Vendor Specific Class, Driver=, 5000M Type-C"]

            with mock.patch('subprocess.run', return_value=mock.Mock(stdout=lsusb_output, returncode=0)):
                result = usb_c_detector.detect_usb_c()
                assert result == expected_result
                logger.info.assert_any_call("Detecting USB-C devices...")
                logger.info.assert_any_call(f"Detected USB-C devices: {expected_result}")

    def test_detect_usb_c_windows_success(self, logger):
        with mock.patch('platform.system', return_value='Windows'):
            usb_c_detector = USBcDetector(logger)
            powershell_output = "Status OK Type-C Device\n"
            expected_result = ["Status OK Type-C Device"]

            with mock.patch('subprocess.run', return_value=mock.Mock(stdout=powershell_output, returncode=0)):
                result = usb_c_detector.detect_usb_c()
                assert result == expected_result
                logger.info.assert_any_call("Detecting USB-C devices...")
                logger.info.assert_any_call(f"Detected USB-C devices: {expected_result}")

    def test_detect_usb_c_macos_success(self, logger):
        with mock.patch('platform.system', return_value='Darwin'):
            usb_c_detector = USBcDetector(logger)
            system_profiler_output = "Type-C Device\n"
            expected_result = ["Type-C Device"]

            with mock.patch('subprocess.run', return_value=mock.Mock(stdout=system_profiler_output, returncode=0)):
                result = usb_c_detector.detect_usb_c()
                assert result == expected_result
                logger.info.assert_any_call("Detecting USB-C devices...")
                logger.info.assert_any_call(f"Detected USB-C devices: {expected_result}")

    def test_detect_usb_c_failure(self, logger):
        with mock.patch('platform.system', return_value='Linux'):
            usb_c_detector = USBcDetector(logger)
            with mock.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'lsusb -t')):
                result = usb_c_detector.detect_usb_c()
                assert result == []
                logger.error.assert_any_call("Failed to detect USB-C devices: Command 'lsusb -t' returned non-zero exit status 1.")

    def test_detect_usb_c_unsupported_platform(self, logger):
        with mock.patch('platform.system', return_value='unsupportedos'):
            usb_c_detector = USBcDetector(logger)
            result = usb_c_detector.detect_usb_c()
            assert result == []
            logger.error.assert_any_call("USB-C detection not supported on unsupportedos platform.")

    def test_read_usb_c_output_linux(self, logger):
        usb_c_detector = USBcDetector(logger)
        lsusb_output = "    |__ Port 1: Dev 2, If 0, Class=Hub, Driver=hub/5p, 5000M\n"
        with mock.patch('subprocess.run', return_value=mock.Mock(stdout=lsusb_output, returncode=0)):
            output = usb_c_detector._read_usb_c_output_linux()
            assert output == lsusb_output

    def test_parse_usb_c_output_linux(self, logger):
        usb_c_detector = USBcDetector(logger)
        lsusb_output = "    |__ Port 1: Dev 2, If 0, Class=Hub, Driver=hub/5p, 5000M\n        |__ Port 4: Dev 3, If 0, Class=Hub, Driver=hub/4p, 5000M\n            |__ Port 1: Dev 4, If 0, Class=Mass Storage, Driver=usb-storage, 5000M\n                |__ Port 1: Dev 5, If 0, Class=Vendor Specific Class, Driver=, 5000M Type-C\n"
        expected_result = ["                |__ Port 1: Dev 5, If 0, Class=Vendor Specific Class, Driver=, 5000M Type-C"]
        result = usb_c_detector._parse_usb_c_output_linux(lsusb_output)
        assert result == expected_result

    def test_read_usb_c_output_windows(self, logger):
        usb_c_detector = USBcDetector(logger)
        powershell_output = "Status OK Type-C Device\n"
        with mock.patch('subprocess.run', return_value=mock.Mock(stdout=powershell_output, returncode=0)):
            output = usb_c_detector._read_usb_c_output_windows()
            assert output == powershell_output

    def test_parse_usb_c_output_windows(self, logger):
        usb_c_detector = USBcDetector(logger)
        powershell_output = "Status OK Type-C Device\n"
        expected_result = ["Status OK Type-C Device"]
        result = usb_c_detector._parse_usb_c_output_windows(powershell_output)
        assert result == expected_result

    def test_read_usb_c_output_macos(self, logger):
        usb_c_detector = USBcDetector(logger)
        system_profiler_output = "Type-C Device\n"
        with mock.patch('subprocess.run', return_value=mock.Mock(stdout=system_profiler_output, returncode=0)):
            output = usb_c_detector._read_usb_c_output_macos()
            assert output == system_profiler_output

    def test_parse_usb_c_output_macos(self, logger):
        usb_c_detector = USBcDetector(logger)
        system_profiler_output = "Type-C Device\n"
        expected_result = ["Type-C Device"]
        result = usb_c_detector._parse_usb_c_output_macos(system_profiler_output)
        assert result == expected_result

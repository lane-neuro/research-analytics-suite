import pytest
from unittest import mock
import subprocess
import platform

from research_analytics_suite.hardware_manager.interface.serial import SerialDetector


class TestSerialDetector:
    @pytest.fixture
    def logger(self):
        with mock.patch('research_analytics_suite.utils.CustomLogger') as logger:
            yield logger

    @pytest.fixture
    def serial_detector(self, logger):
        with mock.patch('platform.system', return_value='linux'):
            return SerialDetector(logger)

    def test_initialization(self, serial_detector, logger):
        assert serial_detector.logger == logger
        assert serial_detector.os_info == 'linux'

    def test_detect_serial_unix_success(self, serial_detector, logger):
        dmesg_output = "ttyS0: detected\n"
        expected_result = ["ttyS0: detected"]

        with mock.patch('subprocess.run', return_value=mock.Mock(stdout=dmesg_output, returncode=0)):
            result = serial_detector.detect_serial()
            assert result == expected_result
            logger.info.assert_any_call("Detecting serial ports...")
            logger.info.assert_any_call(f"Detected serial ports: {expected_result}")

    def test_detect_serial_unix_no_devices(self, serial_detector, logger):
        dmesg_output = ""
        expected_result = []

        with mock.patch('subprocess.run', return_value=mock.Mock(stdout=dmesg_output, returncode=0)):
            result = serial_detector.detect_serial()
            assert result == expected_result
            logger.info.assert_any_call("Detecting serial ports...")
            logger.info.assert_any_call(f"Detected serial ports: {expected_result}")

    def test_detect_serial_unix_failure(self, serial_detector, logger):
        with mock.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'dmesg | grep tty')):
            result = serial_detector.detect_serial()
            assert result == []
            logger.error.assert_any_call("Failed to detect serial ports: Command 'dmesg | grep tty' returned non-zero exit status 1.")

    def test_detect_serial_windows_success(self, logger):
        with mock.patch('platform.system', return_value='windows'):
            serial_detector = SerialDetector(logger)
            mode_output = "Status for device COM1:\n-----------------------\nBaud: 9600\n"
            expected_result = ["Status for device COM1:\n-----------------------\nBaud: 9600"]

            with mock.patch('subprocess.run', return_value=mock.Mock(stdout=mode_output, returncode=0)):
                result = serial_detector.detect_serial()
                assert result == expected_result
                logger.info.assert_any_call("Detecting serial ports...")
                logger.info.assert_any_call(f"Detected serial ports: {expected_result}")

    def test_detect_serial_windows_no_devices(self, logger):
        with mock.patch('platform.system', return_value='windows'):
            serial_detector = SerialDetector(logger)
            mode_output = ""
            expected_result = []

            with mock.patch('subprocess.run', return_value=mock.Mock(stdout=mode_output, returncode=0)):
                result = serial_detector.detect_serial()
                assert result == expected_result
                logger.info.assert_any_call("Detecting serial ports...")
                logger.info.assert_any_call(f"Detected serial ports: {expected_result}")

    def test_detect_serial_windows_failure(self, logger):
        with mock.patch('platform.system', return_value='windows'):
            serial_detector = SerialDetector(logger)
            with mock.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'mode')):
                result = serial_detector.detect_serial()
                assert result == []
                logger.error.assert_any_call("Failed to detect serial ports: Command 'mode' returned non-zero exit status 1.")

    def test_detect_serial_unsupported_platform(self, logger):
        with mock.patch('platform.system', return_value='unsupportedos'):
            serial_detector = SerialDetector(logger)
            result = serial_detector.detect_serial()
            assert result == []
            logger.error.assert_any_call("Serial port detection not supported on unsupportedos platform.")

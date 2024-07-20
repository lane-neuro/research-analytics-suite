import pytest
from unittest import mock
import subprocess
import platform

from research_analytics_suite.hardware_manager.interface.display import DisplayPortDetector


class TestDisplayPortDetector:
    @pytest.fixture
    def logger(self):
        with mock.patch('research_analytics_suite.utils.CustomLogger') as logger:
            yield logger

    @pytest.fixture
    def displayport_detector(self, logger):
        return DisplayPortDetector(logger)

    def test_initialization(self, displayport_detector, logger):
        assert displayport_detector.logger == logger

    def test_detect_displayport_linux_success(self, displayport_detector, logger):
        xrandr_output = "DP-1 connected primary 1920x1080+0+0 (normal left inverted right x axis y axis) 527mm x 296mm\n"
        expected_result = ["DP-1 connected primary 1920x1080+0+0 (normal left inverted right x axis y axis) 527mm x 296mm"]

        with mock.patch('platform.system', return_value='linux'):
            with mock.patch('subprocess.run', return_value=mock.Mock(stdout=xrandr_output, returncode=0)):
                result = displayport_detector.detect_displayport()
                assert result == expected_result
                logger.info.assert_any_call("Detecting DisplayPort connections...")
                logger.info.assert_any_call(f"Detected DisplayPort connections: {expected_result}")

    def test_detect_displayport_linux_failure(self, displayport_detector, logger):
        with mock.patch('platform.system', return_value='linux'):
            with mock.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'xrandr')):
                result = displayport_detector.detect_displayport()
                assert result == []
                logger.error.assert_any_call("Failed to detect DisplayPort connections on Linux: Command 'xrandr' returned non-zero exit status 1.")

    def test_parse_xrandr_output(self, displayport_detector):
        xrandr_output = "DP-1 connected primary 1920x1080+0+0 (normal left inverted right x axis y axis) 527mm x 296mm\n"
        expected_result = ["DP-1 connected primary 1920x1080+0+0 (normal left inverted right x axis y axis) 527mm x 296mm"]
        result = displayport_detector._parse_xrandr_output(xrandr_output)
        assert result == expected_result

    def test_detect_displayport_windows_success(self, displayport_detector, logger):
        powershell_output = "InstanceName : DISPLAYPORT/0\n"
        expected_result = ["InstanceName : DISPLAYPORT/0"]

        with mock.patch('platform.system', return_value='windows'):
            with mock.patch('subprocess.run', return_value=mock.Mock(stdout=powershell_output, returncode=0)):
                result = displayport_detector.detect_displayport()
                assert result == expected_result
                logger.info.assert_any_call("Detecting DisplayPort connections...")
                logger.info.assert_any_call(f"Detected DisplayPort connections: {expected_result}")

    def test_detect_displayport_windows_failure(self, displayport_detector, logger):
        with mock.patch('platform.system', return_value='windows'):
            with mock.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'powershell')):
                result = displayport_detector.detect_displayport()
                assert result == []
                logger.error.assert_any_call("Failed to detect DisplayPort connections on Windows: Command 'powershell' returned non-zero exit status 1.")

    def test_parse_powershell_output(self, displayport_detector):
        powershell_output = "InstanceName : DISPLAYPORT/0\n"
        expected_result = ["InstanceName : DISPLAYPORT/0"]
        result = displayport_detector._parse_powershell_output(powershell_output)
        assert result == expected_result

    def test_detect_displayport_macos_success(self, displayport_detector, logger):
        system_profiler_output = "DisplayPort:\n"
        expected_result = ["DisplayPort:"]

        with mock.patch('platform.system', return_value='darwin'):
            with mock.patch('subprocess.run', return_value=mock.Mock(stdout=system_profiler_output, returncode=0)):
                result = displayport_detector.detect_displayport()
                assert result == expected_result
                logger.info.assert_any_call("Detecting DisplayPort connections...")
                logger.info.assert_any_call(f"Detected DisplayPort connections: {expected_result}")

    def test_detect_displayport_macos_failure(self, displayport_detector, logger):
        with mock.patch('platform.system', return_value='darwin'):
            with mock.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'system_profiler')):
                result = displayport_detector.detect_displayport()
                assert result == []
                logger.error.assert_any_call("Failed to detect DisplayPort connections on macOS: Command 'system_profiler' returned non-zero exit status 1.")

    def test_parse_macos_output(self, displayport_detector):
        system_profiler_output = "DisplayPort:\n"
        expected_result = ["DisplayPort:"]
        result = displayport_detector._parse_macos_output(system_profiler_output)
        assert result == expected_result

    def test_read_displayport_info(self, displayport_detector, logger):
        with mock.patch.object(displayport_detector, 'detect_displayport', return_value=['DP-1']):
            result = displayport_detector.read_displayport_info()
            expected_result = {'DP-1': {'connection': 'DP-1', 'status': 'active'}}
            assert result == expected_result
            logger.info.assert_any_call("Reading DisplayPort information...")

    def test_write_displayport_config_success(self, displayport_detector, logger):
        config = {'DP-1': 'some config'}
        result = displayport_detector.write_displayport_config(config)
        assert result is True
        logger.info.assert_any_call(f"Writing DisplayPort configuration: {config}")
        logger.info.assert_any_call(f"Configuration applied: {config}")

    def test_write_displayport_config_failure(self, displayport_detector, logger):
        config = {'DP-1': 'some config'}
        with mock.patch.object(displayport_detector, '_apply_config', side_effect=Exception('Error')):
            result = displayport_detector.write_displayport_config(config)
            assert result is False
            logger.error.assert_any_call("Failed to write DisplayPort configuration: Error")

    def test_transmit_displayport_info_success(self, displayport_detector, logger):
        url = 'http://example.com'
        with mock.patch.object(displayport_detector, 'read_displayport_info',
                               return_value={'DP-1': {'connection': 'DP-1', 'status': 'active'}}):
            result = displayport_detector.transmit_displayport_info(url)
            assert result is True
            logger.info.assert_any_call(f"Transmitting DisplayPort information to {url}...")
            logger.info.assert_any_call(
                f"Information transmitted: {{\n  \"DP-1\": {{\n    \"connection\": \"DP-1\",\n    \"status\": \"active\"\n  }}\n}}")

    def test_transmit_displayport_info_failure(self, displayport_detector, logger):
        url = 'http://example.com'
        with mock.patch.object(displayport_detector, 'read_displayport_info', side_effect=Exception('Error')):
            result = displayport_detector.transmit_displayport_info(url)
            assert result is False
            logger.error.assert_any_call(f"Failed to transmit DisplayPort information: Error")

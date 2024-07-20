import pytest
from unittest import mock
import subprocess
import platform

from research_analytics_suite.hardware_manager.interface.display import HDMIDetector


class TestHDMIDetector:
    @pytest.fixture
    def logger(self):
        with mock.patch('research_analytics_suite.utils.CustomLogger') as logger:
            yield logger

    @pytest.fixture
    def hdmi_detector(self, logger):
        return HDMIDetector(logger)

    def test_initialization(self, hdmi_detector, logger):
        assert hdmi_detector.logger == logger

    def test_detect_hdmi_linux_success(self, hdmi_detector, logger):
        xrandr_output = "HDMI-1 connected primary 1920x1080+0+0 (normal left inverted right x axis y axis) 527mm x 296mm\n"
        expected_result = ["HDMI-1 connected primary 1920x1080+0+0 (normal left inverted right x axis y axis) 527mm x 296mm"]

        with mock.patch('platform.system', return_value='linux'):
            with mock.patch('subprocess.run', return_value=mock.Mock(stdout=xrandr_output, returncode=0)):
                result = hdmi_detector.detect_hdmi()
                assert result == expected_result
                logger.info.assert_any_call("Detecting HDMI connections...")
                logger.info.assert_any_call(f"Detected HDMI connections: {expected_result}")

    def test_detect_hdmi_linux_failure(self, hdmi_detector, logger):
        with mock.patch('platform.system', return_value='linux'):
            with mock.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'xrandr')):
                result = hdmi_detector.detect_hdmi()
                assert result == []
                logger.error.assert_any_call("Failed to detect HDMI connections on Linux: Command 'xrandr' returned non-zero exit status 1.")

    def test_parse_xrandr_output(self, hdmi_detector):
        xrandr_output = "HDMI-1 connected primary 1920x1080+0+0 (normal left inverted right x axis y axis) 527mm x 296mm\n"
        expected_result = ["HDMI-1 connected primary 1920x1080+0+0 (normal left inverted right x axis y axis) 527mm x 296mm"]
        result = hdmi_detector._parse_xrandr_output(xrandr_output)
        assert result == expected_result

    def test_detect_hdmi_windows_success(self, hdmi_detector, logger):
        powershell_output = "InstanceName : HDMI/0\n"
        expected_result = ["InstanceName : HDMI/0"]

        with mock.patch('platform.system', return_value='windows'):
            with mock.patch('subprocess.run', return_value=mock.Mock(stdout=powershell_output, returncode=0)):
                result = hdmi_detector.detect_hdmi()
                assert result == expected_result
                logger.info.assert_any_call("Detecting HDMI connections...")
                logger.info.assert_any_call(f"Detected HDMI connections: {expected_result}")

    def test_detect_hdmi_windows_failure(self, hdmi_detector, logger):
        with mock.patch('platform.system', return_value='windows'):
            with mock.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'powershell')):
                result = hdmi_detector.detect_hdmi()
                assert result == []
                logger.error.assert_any_call("Failed to detect HDMI connections on Windows: Command 'powershell' returned non-zero exit status 1.")

    def test_parse_powershell_output(self, hdmi_detector):
        powershell_output = "InstanceName : HDMI/0\n"
        expected_result = ["InstanceName : HDMI/0"]
        result = hdmi_detector._parse_powershell_output(powershell_output)
        assert result == expected_result

    def test_detect_hdmi_macos_success(self, hdmi_detector, logger):
        system_profiler_output = "HDMI:\n"
        expected_result = ["HDMI:"]

        with mock.patch('platform.system', return_value='darwin'):
            with mock.patch('subprocess.run', return_value=mock.Mock(stdout=system_profiler_output, returncode=0)):
                result = hdmi_detector.detect_hdmi()
                assert result == expected_result
                logger.info.assert_any_call("Detecting HDMI connections...")
                logger.info.assert_any_call(f"Detected HDMI connections: {expected_result}")

    def test_detect_hdmi_macos_failure(self, hdmi_detector, logger):
        with mock.patch('platform.system', return_value='darwin'):
            with mock.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'system_profiler')):
                result = hdmi_detector.detect_hdmi()
                assert result == []
                logger.error.assert_any_call("Failed to detect HDMI connections on macOS: Command 'system_profiler' returned non-zero exit status 1.")

    def test_parse_macos_output(self, hdmi_detector):
        system_profiler_output = "HDMI:\n"
        expected_result = ["HDMI:"]
        result = hdmi_detector._parse_macos_output(system_profiler_output)
        assert result == expected_result

    def test_read_hdmi_info(self, hdmi_detector, logger):
        with mock.patch.object(hdmi_detector, 'detect_hdmi', return_value=['HDMI-1']):
            result = hdmi_detector.read_hdmi_info()
            expected_result = {'HDMI-1': {'connection': 'HDMI-1', 'status': 'active'}}
            assert result == expected_result
            logger.info.assert_any_call("Reading HDMI information...")

    def test_write_hdmi_config_success(self, hdmi_detector, logger):
        config = {'HDMI-1': 'some config'}
        result = hdmi_detector.write_hdmi_config(config)
        assert result is True
        logger.info.assert_any_call(f"Writing HDMI configuration: {config}")
        logger.info.assert_any_call(f"Configuration applied: {config}")

    def test_write_hdmi_config_failure(self, hdmi_detector, logger):
        config = {'HDMI-1': 'some config'}
        with mock.patch.object(hdmi_detector, '_apply_config', side_effect=Exception('Error')):
            result = hdmi_detector.write_hdmi_config(config)
            assert result is False
            logger.error.assert_any_call("Failed to write HDMI configuration: Error")

    def test_transmit_hdmi_info_success(self, hdmi_detector, logger):
        url = 'http://example.com'
        with mock.patch.object(hdmi_detector, 'read_hdmi_info', return_value={'HDMI-1': {'connection': 'HDMI-1', 'status': 'active'}}):
            result = hdmi_detector.transmit_hdmi_info(url)
            assert result is True
            logger.info.assert_any_call(f"Transmitting HDMI information to {url}...")
            logger.info.assert_any_call(f"Information transmitted: {{\n  \"HDMI-1\": {{\n    \"connection\": \"HDMI-1\",\n    \"status\": \"active\"\n  }}\n}}")

    def test_transmit_hdmi_info_failure(self, hdmi_detector, logger):
        url = 'http://example.com'
        with mock.patch.object(hdmi_detector, 'read_hdmi_info', side_effect=Exception('Error')):
            result = hdmi_detector.transmit_hdmi_info(url)
            assert result is False
            logger.error.assert_any_call(f"Failed to transmit HDMI information: Error")

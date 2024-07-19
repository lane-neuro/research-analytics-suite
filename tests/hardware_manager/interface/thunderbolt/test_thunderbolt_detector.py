import pytest
from unittest import mock
import platform
import subprocess

from research_analytics_suite.hardware_manager.interface.thunderbolt import ThunderboltDetector


class TestThunderboltDetector:
    @pytest.fixture
    def logger(self):
        with mock.patch('research_analytics_suite.utils.CustomLogger') as logger:
            yield logger

    def test_detect_thunderbolt_linux_success(self, logger):
        with mock.patch('platform.system', return_value='Linux'):
            thunderbolt_detector = ThunderboltDetector(logger)
            boltctl_output = " ●   Device: 0d8c:0014\n"
            expected_result = ["●   Device: 0d8c:0014"]

            with mock.patch('subprocess.run', return_value=mock.Mock(stdout=boltctl_output, returncode=0)):
                result = thunderbolt_detector.detect_thunderbolt()
                assert result == expected_result
                logger.info.assert_any_call("Detecting Thunderbolt devices...")
                logger.info.assert_any_call(f"Detected Thunderbolt devices: {expected_result}")

    def test_detect_thunderbolt_windows_success(self, logger):
        with mock.patch('platform.system', return_value='Windows'):
            thunderbolt_detector = ThunderboltDetector(logger)
            powershell_output = "Status OK Thunderbolt Device\n"
            expected_result = ["Status OK Thunderbolt Device"]

            with mock.patch('subprocess.run', return_value=mock.Mock(stdout=powershell_output, returncode=0)):
                result = thunderbolt_detector.detect_thunderbolt()
                assert result == expected_result
                logger.info.assert_any_call("Detecting Thunderbolt devices...")
                logger.info.assert_any_call(f"Detected Thunderbolt devices: {expected_result}")

    def test_detect_thunderbolt_macos_success(self, logger):
        with mock.patch('platform.system', return_value='Darwin'):
            thunderbolt_detector = ThunderboltDetector(logger)
            system_profiler_output = "Thunderbolt Device\n"
            expected_result = ["Thunderbolt Device"]

            with mock.patch('subprocess.run', return_value=mock.Mock(stdout=system_profiler_output, returncode=0)):
                result = thunderbolt_detector.detect_thunderbolt()
                assert result == expected_result
                logger.info.assert_any_call("Detecting Thunderbolt devices...")
                logger.info.assert_any_call(f"Detected Thunderbolt devices: {expected_result}")

    def test_detect_thunderbolt_failure(self, logger):
        with mock.patch('platform.system', return_value='Linux'):
            thunderbolt_detector = ThunderboltDetector(logger)
            with mock.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'boltctl')):
                result = thunderbolt_detector.detect_thunderbolt()
                assert result == []
                logger.error.assert_any_call("Failed to detect Thunderbolt devices: Command 'boltctl' returned non-zero exit status 1.")

    def test_detect_thunderbolt_unsupported_platform(self, logger):
        with mock.patch('platform.system', return_value='unsupportedos'):
            thunderbolt_detector = ThunderboltDetector(logger)
            result = thunderbolt_detector.detect_thunderbolt()
            assert result == []
            logger.error.assert_any_call("Thunderbolt detection not supported on unsupportedos platform.")

    def test_read_thunderbolt_output_linux(self, logger):
        thunderbolt_detector = ThunderboltDetector(logger)
        boltctl_output = " ●   Device: 0d8c:0014\n"
        with mock.patch('subprocess.run', return_value=mock.Mock(stdout=boltctl_output, returncode=0)):
            output = thunderbolt_detector._read_thunderbolt_output_linux()
            assert output == boltctl_output

    def test_parse_thunderbolt_output_linux(self, logger):
        thunderbolt_detector = ThunderboltDetector(logger)
        boltctl_output = " ●   Device: 0d8c:0014\n"
        expected_result = ["●   Device: 0d8c:0014"]
        result = thunderbolt_detector._parse_thunderbolt_output_linux(boltctl_output)
        assert result == expected_result

    def test_read_thunderbolt_output_windows(self, logger):
        thunderbolt_detector = ThunderboltDetector(logger)
        powershell_output = "Status OK Thunderbolt Device\n"
        with mock.patch('subprocess.run', return_value=mock.Mock(stdout=powershell_output, returncode=0)):
            output = thunderbolt_detector._read_thunderbolt_output_windows()
            assert output == powershell_output

    def test_parse_thunderbolt_output_windows(self, logger):
        thunderbolt_detector = ThunderboltDetector(logger)
        powershell_output = "Status OK Thunderbolt Device\n"
        expected_result = ["Status OK Thunderbolt Device"]
        result = thunderbolt_detector._parse_thunderbolt_output_windows(powershell_output)
        assert result == expected_result

    def test_read_thunderbolt_output_macos(self, logger):
        thunderbolt_detector = ThunderboltDetector(logger)
        system_profiler_output = "Thunderbolt Device\n"
        with mock.patch('subprocess.run', return_value=mock.Mock(stdout=system_profiler_output, returncode=0)):
            output = thunderbolt_detector._read_thunderbolt_output_macos()
            assert output == system_profiler_output

    def test_parse_thunderbolt_output_macos(self, logger):
        thunderbolt_detector = ThunderboltDetector(logger)
        system_profiler_output = "Thunderbolt Device\n"
        expected_result = ["Thunderbolt Device"]
        result = thunderbolt_detector._parse_thunderbolt_output_macos(system_profiler_output)
        assert result == expected_result

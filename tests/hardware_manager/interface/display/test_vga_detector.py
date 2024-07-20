import platform

import pytest
from unittest import mock
import subprocess

from research_analytics_suite.hardware_manager.interface.display import VGADetector

class TestVGADetector:
    @pytest.fixture
    def logger(self):
        with mock.patch('research_analytics_suite.utils.CustomLogger') as logger:
            yield logger

    @pytest.fixture
    def vga_detector(self, logger):
        return VGADetector(logger)

    def test_initialization(self, vga_detector, logger):
        assert vga_detector.logger == logger

    @pytest.mark.skipif(platform.system().lower() == 'linux', reason="Avoid ctypes errors on Linux systems")
    def test_detect_vga_linux_success(self, vga_detector, logger):
        lspci_output = "00:02.0 VGA compatible controller: Intel Corporation HD Graphics 620\n"
        expected_result = [{'device_id': '00:02.0', 'description': 'Intel Corporation HD Graphics 620'}]

        with mock.patch('platform.system', return_value='linux'):
            with mock.patch('subprocess.run', return_value=mock.Mock(stdout=lspci_output, returncode=0)):
                result = vga_detector.detect_vga()
                assert result == expected_result
                logger.info.assert_any_call("Detecting VGA connections...")
                logger.info.assert_any_call(f"Detected VGA connections: {expected_result}")

    @pytest.mark.skipif(platform.system().lower() == 'linux', reason="Avoid ctypes errors on Linux systems")
    def test_detect_vga_linux_failure(self, vga_detector, logger):
        with mock.patch('platform.system', return_value='linux'):
            with mock.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'lspci')):
                result = vga_detector.detect_vga()
                assert result == []
                logger.error.assert_any_call("Failed to detect VGA connections on Linux: Command 'lspci' returned non-zero exit status 1.")

    @pytest.mark.skipif(platform.system().lower() == 'linux', reason="Avoid ctypes errors on Linux systems")
    def test_parse_lspci_output(self, vga_detector):
        lspci_output = "00:02.0 VGA compatible controller: Intel Corporation HD Graphics 620\n"
        expected_result = [{'device_id': '00:02.0', 'description': 'Intel Corporation HD Graphics 620'}]
        result = vga_detector._parse_lspci_output(lspci_output)
        assert result == expected_result

    def test_detect_vga_windows_success(self, vga_detector, logger):
        powershell_output = "Name : Intel(R) HD Graphics 620\n"
        expected_result = [{'description': 'Intel(R) HD Graphics 620'}]

        with mock.patch('platform.system', return_value='windows'):
            with mock.patch('subprocess.run', return_value=mock.Mock(stdout=powershell_output, returncode=0)):
                result = vga_detector.detect_vga()
                assert result == expected_result
                logger.info.assert_any_call("Detecting VGA connections...")
                logger.info.assert_any_call(f"Detected VGA connections: {expected_result}")

    def test_detect_vga_windows_failure(self, vga_detector, logger):
        with mock.patch('platform.system', return_value='windows'):
            with mock.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'powershell')):
                result = vga_detector.detect_vga()
                assert result == []
                logger.error.assert_any_call("Failed to detect VGA connections on Windows: Command 'powershell' returned non-zero exit status 1.")

    def test_parse_windows_output(self, vga_detector):
        powershell_output = "Name : Intel(R) HD Graphics 620\n"
        expected_result = [{'description': 'Intel(R) HD Graphics 620'}]
        result = vga_detector._parse_windows_output(powershell_output)
        assert result == expected_result

    def test_detect_vga_macos_success(self, vga_detector, logger):
        system_profiler_output = "Chipset Model: Intel HD Graphics 620\n"
        expected_result = [{'description': 'Intel HD Graphics 620'}]

        with mock.patch('platform.system', return_value='darwin'):
            with mock.patch('subprocess.run', return_value=mock.Mock(stdout=system_profiler_output, returncode=0)):
                result = vga_detector.detect_vga()
                assert result == expected_result
                logger.info.assert_any_call("Detecting VGA connections...")
                logger.info.assert_any_call(f"Detected VGA connections: {expected_result}")

    def test_detect_vga_macos_failure(self, vga_detector, logger):
        with mock.patch('platform.system', return_value='darwin'):
            with mock.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'system_profiler')):
                result = vga_detector.detect_vga()
                assert result == []
                logger.error.assert_any_call("Failed to detect VGA connections on macOS: Command 'system_profiler' returned non-zero exit status 1.")

    def test_parse_macos_output(self, vga_detector):
        system_profiler_output = "Chipset Model: Intel HD Graphics 620\n"
        expected_result = [{'description': 'Intel HD Graphics 620'}]
        result = vga_detector._parse_macos_output(system_profiler_output)
        assert result == expected_result

import pytest
from unittest.mock import Mock, patch

from research_analytics_suite.hardware_manager.interface.audio import AudioDetector


class TestAudioDetector:
    @pytest.fixture
    def logger(self):
        return Mock()

    @pytest.fixture
    def audio_detector(self, logger):
        return AudioDetector(logger)

    @patch('platform.system', return_value='Linux')
    @patch('subprocess.run')
    def test_detect_audio_linux(self, mock_subprocess_run, mock_platform_system, audio_detector, logger):
        mock_subprocess_run.return_value.stdout = "card 0: Device 1\ncard 1: Device 2\n"
        devices = audio_detector.detect_audio()
        assert "card 0: Device 1" in devices
        assert "card 1: Device 2" in devices

        logger.info.assert_any_call("Detecting audio devices...")
        logger.info.assert_any_call("Detected audio devices: ['card 0: Device 1', 'card 1: Device 2', '']")

    @patch('platform.system', return_value='Windows')
    @patch('subprocess.run')
    def test_detect_audio_windows(self, mock_subprocess_run, mock_platform_system, audio_detector, logger):
        mock_subprocess_run.return_value.stdout = "Device 1\nDevice 2\n"
        devices = audio_detector.detect_audio()
        assert "Device 1" in devices
        assert "Device 2" in devices

        logger.info.assert_any_call("Detecting audio devices...")
        logger.info.assert_any_call("Detected audio devices: ['Device 1', 'Device 2', '']")

    @patch('platform.system', return_value='Darwin')
    @patch('subprocess.run')
    def test_detect_audio_macos(self, mock_subprocess_run, mock_platform_system, audio_detector, logger):
        mock_subprocess_run.return_value.stdout = "Device 1\nDevice 2\n"
        devices = audio_detector.detect_audio()
        assert "Device 1" in devices
        assert "Device 2" in devices

        logger.info.assert_any_call("Detecting audio devices...")
        logger.info.assert_any_call("Detected audio devices: ['Device 1', 'Device 2', '']")

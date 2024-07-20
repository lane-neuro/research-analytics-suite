import pytest
import wave
from unittest.mock import Mock, patch

from research_analytics_suite.hardware_manager.interface.audio.AudioRecorder import AudioRecorder


class TestAudioRecorder:
    @pytest.fixture
    def logger(self):
        return Mock()

    @pytest.fixture
    def audio_recorder(self, logger):
        return AudioRecorder(logger)

    @patch('wave.open', create=True)
    def test_record_audio(self, mock_wave_open, audio_recorder, logger):
        stream = Mock()
        audio_recorder.audio.open = Mock(return_value=stream)

        mock_wave = Mock()
        mock_wave_open.return_value.__enter__.return_value = mock_wave

        # Ensure stream.read returns bytes-like object
        stream.read.return_value = b'\x00\x01' * 512  # Example bytes data for one frame

        audio_recorder.record_audio("test.wav")

        stream.read.assert_called()
        stream.stop_stream.assert_called_once()
        stream.close.assert_called_once()
        mock_wave.writeframes.assert_called()

        logger.info.assert_any_call("Recording audio for 5 seconds...")
        logger.info.assert_any_call("Audio recording saved to test.wav")

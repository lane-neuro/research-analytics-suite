import pyaudio
import pytest
import wave
import platform
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

    @patch('wave.open', create=True)
    def test_record_audio_different_durations(self, mock_wave_open, audio_recorder, logger):
        stream = Mock()
        audio_recorder.audio.open = Mock(return_value=stream)

        mock_wave = Mock()
        mock_wave_open.return_value.__enter__.return_value = mock_wave

        stream.read.return_value = b'\x00\x01' * 512

        durations = [1, 3, 10]  # Different durations to test
        for duration in durations:
            audio_recorder.record_audio(f"test_{duration}.wav", duration=duration)
            stream.read.assert_called()
            stream.stop_stream.assert_called()
            stream.close.assert_called()
            mock_wave.writeframes.assert_called()
            logger.info.assert_any_call(f"Recording audio for {duration} seconds...")
            logger.info.assert_any_call(f"Audio recording saved to test_{duration}.wav")

    @patch('wave.open', create=True)
    def test_record_audio_different_sample_rates_and_channels(self, mock_wave_open, audio_recorder, logger):
        stream = Mock()
        audio_recorder.audio.open = Mock(return_value=stream)

        mock_wave = Mock()
        mock_wave_open.return_value.__enter__.return_value = mock_wave

        stream.read.return_value = b'\x00\x01' * 512

        sample_rates = [22050, 44100, 48000]
        channels = [1, 2]
        for sr in sample_rates:
            for ch in channels:
                audio_recorder.record_audio(f"test_{sr}_{ch}.wav", sample_rate=sr, channels=ch)
                stream.read.assert_called()
                stream.stop_stream.assert_called()
                stream.close.assert_called()
                mock_wave.writeframes.assert_called()
                logger.info.assert_any_call(f"Recording audio for 5 seconds...")
                logger.info.assert_any_call(f"Audio recording saved to test_{sr}_{ch}.wav")

    @patch('wave.open', create=True)
    def test_record_audio_exception_handling(self, mock_wave_open, audio_recorder, logger):
        stream = Mock()
        audio_recorder.audio.open = Mock(return_value=stream)

        mock_wave = Mock()
        mock_wave_open.return_value.__enter__.return_value = mock_wave

        stream.read.side_effect = Exception("Microphone error")

        with pytest.raises(Exception):
            audio_recorder.record_audio("test.wav")

        stream.read.assert_called()
        stream.stop_stream.assert_called_once()
        stream.close.assert_called_once()
        logger.error.assert_any_call("Failed to record audio: Microphone error")

    @patch('wave.open', create=True)
    def test_record_audio_cleanup_on_error(self, mock_wave_open, audio_recorder, logger):
        stream = Mock()
        audio_recorder.audio.open = Mock(return_value=stream)

        mock_wave = Mock()
        mock_wave_open.return_value.__enter__.return_value = mock_wave

        stream.read.side_effect = Exception("Microphone error")

        with pytest.raises(Exception):
            audio_recorder.record_audio("test.wav")

        stream.read.assert_called()
        stream.stop_stream.assert_called_once()
        stream.close.assert_called_once()
        logger.error.assert_any_call("Failed to record audio: Microphone error")

    @patch('wave.open', create=True)
    def test_record_audio_output_file_verification(self, mock_wave_open, audio_recorder, logger):
        stream = Mock()
        audio_recorder.audio.open = Mock(return_value=stream)

        mock_wave = Mock()
        mock_wave_open.return_value.__enter__.return_value = mock_wave

        stream.read.return_value = b'\x00\x01' * 512

        audio_recorder.record_audio("test.wav")

        stream.read.assert_called()
        stream.stop_stream.assert_called_once()
        stream.close.assert_called_once()
        mock_wave.writeframes.assert_called()

        logger.info.assert_any_call("Recording audio for 5 seconds...")
        logger.info.assert_any_call("Audio recording saved to test.wav")

        # Verify the output file content
        mock_wave_open.assert_called_with("test.wav", 'wb')
        mock_wave.setnchannels.assert_called_with(2)
        mock_wave.setsampwidth.assert_called_with(audio_recorder.audio.get_sample_size(pyaudio.paInt16))
        mock_wave.setframerate.assert_called_with(44100)
        mock_wave.writeframes.assert_called_with(b'\x00\x01' * 512 * (44100 // 1024 * 5))

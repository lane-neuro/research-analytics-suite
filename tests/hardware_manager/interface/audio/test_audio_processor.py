import pytest
import wave
import numpy as np
from unittest.mock import Mock, patch

from research_analytics_suite.hardware_manager.interface.audio.AudioProcessor import AudioProcessor


class TestAudioProcessor:
    @pytest.fixture
    def logger(self):
        return Mock()

    @pytest.fixture
    def audio_processor(self, logger):
        return AudioProcessor(logger)

    def test_list_devices(self, audio_processor, logger):
        audio_processor.audio.get_device_count = Mock(return_value=2)
        audio_processor.audio.get_device_info_by_index = Mock(
            side_effect=[
                {"name": "Device 1"},
                {"name": "Device 2"}
            ]
        )
        audio_processor.list_devices()
        logger.info.assert_any_call("Listing available audio devices...")
        logger.info.assert_any_call("Device 0: Device 1")
        logger.info.assert_any_call("Device 1: Device 2")

    @patch('wave.open', create=True)
    def test_play_audio(self, mock_wave_open, audio_processor, logger):
        mock_wave = Mock()
        mock_wave_open.return_value.__enter__.return_value = mock_wave

        stream = Mock()
        audio_processor.audio.open = Mock(return_value=stream)
        mock_wave.readframes.side_effect = [b'data', b'']
        mock_wave.getsampwidth.return_value = 2  # Ensure this returns an actual integer

        audio_processor.play_audio("test.wav")

        stream.write.assert_called_with(b'data')
        stream.stop_stream.assert_called_once()
        stream.close.assert_called_once()

        logger.info.assert_any_call("Playing audio from test.wav...")
        logger.info.assert_any_call("Audio playback finished.")

    @patch('wave.open', create=True)
    def test_normalize_audio(self, mock_wave_open, audio_processor, logger):
        mock_wave = Mock()
        mock_wave_open.return_value.__enter__.return_value = mock_wave

        sample_data = np.array([0, 1, -1, 32767, -32768], dtype=np.int16).tobytes()
        mock_wave.readframes.return_value = sample_data
        mock_wave.getparams.return_value = wave._wave_params(1, 2, 44100, 5, 'NONE', 'not compressed')

        audio_processor.normalize_audio("input.wav", "output.wav")

        mock_wave.setparams.assert_called()
        mock_wave.writeframes.assert_called()

        logger.info.assert_any_call("Normalizing audio from input.wav to output.wav...")
        logger.info.assert_any_call("Audio normalization finished.")

    @patch('wave.open', create=True)
    def test_analyze_frequency(self, mock_wave_open, audio_processor, logger):
        mock_wave = Mock()
        mock_wave_open.return_value.__enter__.return_value = mock_wave

        sample_data = np.array([0, 1, -1, 32767, -32768], dtype=np.int16).tobytes()
        mock_wave.readframes.return_value = sample_data
        mock_wave.getparams.return_value = wave._wave_params(1, 2, 44100, 5, 'NONE', 'not compressed')

        freqs, fft_result = audio_processor.analyze_frequency("test.wav")

        assert len(freqs) > 0
        assert len(fft_result) > 0

        logger.info.assert_any_call("Analyzing frequency components of test.wav...")
        logger.info.assert_any_call("Frequency analysis finished.")

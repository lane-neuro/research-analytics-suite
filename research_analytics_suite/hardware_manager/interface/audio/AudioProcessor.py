"""
AudioProcessor

This module provides an interface for recording and playing audio using the PyAudio library.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import numpy as np
import pyaudio
import wave


class AudioProcessor:
    def __init__(self, logger):
        self.logger = logger
        self.audio = pyaudio.PyAudio()

    def list_devices(self):
        """List all available audio devices."""
        self.logger.info("Listing available audio devices...")
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            self.logger.info(f"Device {i}: {info['name']}")

    def play_audio(self, input_filename):
        """Play audio from a WAV file."""
        self.logger.info(f"Playing audio from {input_filename}...")
        with wave.open(input_filename, 'rb') as wf:
            stream = self.audio.open(format=self.audio.get_format_from_width(wf.getsampwidth()),
                                     channels=wf.getnchannels(),
                                     rate=wf.getframerate(),
                                     output=True)

            data = wf.readframes(1024)
            while data:
                stream.write(data)
                data = wf.readframes(1024)

            stream.stop_stream()
            stream.close()

        self.logger.info("Audio playback finished.")

    def normalize_audio(self, input_filename, output_filename):
        """Normalize audio volume to a standard level."""
        self.logger.info(f"Normalizing audio from {input_filename} to {output_filename}...")

        with wave.open(input_filename, 'rb') as wf:
            params = wf.getparams()
            frames = wf.readframes(params.nframes)
            audio_data = np.frombuffer(frames, dtype=np.int16)
            max_val = np.max(np.abs(audio_data))
            normalized_data = (audio_data / max_val * 32767).astype(np.int16)

        with wave.open(output_filename, 'wb') as wf:
            wf.setparams(params)
            wf.writeframes(normalized_data.tobytes())

        self.logger.info("Audio normalization finished.")

    def analyze_frequency(self, input_filename):
        """Analyze the frequency components of the audio."""
        self.logger.info(f"Analyzing frequency components of {input_filename}...")

        with wave.open(input_filename, 'rb') as wf:
            params = wf.getparams()
            frames = wf.readframes(params.nframes)
            audio_data = np.frombuffer(frames, dtype=np.int16)

        fft_result = np.fft.fft(audio_data)
        freqs = np.fft.fftfreq(len(fft_result))

        self.logger.info("Frequency analysis finished.")
        return freqs, np.abs(fft_result)

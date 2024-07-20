"""
AudioRecorder

This class is responsible for recording audio from the system's default audio input device. It uses the PyAudio library to record audio data from the microphone and save it to a WAV file.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import pyaudio
import wave


class AudioRecorder:
    def __init__(self, logger):
        self.logger = logger
        self.audio = pyaudio.PyAudio()

    def record_audio(self, output_filename, duration=5, sample_rate=44100, channels=2):
        """Record audio from the default microphone."""
        self.logger.info(f"Recording audio for {duration} seconds...")

        stream = None
        try:
            stream = self.audio.open(format=pyaudio.paInt16, channels=channels,
                                     rate=sample_rate, input=True,
                                     frames_per_buffer=1024)

            frames = []
            for _ in range(0, int(sample_rate / 1024 * duration)):
                data = stream.read(1024)
                frames.append(data)

            with wave.open(output_filename, 'wb') as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(sample_rate)
                wf.writeframes(b''.join(frames))

            self.logger.info(f"Audio recording saved to {output_filename}")

        except Exception as e:
            self.logger.error(f"Failed to record audio: {e}")
            raise e
        finally:
            if stream:
                if stream.is_active():
                    stream.stop_stream()
                stream.close()
            self.audio.terminate()

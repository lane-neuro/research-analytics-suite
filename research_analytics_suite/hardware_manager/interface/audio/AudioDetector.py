"""
AudioDetector

This module contains the AudioDetector class, which detects audio devices.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import subprocess


class AudioDetector:
    def __init__(self, logger):
        self.logger = logger

    def detect_audio(self):
        """Detect audio devices.

        Returns:
            list: Information about detected audio devices.
        """
        self.logger.info("Detecting audio devices...")
        try:
            result = subprocess.run(['aplay -l'], capture_output=True, text=True, shell=True, check=True)
            audio_devices = result.stdout.split('\n')
            self.logger.info(f"Detected audio devices: {audio_devices}")
            return audio_devices
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect audio devices: {e}")
            return []

"""
AudioDetector

This module contains the AudioDetector class, which detects audio devices and manages audio capture and playback.

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
import platform
from typing import List


class AudioDetector:
    def __init__(self, logger):
        self.logger = logger

    def detect_audio(self) -> List[str]:
        """Detect audio devices.

        Returns:
            list: Information about detected audio devices.
        """
        self.logger.info("Detecting audio devices...")
        os_info = platform.system().lower()
        if os_info == 'linux':
            return self._detect_audio_linux()
        elif os_info == 'windows':
            return self._detect_audio_windows()
        elif os_info == 'darwin':
            return self._detect_audio_macos()
        else:
            self.logger.error(f"Unsupported operating system: {os_info}")
            return []

    def _detect_audio_linux(self) -> List[str]:
        try:
            result = subprocess.run(['aplay', '-l'], capture_output=True, text=True, shell=False, check=True)
            audio_devices = result.stdout.split('\n')
            self.logger.info(f"Detected audio devices: {audio_devices}")
            return audio_devices
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect audio devices on Linux: {e}")
            return []

    def _detect_audio_windows(self) -> List[str]:
        try:
            result = subprocess.run(['powershell', 'Get-PnpDevice -Class Media'], capture_output=True, text=True, shell=False, check=True)
            audio_devices = result.stdout.split('\n')
            self.logger.info(f"Detected audio devices: {audio_devices}")
            return audio_devices
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect audio devices on Windows: {e}")
            return []

    def _detect_audio_macos(self) -> List[str]:
        try:
            result = subprocess.run(['system_profiler', 'SPAudioDataType'], capture_output=True, text=True, shell=False, check=True)
            audio_devices = result.stdout.split('\n')
            self.logger.info(f"Detected audio devices: {audio_devices}")
            return audio_devices
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect audio devices on macOS: {e}")
            return []
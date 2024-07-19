"""
Thunderbolt Detector

This module contains the ThunderboltDetector class, which detects Thunderbolt devices.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import platform
import subprocess


class ThunderboltDetector:
    def __init__(self, logger):
        self.logger = logger
        self.os_info = platform.system().lower()

    def detect_thunderbolt(self):
        """Detect Thunderbolt devices.

        Returns:
            list: Information about detected Thunderbolt devices.
        """
        self.logger.info("Detecting Thunderbolt devices...")

        if self.os_info == 'linux':
            return self._detect_thunderbolt_linux()
        elif self.os_info == 'windows':
            return self._detect_thunderbolt_windows()
        elif self.os_info == 'darwin':
            return self._detect_thunderbolt_macos()
        else:
            self.logger.error(f"Thunderbolt detection not supported on {self.os_info} platform.")
            return []

    def _detect_thunderbolt_linux(self):
        """Detect Thunderbolt devices on Linux.

        Returns:
            list: Information about detected Thunderbolt devices on Linux.
        """
        try:
            output = self._read_thunderbolt_output_linux()
            thunderbolt_devices = self._parse_thunderbolt_output_linux(output)
            self.logger.info(f"Detected Thunderbolt devices: {thunderbolt_devices}")
            return thunderbolt_devices
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect Thunderbolt devices: {e}")
            return []

    def _read_thunderbolt_output_linux(self):
        """Read Thunderbolt device information on Linux."""
        result = subprocess.run(['boltctl'], capture_output=True, text=True, check=True)
        return result.stdout

    def _parse_thunderbolt_output_linux(self, output):
        """Parse the output of the boltctl command to find Thunderbolt devices."""
        return [line.strip() for line in output.split('\n') if line.strip()]

    def _detect_thunderbolt_windows(self):
        """Detect Thunderbolt devices on Windows.

        Returns:
            list: Information about detected Thunderbolt devices on Windows.
        """
        try:
            output = self._read_thunderbolt_output_windows()
            thunderbolt_devices = self._parse_thunderbolt_output_windows(output)
            self.logger.info(f"Detected Thunderbolt devices: {thunderbolt_devices}")
            return thunderbolt_devices
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect Thunderbolt devices: {e}")
            return []

    def _read_thunderbolt_output_windows(self):
        """Read Thunderbolt device information on Windows."""
        result = subprocess.run(['powershell', 'Get-PnpDevice -Class Thunderbolt'], capture_output=True, text=True, shell=True, check=True)
        return result.stdout

    def _parse_thunderbolt_output_windows(self, output):
        """Parse the output of the PowerShell command to find Thunderbolt devices."""
        return [line.strip() for line in output.split('\n') if line.strip()]

    def _detect_thunderbolt_macos(self):
        """Detect Thunderbolt devices on macOS.

        Returns:
            list: Information about detected Thunderbolt devices on macOS.
        """
        try:
            output = self._read_thunderbolt_output_macos()
            thunderbolt_devices = self._parse_thunderbolt_output_macos(output)
            self.logger.info(f"Detected Thunderbolt devices: {thunderbolt_devices}")
            return thunderbolt_devices
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect Thunderbolt devices: {e}")
            return []

    def _read_thunderbolt_output_macos(self):
        """Read Thunderbolt device information on macOS."""
        result = subprocess.run(['system_profiler', 'SPThunderboltDataType'], capture_output=True, text=True, check=True)
        return result.stdout

    def _parse_thunderbolt_output_macos(self, output):
        """Parse the output of the system_profiler command to find Thunderbolt devices."""
        return [line.strip() for line in output.split('\n') if line.strip()]

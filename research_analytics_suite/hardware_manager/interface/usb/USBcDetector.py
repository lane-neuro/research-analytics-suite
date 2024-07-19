"""
USBcDetector

This module contains the USBcDetector class, which detects USB-C devices.

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


class USBcDetector:
    def __init__(self, logger):
        self.logger = logger
        self.os_info = platform.system().lower()

    def detect_usb_c(self):
        """Detect USB-C devices.

        Returns:
            list: Information about detected USB-C devices.
        """
        self.logger.info("Detecting USB-C devices...")

        if self.os_info == 'linux':
            return self._detect_usb_c_linux()
        elif self.os_info == 'windows':
            return self._detect_usb_c_windows()
        elif self.os_info == 'darwin':
            return self._detect_usb_c_macos()
        else:
            self.logger.error(f"USB-C detection not supported on {self.os_info} platform.")
            return []

    def _detect_usb_c_linux(self):
        """Detect USB-C devices on Linux.

        Returns:
            list: Information about detected USB-C devices on Linux.
        """
        try:
            output = self._read_usb_c_output_linux()
            usb_c_devices = self._parse_usb_c_output_linux(output)
            self.logger.info(f"Detected USB-C devices: {usb_c_devices}")
            return usb_c_devices
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect USB-C devices: {e}")
            return []

    def _read_usb_c_output_linux(self):
        """Read USB-C device information on Linux."""
        result = subprocess.run(['lsusb', '-t'], capture_output=True, text=True, check=True)
        return result.stdout

    def _parse_usb_c_output_linux(self, output):
        """Parse the output of the lsusb command to find USB-C devices."""
        return [line for line in output.split('\n') if 'Type-C' in line and line.strip()]

    def _detect_usb_c_windows(self):
        """Detect USB-C devices on Windows.

        Returns:
            list: Information about detected USB-C devices on Windows.
        """
        try:
            output = self._read_usb_c_output_windows()
            usb_c_devices = self._parse_usb_c_output_windows(output)
            self.logger.info(f"Detected USB-C devices: {usb_c_devices}")
            return usb_c_devices
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect USB-C devices: {e}")
            return []

    def _read_usb_c_output_windows(self):
        """Read USB-C device information on Windows."""
        result = subprocess.run(['powershell', 'Get-PnpDevice -Class USB'], capture_output=True, text=True, shell=True, check=True)
        return result.stdout

    def _parse_usb_c_output_windows(self, output):
        """Parse the output of the PowerShell command to find USB-C devices."""
        return [line for line in output.split('\n') if 'Type-C' in line and line.strip()]

    def _detect_usb_c_macos(self):
        """Detect USB-C devices on macOS.

        Returns:
            list: Information about detected USB-C devices on macOS.
        """
        try:
            output = self._read_usb_c_output_macos()
            usb_c_devices = self._parse_usb_c_output_macos(output)
            self.logger.info(f"Detected USB-C devices: {usb_c_devices}")
            return usb_c_devices
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect USB-C devices: {e}")
            return []

    def _read_usb_c_output_macos(self):
        """Read USB-C device information on macOS."""
        result = subprocess.run(['system_profiler', 'SPUSBDataType'], capture_output=True, text=True, check=True)
        return result.stdout

    def _parse_usb_c_output_macos(self, output):
        """Parse the output of the system_profiler command to find USB-C devices."""
        return [line for line in output.split('\n') if 'Type-C' in line and line.strip()]

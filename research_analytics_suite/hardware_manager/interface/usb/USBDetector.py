"""
USBDetector

This module contains the USBDetector class, which detects USB devices.

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
import re
from typing import List, Dict


class USBDetector:
    def __init__(self, logger):
        self.logger = logger
        self.os_info = platform.system().lower()

    def detect_usb(self) -> List[Dict[str, str]]:
        """Detect USB devices with detailed information.

        Returns:
            list: Information about detected USB devices.
        """
        self.logger.info("Detecting USB devices...")
        if self.os_info == 'linux':
            return self._detect_usb_linux()
        elif self.os_info == 'windows':
            return self._detect_usb_windows()
        elif self.os_info == 'darwin':
            return self._detect_usb_macos()
        else:
            self.logger.error(f"Unsupported operating system: {self.os_info}")
            return []

    def _detect_usb_linux(self) -> List[Dict[str, str]]:
        """Detect USB devices on Linux.

        Returns:
            list: Information about detected USB devices on Linux.
        """
        try:
            result = subprocess.run(['lsusb'], capture_output=True, text=True, check=True)
            usb_devices = self._parse_lsusb_output(result.stdout)
            self.logger.info(f"Detected USB devices: {usb_devices}")
            return usb_devices
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect USB devices on Linux: {e}")
            return []

    def _parse_lsusb_output(self, output: str) -> List[Dict[str, str]]:
        """Parse the output of the lsusb command.

        Args:
            output (str): The output of the lsusb command.

        Returns:
            list: Parsed information about detected USB devices.
        """
        devices = []
        lines = output.split('\n')
        for line in lines:
            if line:
                match = re.match(r'Bus (\d+) Device (\d+): ID (\w+:\w+) (.+)', line)
                if match:
                    devices.append({
                        'bus': match.group(1),
                        'device': match.group(2),
                        'id': match.group(3),
                        'description': match.group(4)
                    })
        return devices

    def _detect_usb_windows(self) -> List[Dict[str, str]]:
        """Detect USB devices on Windows.

        Returns:
            list: Information about detected USB devices on Windows.
        """
        try:
            result = subprocess.run(['powershell', 'Get-PnpDevice -Class USB'],
                                    capture_output=True, text=True, check=True)
            usb_devices = self._parse_windows_output(result.stdout)
            self.logger.info(f"Detected USB devices: {usb_devices}")
            return usb_devices
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect USB devices on Windows: {e}")
            return []

    def _parse_windows_output(self, output: str) -> List[Dict[str, str]]:
        """Parse the output of the PowerShell command.

        Args:
            output (str): The output of the PowerShell command.

        Returns:
            list: Parsed information about detected USB devices.
        """
        devices = []
        lines = output.split('\n')
        for line in lines:
            if line and 'USB' in line:
                parts = line.split()
                status = parts[0]
                name = ' '.join(parts[2:])
                devices.append({
                    'name': name,
                    'status': f'{status} {parts[1]}'
                })
        return devices

    def _detect_usb_macos(self) -> List[Dict[str, str]]:
        """Detect USB devices on macOS.

        Returns:
            list: Information about detected USB devices on macOS.
        """
        try:
            result = subprocess.run(['system_profiler', 'SPUSBDataType'],
                                    capture_output=True, text=True, check=True)
            usb_devices = self._parse_macos_output(result.stdout)
            self.logger.info(f"Detected USB devices: {usb_devices}")
            return usb_devices
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect USB devices on macOS: {e}")
            return []

    def _parse_macos_output(self, output: str) -> List[Dict[str, str]]:
        """Parse the output of the system_profiler command.

        Args:
            output (str): The output of the system_profiler command.

        Returns:
            list: Parsed information about detected USB devices.
        """
        devices = []
        current_device = {}
        for line in output.split('\n'):
            line = line.strip()
            if not line:
                continue
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                if key == "Product ID":
                    current_device['Product ID'] = value
                elif key:
                    current_device['description'] = key
            if 'description' in current_device and 'Product ID' in current_device:
                devices.append(current_device)
                current_device = {}
        return devices

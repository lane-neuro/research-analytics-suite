"""
USBInterface

This module contains the USBInterface class, which detects and parses USB devices.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.2
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import re
import subprocess
from typing import List, Dict
from research_analytics_suite.hardware_manager.interface.BaseInterface import BaseInterface
import platform


class USBInterface(BaseInterface):
    def __init__(self, logger):
        super().__init__(logger)
        self.os_info = self._detect_os()

    def _detect_os(self) -> str:
        """Detect the operating system."""
        os_name = platform.system()
        if os_name == 'Linux' or os_name == 'Darwin':
            return os_name.lower()
        elif os_name == 'Windows':
            return 'windows'
        else:
            self.logger.error(f"Unsupported OS: {os_name}")
            return 'unsupported'

    def _get_command(self, action: str, identifier: str = '', data: str = '', settings=None) -> List[str]:
        """Get the command to interact with USB devices based on OS and action."""
        if action == 'detect':
            if self.os_info == 'linux':
                return ['lsusb']
            elif self.os_info == 'windows':
                return ['powershell', '-Command', 'Get-PnpDevice -Class USB']
            elif self.os_info == 'darwin':
                return ['system_profiler', 'SPUSBDataType']
            else:
                self.logger.error(f"Unsupported OS: {self.os_info}")
                return []
        elif action == 'read':
            if self.os_info == 'linux':
                return ['cat', f'/sys/bus/usb/devices/{identifier}/product']
            elif self.os_info == 'windows':
                return ['powershell', '-Command',
                        f'Get-WmiObject -Query "SELECT * '
                        f'FROM Win32_PnPEntity WHERE DeviceID=\'{identifier}\'" | Select-Object -ExpandProperty Name']
            elif self.os_info == 'darwin':
                return ['system_profiler', 'SPUSBDataType', f'-detailLevel {identifier}']
        return []

    def _parse_output(self, output: str) -> List[Dict[str, str]]:
        """Parse the output to find USB devices."""
        devices = []
        if self.os_info == 'linux':
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
        elif self.os_info == 'windows':
            lines = output.split('\n')
            for line in lines:
                if line.strip() and not line.startswith('------'):
                    parts = line.split(None, 2)
                    if len(parts) == 3:
                        status, cls, name = parts
                        devices.append({
                            'status': f"{status} {cls}",
                            'name': name.strip()
                        })
        elif self.os_info == 'darwin':
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
                    else:
                        current_device['description'] = key
                if 'description' in current_device and 'Product ID' in current_device:
                    devices.append(current_device)
                    current_device = {}
            if 'description' in current_device and 'Product ID' in current_device:
                devices.append(current_device)
        return devices

    def detect(self) -> List[Dict[str, str]]:
        """Detect USB devices.

        Returns:
            list: Information about detected USB devices.
        """
        command = self._get_command('detect')
        if not command:
            return []
        try:
            result = self._execute_command(command)
            devices = self._parse_output(result)
            self.logger.info(f"Detected devices: {devices}")
            return devices
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect devices: {e}")
            return []

    def read(self, identifier: str) -> str:
        """Read data from a USB device."""
        command = self._get_command('read', identifier)
        if not command:
            return ""
        try:
            result = self._execute_command(command)
            self.logger.info(f"Read from USB device {identifier}: {result}")
            return result
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to read from USB device {identifier}: {e}")
            return ""

    def _execute_command(self, command: List[str]) -> str:
        """Execute a system command.

        Args:
            command (list): The command to execute.

        Returns:
            str: The output of the command.
        """
        self.logger.debug(f"Executing command: {' '.join(command)}")
        try:
            result = subprocess.run(command, capture_output=True, text=True, shell=(self.os_info == 'windows'), check=True)
            self.logger.debug(f"Command output: {result.stdout}")
            self.logger.debug(f"Command stderr: {result.stderr}")
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command '{' '.join(command)}' failed with error: {e}")
            raise

"""
HDMI Module

This module contains the HDMI class, which detects and manages HDMI interfaces.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

from .DisplayInterface import DisplayInterface
from typing import List, Dict


class HDMI(DisplayInterface):
    def detect(self) -> List[Dict[str, str]]:
        """Detect HDMI interfaces.

        Returns:
            list: Information about detected HDMI interfaces.
        """
        command = self._get_command('list')
        output = self._execute_command(command)
        return self._parse_output(output)

    def _get_command(self, action: str) -> List[str]:
        """Get the command to perform an action based on the OS.

        Args:
            action (str): The action to perform.

        Returns:
            list: Command to perform the action.
        """
        if self.os_info == 'linux':
            return ['xrandr']
        elif self.os_info == 'windows':
            return ['powershell', 'Get-WmiObject -Namespace root\\wmi -Class WmiMonitorID']
        elif self.os_info == 'darwin':
            return ['system_profiler', 'SPDisplaysDataType']
        return []

    def _parse_output(self, output: str) -> List[Dict[str, str]]:
        """Parse the raw output to extract HDMI information.

        Args:
            output (str): Raw output from the system command.

        Returns:
            list: Parsed information about detected HDMI interfaces.
        """
        devices = []
        if self.os_info == 'linux':
            devices = self._parse_linux_output(output)
        elif self.os_info == 'windows':
            devices = self._parse_windows_output(output)
        elif self.os_info == 'darwin':
            devices = self._parse_darwin_output(output)
        return devices

    def _parse_linux_output(self, output: str) -> List[Dict[str, str]]:
        devices = []
        for line in output.split('\n'):
            if 'HDMI' in line:
                parts = line.split()
                interface = parts[0]
                device_info = {'interface': interface, 'description': 'HDMI Interface'}
                devices.append(device_info)
        return devices

    def _parse_windows_output(self, output: str) -> List[Dict[str, str]]:
        devices = []
        for line in output.split('\n'):
            if 'HDMI' in line:
                parts = line.split()
                interface = parts[0]
                device_info = {'interface': interface, 'description': 'HDMI Interface'}
                devices.append(device_info)
        return devices

    def _parse_darwin_output(self, output: str) -> List[Dict[str, str]]:
        devices = []
        lines = output.split('\n')
        current_device = None
        for line in lines:
            if 'HDMI' in line:
                if current_device:
                    devices.append(current_device)
                current_device = {'description': 'HDMI Interface'}
            if 'HDMI' in line and current_device is not None:
                current_device['interface'] = line.split()[-1]
        if current_device:
            devices.append(current_device)
        return devices

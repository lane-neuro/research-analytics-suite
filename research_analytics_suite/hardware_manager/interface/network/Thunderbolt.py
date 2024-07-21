"""
Thunderbolt Module

This module contains the Thunderbolt class, which detects and manages Thunderbolt network devices.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

from .NetworkInterface import NetworkInterface
from typing import List, Dict


class Thunderbolt(NetworkInterface):
    def detect(self) -> List[Dict[str, str]]:
        """Detect Thunderbolt network devices.

        Returns:
            list: Information about detected Thunderbolt network devices.
        """
        command = self._get_command('list')
        output = self._execute_command(command)
        return self._parse_output(output)

    def _get_command(self, action: str, identifier: str = '', data: str = '', settings=None) -> List[str]:
        """Get the command to perform an action based on the OS.

        Args:
            action (str): The action to perform.
            identifier (str): The identifier of the device (optional).
            data (str): The data to write (optional).
            settings (dict): The settings to apply (optional).

        Returns:
            list: Command to perform the action.
        """
        if self.os_info == 'linux':
            return self._get_command_linux(action, identifier, data, settings)
        elif self.os_info == 'windows':
            return self._get_command_windows(action, identifier, data, settings)
        elif self.os_info == 'darwin':
            return self._get_command_darwin(action, identifier, data, settings)
        return []

    def _get_command_linux(self, action: str, identifier: str = '', data: str = '', settings=None) -> List[str]:
        if action == 'list':
            return ['lspci', '-nn', '-D']
        return []

    def _get_command_windows(self, action: str, identifier: str = '', data: str = '', settings=None) -> List[str]:
        if action == 'list':
            return ['powershell', 'Get-PnpDevice -Class Net']
        return []

    def _get_command_darwin(self, action: str, identifier: str = '', data: str = '', settings=None) -> List[str]:
        if action == 'list':
            return ['system_profiler', 'SPThunderboltDataType']
        return []

    def _parse_output(self, output: str) -> List[Dict[str, str]]:
        """Parse the raw output to extract Thunderbolt network device information.

        Args:
            output (str): Raw output from the system command.

        Returns:
            list: Parsed information about detected Thunderbolt network devices.
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
            if 'Thunderbolt' in line:
                parts = line.split()
                interface = parts[0]
                device_info = {'interface': interface, 'description': 'Thunderbolt Network Interface'}
                devices.append(device_info)
        return devices

    def _parse_windows_output(self, output: str) -> List[Dict[str, str]]:
        devices = []
        lines = output.split('\n')
        for line in lines:
            if 'Thunderbolt' in line:
                parts = line.split()
                interface = parts[0]
                device_info = {'interface': interface, 'description': 'Thunderbolt Network Interface'}
                devices.append(device_info)
        return devices

    def _parse_darwin_output(self, output: str) -> List[Dict[str, str]]:
        devices = []
        current_device = None
        for line in output.split('\n'):
            if 'Address:' in line:
                address = line.split()[-1]
                devices.append({'interface': address, 'description': 'Thunderbolt Network Interface'})
        return devices

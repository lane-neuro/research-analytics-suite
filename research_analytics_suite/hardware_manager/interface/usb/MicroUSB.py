"""
MicroUSB Module

This module contains the MicroUSB class, which detects and parses Micro-USB devices.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

from .USB import USB
from typing import List, Dict


class MicroUSB(USB):
    def detect(self) -> List[Dict[str, str]]:
        """Detect Micro-USB devices.

        Returns:
            list: Information about detected Micro-USB devices.
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
            return ['lsusb']
        elif action == 'read':
            return ['cat', f'/dev/{identifier}']
        return []

    def _get_command_windows(self, action: str, identifier: str = '', data: str = '', settings=None) -> List[str]:
        if action == 'list':
            return ['powershell', 'Get-PnpDevice -Class USB']
        elif action == 'read':
            return ['powershell', f'Get-Content -Path \\\\.\\{identifier}']
        return []

    def _get_command_darwin(self, action: str, identifier: str = '', data: str = '', settings=None) -> List[str]:
        if action == 'list':
            return ['system_profiler', 'SPUSBDataType']
        elif action == 'read':
            return ['cat', f'/dev/{identifier}']
        return []

    def _parse_output(self, output: str) -> List[Dict[str, str]]:
        """Parse the raw output to extract Micro-USB device information.

        Args:
            output (str): Raw output from the system command.

        Returns:
            list: Parsed information about detected Micro-USB devices.
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
            if line.strip():
                parts = line.split()
                bus = parts[1]
                device = parts[3][:-1]
                vendor_id, product_id = parts[5].split(':')
                device_info = {
                    'bus': bus,
                    'device': device,
                    'vendor_id': vendor_id,
                    'product_id': product_id,
                    'description': ' '.join(parts[6:])
                }
                if 'micro-usb' in device_info['description'].lower():
                    devices.append(device_info)
        return devices

    def _parse_windows_output(self, output: str) -> List[Dict[str, str]]:
        devices = []
        lines = output.split('\n')
        if len(lines) > 2:  # Ensure there are more than just the header lines
            for line in lines[2:]:
                if line.strip():
                    parts = line.split()
                    status = parts[0]
                    device_class = parts[1]
                    friendly_name = ' '.join(parts[2:-1])
                    instance_id = parts[-1]
                    device_info = {
                        'status': status,
                        'class': device_class,
                        'friendly_name': friendly_name,
                        'instance_id': instance_id
                    }
                    if 'micro-usb' in device_info['friendly_name'].lower():
                        devices.append(device_info)
        return devices

    def _parse_darwin_output(self, output: str) -> List[Dict[str, str]]:
        devices = []
        current_device = None
        for line in output.split('\n'):
            if 'Product ID' in line:
                if current_device:
                    devices.append(current_device)
                current_device = {}
            if current_device is not None:
                if 'Product ID' in line:
                    current_device['product_id'] = line.split(':')[-1].strip()
                elif 'Vendor ID' in line:
                    current_device['vendor_id'] = line.split(':')[-1].strip().split()[0]
                    current_device['vendor_name'] = ' '.join(line.split(':')[-1].strip().split()[1:])
                elif 'Location ID' in line:
                    current_device['location_id'] = line.split(':')[-1].strip()
                elif 'Speed' in line:
                    current_device['speed'] = line.split(':')[-1].strip()
        if current_device:
            devices.append(current_device)
        return devices

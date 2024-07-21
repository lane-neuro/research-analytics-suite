"""
WirelessInterface Module

This module contains the WirelessInterface class, which detects and manages wireless devices.

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


class WirelessInterface(NetworkInterface):
    def detect(self) -> List[Dict[str, str]]:
        """Detect Wireless devices.

        Returns:
            list: Information about detected Wireless devices.
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
            return ['iwconfig']
        elif action == 'read':
            return ['iwlist', identifier, 'scan']
        elif action == 'connect':
            ssid = settings['ssid']
            password = settings['password']
            return [
                'nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password
            ]
        return []

    def _get_command_windows(self, action: str, identifier: str = '', data: str = '', settings=None) -> List[str]:
        if action == 'list':
            return ['powershell', 'Get-NetAdapter -InterfaceDescription *Wi-Fi*']
        elif action == 'read':
            return ['powershell', f'Get-NetAdapter -Name {identifier}']
        elif action == 'connect':
            ssid = settings['ssid']
            password = settings['password']
            return [
                'powershell', f'netsh wlan connect name={ssid} key={password}'
            ]
        return []

    def _get_command_darwin(self, action: str, identifier: str = '', data: str = '', settings=None) -> List[str]:
        if action == 'list':
            return ['networksetup', '-listallhardwareports']
        elif action == 'read':
            return ['airport', '-s']
        elif action == 'connect':
            ssid = settings['ssid']
            password = settings['password']
            return [
                'networksetup', '-setairportnetwork', identifier, ssid, password
            ]
        return []

    def _parse_output(self, output: str) -> List[Dict[str, str]]:
        """Parse the raw output to extract Wireless device information.

        Args:
            output (str): Raw output from the system command.

        Returns:
            list: Parsed information about detected Wireless devices.
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
            if 'IEEE 802.11' in line:
                parts = line.split()
                interface = parts[0]
                device_info = {'interface': interface, 'description': 'Wireless Interface'}
                devices.append(device_info)
        return devices

    def _parse_windows_output(self, output: str) -> List[Dict[str, str]]:
        devices = []
        lines = output.split('\n')
        for line in lines:
            if 'Wi-Fi' in line:
                parts = line.split()
                interface = parts[0]
                device_info = {'interface': interface, 'description': 'Wireless Interface'}
                devices.append(device_info)
        return devices

    def _parse_darwin_output(self, output: str) -> List[Dict[str, str]]:
        devices = []
        lines = output.split('\n')
        current_device = None
        for line in lines:
            if 'Hardware Port' in line and 'Wi-Fi' in line:
                if current_device:
                    devices.append(current_device)
                current_device = {'description': 'Wireless Interface'}
            if 'Device' in line and current_device is not None:
                current_device['interface'] = line.split()[-1]
        if current_device:
            devices.append(current_device)
        return devices

    def connect(self, identifier: str, ssid: str, password: str):
        """Connect to a wireless network.

        Args:
            identifier (str): The identifier of the wireless interface.
            ssid (str): The SSID of the wireless network.
            password (str): The password of the wireless network.
        """
        settings = {'ssid': ssid, 'password': password}
        command = self._get_command('connect', identifier, settings=settings)
        output = self._execute_command(command)
        self.logger.debug(f"Connect output: {output}")

    def send_data(self, identifier: str, data: str):
        """Send data over a wireless connection.

        Args:
            identifier (str): The identifier of the wireless interface.
            data (str): The data to send.
        """
        if self.os_info == 'linux':
            self._execute_command(['echo', data, '>', f'/dev/{identifier}'])
        elif self.os_info == 'windows':
            self._execute_command(['powershell', f'echo {data} > {identifier}'])
        elif self.os_info == 'darwin':
            self._execute_command(['sh', '-c', f'echo {data} > {identifier}'])

    def receive_data(self, identifier: str) -> str:
        """Receive data over a wireless connection.

        Args:
            identifier (str): The identifier of the wireless interface.

        Returns:
            str: The received data.
        """
        if self.os_info == 'linux':
            output = self._execute_command(['cat', f'/dev/{identifier}'])
        elif self.os_info == 'windows':
            output = self._execute_command(['powershell', f'Get-Content {identifier}'])
        elif self.os_info == 'darwin':
            output = self._execute_command(['sh', '-c', f'cat {identifier}'])
        return output.strip()

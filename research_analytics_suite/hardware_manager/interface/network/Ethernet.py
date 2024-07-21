"""
Ethernet Module

This module contains the Ethernet class, which detects and manages Ethernet devices.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import socket
from .NetworkInterface import NetworkInterface
from typing import List, Dict


class Ethernet(NetworkInterface):
    def detect(self) -> List[Dict[str, str]]:
        """Detect Ethernet devices.

        Returns:
            list: Information about detected Ethernet devices.
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
            return ['ip', 'link']
        elif action == 'read':
            return ['cat', f'/sys/class/net/{identifier}/address']
        elif action == 'ipconfig':
            return ['ip', 'addr', 'show', identifier]
        return []

    def _get_command_windows(self, action: str, identifier: str = '', data: str = '', settings=None) -> List[str]:
        if action == 'list':
            return ['powershell', 'Get-NetAdapter']
        elif action == 'read':
            return ['powershell', f'Get-NetAdapter -Name {identifier}']
        elif action == 'ipconfig':
            return ['powershell', f'Get-NetIPAddress -InterfaceAlias {identifier}']
        return []

    def _get_command_darwin(self, action: str, identifier: str = '', data: str = '', settings=None) -> List[str]:
        if action == 'list':
            return ['networksetup', '-listallhardwareports']
        elif action == 'read':
            return ['ifconfig', identifier]
        elif action == 'ipconfig':
            return ['ifconfig', identifier]
        return []

    def _parse_output(self, output: str) -> List[Dict[str, str]]:
        """Parse the raw output to extract Ethernet device information.

        Args:
            output (str): Raw output from the system command.

        Returns:
            list: Parsed information about detected Ethernet devices.
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
            if 'state UP' in line:
                parts = line.split()
                interface = parts[1].strip(':')
                device_info = {'interface': interface, 'description': 'Ethernet Interface'}
                devices.append(device_info)
        return devices

    def _parse_windows_output(self, output: str) -> List[Dict[str, str]]:
        devices = []
        lines = output.split('\n')
        for line in lines:
            if 'Ethernet' in line:
                parts = line.split()
                interface = parts[0]
                device_info = {'interface': interface, 'description': 'Ethernet Interface'}
                devices.append(device_info)
        return devices

    def _parse_darwin_output(self, output: str) -> List[Dict[str, str]]:
        devices = []
        lines = output.split('\n')
        current_device = None
        for line in lines:
            if 'Hardware Port' in line and 'Ethernet' in line:
                if current_device:
                    devices.append(current_device)
                current_device = {'description': 'Ethernet Interface'}
            if 'Device' in line and current_device is not None:
                current_device['interface'] = line.split()[-1]
        if current_device:
            devices.append(current_device)
        return devices

    def get_ip_configuration(self, interface: str) -> Dict[str, str]:
        """Get IP configuration for the specified Ethernet interface.

        Args:
            interface (str): The name of the Ethernet interface.

        Returns:
            dict: IP configuration information.
        """
        command = self._get_command('ipconfig', interface)
        output = self._execute_command(command)
        return self._parse_ip_configuration(output)

    def _parse_ip_configuration(self, output: str) -> Dict[str, str]:
        """Parse IP configuration output.

        Args:
            output (str): Raw output from the IP configuration command.

        Returns:
            dict: Parsed IP configuration information.
        """
        ip_info = {}
        if self.os_info == 'linux' or self.os_info == 'darwin':
            lines = output.split('\n')
            for line in lines:
                if 'inet ' in line:
                    parts = line.split()
                    ip_info['ip_address'] = parts[1]
                if 'netmask ' in line:
                    parts = line.split()
                    ip_info['netmask'] = parts[3]
                if 'broadcast ' in line:
                    parts = line.split()
                    ip_info['broadcast'] = parts[5]
        elif self.os_info == 'windows':
            lines = output.split('\n')
            for line in lines:
                if 'IPv4 Address' in line:
                    ip_info['ip_address'] = line.split(':')[-1].strip()
                if 'Subnet Mask' in line:
                    ip_info['netmask'] = line.split(':')[-1].strip()
                if 'Default Gateway' in line:
                    ip_info['gateway'] = line.split(':')[-1].strip()
        return ip_info

    def send_data(self, ip_address: str, port: int, data: str):
        """Send data to a specified IP address and port.

        Args:
            ip_address (str): The IP address to send data to.
            port (int): The port to send data to.
            data (str): The data to send.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip_address, port))
            s.sendall(data.encode())
            s.close()

    def receive_data(self, port: int) -> str:
        """Receive data on the specified port.

        Args:
            port (int): The port to receive data on.

        Returns:
            str: The received data.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', port))
            s.listen()
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024)
                return data.decode()

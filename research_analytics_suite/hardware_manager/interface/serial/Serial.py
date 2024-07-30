"""
Serial

This module contains the Serial class, which detects serial ports.

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
from typing import List, Dict

from research_analytics_suite.hardware_manager.interface.serial.Serial_Interface import Serial_Interface


class Serial(Serial_Interface):
    def detect(self):
        """Detect serial ports.

        Returns:
            list: Information about detected serial ports.
        """
        self.logger.debug("Detecting serial ports...")
        command = self._get_command('detect')
        output = self._execute_command(command)
        return self._parse_output(output)

    def _get_command(self, action: str) -> List[str]:
        """Get the command to detect serial ports based on OS.

        Args:
            action (str): The action to perform.

        Returns:
            list: Command to perform the action.
        """
        if action == 'detect':
            if self.os_info in ['linux', 'darwin']:
                return ['dmesg | grep tty']
            elif self.os_info == 'windows':
                return ['mode']
            else:
                self.logger.error(f"Serial port detection not supported on {self.os_info} platform.")
                return []
        else:
            self.logger.error(f"Unknown action: {action}")
            return []

    def _parse_output(self, output: str) -> List[Dict[str, str]]:
        """Parse the output of the command to find serial ports.

        Args:
            output (str): Raw output from the system command.

        Returns:
            list: Parsed information about detected serial ports.
        """
        if self.os_info in ['linux', 'darwin']:
            return self._parse_serial_output_unix(output)
        elif self.os_info == 'windows':
            return self._parse_serial_output_windows(output)
        else:
            self.logger.error(f"Serial port detection not supported on {self.os_info} platform.")
            return []

    def _parse_serial_output_unix(self, output: str) -> List[Dict[str, str]]:
        """Parse the output of the dmesg command to find serial ports on Unix-like systems."""
        return [{'description': line.strip()} for line in output.split('\n') if line.strip()]

    def _parse_serial_output_windows(self, output: str) -> List[Dict[str, str]]:
        """Parse the output of the mode command to find serial ports on Windows."""
        serial_ports = []
        current_port = []
        for line in output.split('\n'):
            if 'Status for device' in line:
                if current_port:
                    serial_ports.append({'description': '\n'.join(current_port).strip()})
                    current_port = []
            current_port.append(line.strip())
        if current_port:
            serial_ports.append({'description': '\n'.join(current_port).strip()})
        return serial_ports

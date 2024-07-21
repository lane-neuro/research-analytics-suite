"""
USBcInterface Module

This module contains the USBcInterface class, which detects and parses USB-C devices.

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
from typing import List, Dict

from research_analytics_suite.hardware_manager.interface.BaseInterface import BaseInterface


class USBcInterface(BaseInterface):
    def __init__(self, logger):
        super().__init__(logger)

    def _read_output(self) -> str:
        """Read USB-C device information."""
        if self.os_info == 'linux':
            return subprocess.run(['lsusb', '-t'], capture_output=True, text=True, check=True).stdout
        elif self.os_info == 'windows':
            return subprocess.run(['powershell', 'Get-PnpDevice -Class USB'], capture_output=True, text=True, shell=True, check=True).stdout
        elif self.os_info == 'darwin':
            return subprocess.run(['system_profiler', 'SPUSBDataType'], capture_output=True, text=True, check=True).stdout
        else:
            raise subprocess.CalledProcessError(f"Unsupported OS: {self.os_info}")

    def _parse_output(self, output: str) -> List[Dict[str, str]]:
        """Parse the output to find USB-C devices."""
        return [{'device': line} for line in output.split('\n') if 'Type-C' in line and line.strip()]

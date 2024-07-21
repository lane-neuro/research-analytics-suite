"""
HDMI_Interface

This module contains the HDMI_Interface class, which detects and parses HDMI connections.

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


class HDMIInterface(BaseInterface):
    def __init__(self, logger):
        super().__init__(logger)

    def _read_output(self) -> str:
        """Read HDMI device information."""
        if self.os_info == 'linux':
            return subprocess.run(['xrandr', '--verbose'], capture_output=True, text=True, check=True).stdout
        elif self.os_info == 'windows':
            return subprocess.run(['powershell', 'Get-WmiObject -Namespace root\\wmi -Class WmiMonitorConnectionParams'], capture_output=True, text=True, check=True).stdout
        elif self.os_info == 'darwin':
            return subprocess.run(['system_profiler', 'SPDisplaysDataType'], capture_output=True, text=True, check=True).stdout
        else:
            raise subprocess.CalledProcessError(f"Unsupported OS: {self.os_info}")

    def _parse_output(self, output: str) -> List[Dict[str, str]]:
        """Parse the output to find HDMI connections."""
        return [{'device': line} for line in output.split('\n') if 'HDMI' in line and ' connected' in line]

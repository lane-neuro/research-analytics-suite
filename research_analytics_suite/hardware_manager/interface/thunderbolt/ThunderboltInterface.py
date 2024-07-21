"""
ThunderboltInterface

This module contains the ThunderboltInterface class, which detects & parses Thunderbolt devices.

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


class ThunderboltInterface(BaseInterface):
    def __init__(self, logger):
        super().__init__(logger)

    def _read_output(self) -> str:
        """Read Thunderbolt device information."""
        if self.os_info == 'linux':
            return subprocess.run(['boltctl'], capture_output=True, text=True, check=True).stdout
        elif self.os_info == 'windows':
            return subprocess.run(['powershell', 'Get-PnpDevice -Class Thunderbolt'], capture_output=True, text=True, shell=True, check=True).stdout
        elif self.os_info == 'darwin':
            return subprocess.run(['system_profiler', 'SPThunderboltDataType'], capture_output=True, text=True, check=True).stdout
        else:
            raise subprocess.CalledProcessError(f"Unsupported OS: {self.os_info}")

    def _parse_output(self, output: str) -> List[Dict[str, str]]:
        """Parse the output to find Thunderbolt devices."""
        return [{'device': line} for line in output.split('\n') if line.strip()]
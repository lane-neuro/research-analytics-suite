"""
VGADetector

This module contains the VGADetector class, which detects VGA connections.

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
import platform
import re
from typing import List, Dict

class VGADetector:
    def __init__(self, logger):
        self.logger = logger

    def detect_vga(self) -> List[Dict[str, str]]:
        """Detect VGA connections.

        Returns:
            list: Information about detected VGA connections.
        """
        self.logger.info("Detecting VGA connections...")
        os_info = platform.system().lower()
        if os_info == 'linux':
            return self._detect_vga_linux()
        elif os_info == 'windows':
            return self._detect_vga_windows()
        elif os_info == 'darwin':
            return self._detect_vga_macos()
        else:
            self.logger.error(f"Unsupported operating system: {os_info}")
            return []

    def _detect_vga_linux(self) -> List[Dict[str, str]]:
        try:
            result = subprocess.run(['lspci'], capture_output=True, text=True, check=True)
            vga_connections = self._parse_lspci_output(result.stdout)
            self.logger.info(f"Detected VGA connections: {vga_connections}")
            return vga_connections
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect VGA connections on Linux: Command 'lspci' returned non-zero exit status 1.")
            return []

    def _parse_lspci_output(self, output: str) -> List[Dict[str, str]]:
        connections = []
        lines = output.split('\n')
        for line in lines:
            if 'VGA compatible controller' in line:
                match = re.match(r'(\d{2}:\d{2}\.\d) VGA compatible controller: (.+)', line)
                if match:
                    connections.append({
                        'device_id': match.group(1),
                        'description': match.group(2)
                    })
        return connections

    def _detect_vga_windows(self) -> List[Dict[str, str]]:
        try:
            result = subprocess.run(['powershell', 'Get-WmiObject Win32_VideoController'], capture_output=True, text=True, check=True)
            vga_connections = self._parse_windows_output(result.stdout)
            self.logger.info(f"Detected VGA connections: {vga_connections}")
            return vga_connections
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect VGA connections on Windows: Command 'powershell' returned non-zero exit status 1.")
            return []

    def _parse_windows_output(self, output: str) -> List[Dict[str, str]]:
        connections = []
        lines = output.split('\n')
        for line in lines:
            if "Name" in line:
                match = re.search(r'Name\s+:\s+(.+)', line)
                if match:
                    connections.append({'description': match.group(1).strip()})
        return connections

    def _detect_vga_macos(self) -> List[Dict[str, str]]:
        try:
            result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], capture_output=True, text=True, check=True)
            vga_connections = self._parse_macos_output(result.stdout)
            self.logger.info(f"Detected VGA connections: {vga_connections}")
            return vga_connections
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect VGA connections on macOS: Command 'system_profiler' returned non-zero exit status 1.")
            return []

    def _parse_macos_output(self, output: str) -> List[Dict[str, str]]:
        connections = []
        lines = output.split('\n')
        for line in lines:
            if "Chipset Model:" in line:
                match = re.search(r'Chipset Model:\s+(.+)', line)
                if match:
                    connections.append({'description': match.group(1).strip()})
        return connections

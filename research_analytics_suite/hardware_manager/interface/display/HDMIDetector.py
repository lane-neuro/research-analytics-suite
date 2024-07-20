"""
HDMIDetector

This module contains the HDMIDetector class, which detects HDMI connections.

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
import json
from typing import List, Dict


class HDMIDetector:
    def __init__(self, logger):
        self.logger = logger

    def detect_hdmi(self) -> List[str]:
        """Detect HDMI connections.

        Returns:
            list: Information about detected HDMI connections.
        """
        self.logger.info("Detecting HDMI connections...")
        os_info = platform.system().lower()
        if os_info == 'linux':
            return self._detect_hdmi_linux()
        elif os_info == 'windows':
            return self._detect_hdmi_windows()
        elif os_info == 'darwin':
            return self._detect_hdmi_macos()
        else:
            self.logger.error(f"Unsupported operating system: {os_info}")
            return []

    def _detect_hdmi_linux(self) -> List[str]:
        try:
            result = subprocess.run(['xrandr', '--verbose'],
                                    capture_output=True, text=True, shell=False, check=True)
            hdmi_connections = self._parse_xrandr_output(result.stdout)
            self.logger.info(f"Detected HDMI connections: {hdmi_connections}")
            return hdmi_connections
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect HDMI connections on Linux: {e}")
            return []

    def _parse_xrandr_output(self, output: str) -> List[str]:
        return [line for line in output.split('\n') if 'HDMI' in line and ' connected' in line]

    def _detect_hdmi_windows(self) -> List[str]:
        try:
            result = subprocess.run(['powershell', 'Get-WmiObject -Namespace root\\wmi -Class WmiMonitorConnectionParams'],
                                    capture_output=True, text=True, shell=False, check=True)
            hdmi_connections = self._parse_powershell_output(result.stdout)
            self.logger.info(f"Detected HDMI connections: {hdmi_connections}")
            return hdmi_connections
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect HDMI connections on Windows: {e}")
            return []

    def _parse_powershell_output(self, output: str) -> List[str]:
        return [line for line in output.split('\n') if 'HDMI' in line.upper()]

    def _detect_hdmi_macos(self) -> List[str]:
        try:
            result = subprocess.run(['system_profiler', 'SPDisplaysDataType'],
                                    capture_output=True, text=True, shell=False, check=True)
            hdmi_connections = self._parse_macos_output(result.stdout)
            self.logger.info(f"Detected HDMI connections: {hdmi_connections}")
            return hdmi_connections
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect HDMI connections on macOS: {e}")
            return []

    def _parse_macos_output(self, output: str) -> List[str]:
        return [line for line in output.split('\n') if 'HDMI' in line]

    def read_hdmi_info(self) -> Dict[str, List[str]]:
        """Read detailed information about the HDMI connections.

        Returns:
            dict: Detailed information about detected HDMI connections.
        """
        self.logger.info("Reading HDMI information...")
        connections = self.detect_hdmi()
        detailed_info = {conn: self._get_connection_details(conn) for conn in connections}
        return detailed_info

    def _get_connection_details(self, connection: str) -> Dict[str, str]:
        """Get detailed information for a single HDMI connection.

        Args:
            connection (str): The connection string.

        Returns:
            dict: Detailed information about the connection.
        """
        # This is a placeholder for actual implementation.
        # In a real scenario, this method would fetch more detailed information about the connection.
        return {"connection": connection, "status": "active"}

    def write_hdmi_config(self, config: Dict[str, str]) -> bool:
        """Write configuration settings for HDMI connections.

        Args:
            config (dict): Configuration settings to be applied.

        Returns:
            bool: True if the configuration was successfully applied, False otherwise.
        """
        self.logger.info(f"Writing HDMI configuration: {config}")
        try:
            self._apply_config(config)
            self.logger.info(f"Configuration applied: {config}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to write HDMI configuration: {e}")
            return False

    def _apply_config(self, config: Dict[str, str]) -> None:
        """Apply the configuration settings. This is a helper method to simulate the configuration process.

        Args:
            config (dict): Configuration settings to be applied.

        Raises:
            Exception: If applying the configuration fails.
        """
        # Simulate the configuration process and raise an exception if needed
        # This is where the actual implementation would go
        pass

    def transmit_hdmi_info(self, url: str) -> bool:
        """Transmit information about the HDMI connections to an external system.

        Args:
            url (str): The URL of the external system.

        Returns:
            bool: True if the information was successfully transmitted, False otherwise.
        """
        self.logger.info(f"Transmitting HDMI information to {url}...")
        try:
            # Simulate transmission of information
            info = self.read_hdmi_info()
            # Here, you would typically use an HTTP client to POST this info to the external system.
            # For example, using the requests library:
            # response = requests.post(url, json=info)
            # response.raise_for_status()
            self.logger.info(f"Information transmitted: {json.dumps(info, indent=2)}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to transmit HDMI information: {e}")
            return False

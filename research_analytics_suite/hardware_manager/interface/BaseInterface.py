"""
BaseInterface Module

This module contains the BaseInterface class, which is an abstract class that defines the interface for
hardware detection.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
"""
import platform
import subprocess
from abc import ABC, abstractmethod
from typing import List, Dict


class BaseInterface(ABC):
    def __init__(self, logger):
        self.logger = logger
        self.os_info = platform.system().lower()

    def detect(self) -> List[Dict[str, str]]:
        """Detect devices.

        Returns:
            list: Information about detected devices.
        """
        self.logger.info("Detecting devices...")
        try:
            command = self._get_command('detect')
            output = self._execute_command(command)
            devices = self._parse_output(output)
            self.logger.info(f"Detected devices: {devices}")
            return devices
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect devices: {e}")
            return []

    def read(self, identifier: str) -> str:
        """Read data from a device.

        Args:
            identifier (str): The identifier of the device to read from.

        Returns:
            str: Data read from the device.
        """
        self.logger.info(f"Reading data from device {identifier}...")
        try:
            command = self._get_command('read', identifier)
            output = self._execute_command(command)
            self.logger.info(f"Read data: {output}")
            return output
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to read data from device {identifier}: {e}")
            return ""

    def write(self, identifier: str, data: str) -> bool:
        """Write data to a device.

        Args:
            identifier (str): The identifier of the device to write to.
            data (str): The data to write.

        Returns:
            bool: True if the write was successful, False otherwise.
        """
        self.logger.info(f"Writing data to device {identifier}...")
        try:
            command = self._get_command('write', identifier, data)
            self._execute_command(command)
            self.logger.info(f"Data written successfully to {identifier}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to write data to device {identifier}: {e}")
            return False

    def stream(self, identifier: str) -> str:
        """Stream data from a device.

        Args:
            identifier (str): The identifier of the device to stream from.

        Returns:
            str: Streamed data.
        """
        self.logger.info(f"Streaming data from device {identifier}...")
        try:
            command = self._get_command('stream', identifier)
            output = self._execute_command(command)
            self.logger.info(f"Streamed data: {output}")
            return output
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to stream data from device {identifier}: {e}")
            return ""

    def configure(self, identifier: str, settings: Dict[str, str]) -> bool:
        """Configure a device.

        Args:
            identifier (str): The identifier of the device to configure.
            settings (dict): A dictionary of settings to apply.

        Returns:
            bool: True if the configuration was successful, False otherwise.
        """
        self.logger.info(f"Configuring device {identifier} with settings {settings}...")
        try:
            command = self._get_command('configure', identifier, settings=settings)
            self._execute_command(command)
            self.logger.info(f"Device {identifier} configured successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to configure device {identifier}: {e}")
            return False

    def _execute_command(self, command: List[str]) -> str:
        """Execute a system command.

        Args:
            command (list): The command to execute.

        Returns:
            str: The output of the command.
        """
        self.logger.debug(f"Executing command: {' '.join(command)}")
        try:
            result = subprocess.run(command, capture_output=True, text=True, shell=(self.os_info == 'windows'),
                                    check=True)
            self.logger.debug(f"Command output: {result.stdout}")
            self.logger.debug(f"Command stderr: {result.stderr}")
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command '{' '.join(command)}' failed with error: {e}")
            self.logger.error(f"Command stdout: {e.stdout}")
            self.logger.error(f"Command stderr: {e.stderr}")
            raise

    @abstractmethod
    def _get_command(self, action: str, identifier: str = '', data: str = '', settings=None) -> List[str]:
        """Get the command to perform an action based on OS.

        Args:
            action (str): The action to perform (detect, read, write, stream, configure).
            identifier (str): The identifier of the device (optional).
            data (str): The data to write (optional).
            settings (dict): The settings to apply (optional).

        Returns:
            list: Command to perform the action.
        """
        pass

    @abstractmethod
    def _parse_output(self, output: str) -> List[Dict[str, str]]:
        """Parse the raw output to extract device information.

        Args:
            output (str): Raw output from the system command.

        Returns:
            list: Parsed information about detected devices.
        """
        pass

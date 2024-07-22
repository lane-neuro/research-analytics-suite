"""
SerialInterface Module

This module contains the SerialInterface base class, which defines the interface for serial detection.

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
from abc import ABC, abstractmethod
from typing import List, Dict


class Serial_Interface(ABC):
    def __init__(self, logger):
        self.logger = logger
        self.os_info = self._detect_os()

    def _detect_os(self) -> str:
        """Detect the operating system."""
        os_name = platform.system()
        if os_name == 'Linux' or os_name == 'Darwin':
            return os_name.lower()
        elif os_name == 'Windows':
            return 'windows'
        else:
            self.logger.error(f"Unsupported OS: {os_name}")
            return 'unsupported'

    def _execute_command(self, command: List[str]) -> str:
        """Execute a system command.

        Args:
            command (list): The command to execute.

        Returns:
            str: The output of the command.
        """
        self.logger.debug(f"Executing command: {' '.join(command)}")
        try:
            result = subprocess.run(command, capture_output=True, text=True, shell=(self.os_info == 'windows'), check=True)
            self.logger.debug(f"Command output: {result.stdout}")
            self.logger.debug(f"Command stderr: {result.stderr}")
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command '{' '.join(command)}' failed with error: {e}")
            self.logger.error(f"Command stdout: {e.stdout}")
            self.logger.error(f"Command stderr: {e.stderr}")
            raise e

    @abstractmethod
    def detect(self) -> List[Dict[str, str]]:
        """Detect serial interfaces.

        Returns:
            list: Information about detected serial interfaces.
        """
        raise NotImplementedError

    @abstractmethod
    def _get_command(self, action: str) -> List[str]:
        """Get the command to perform an action based on OS.

        Args:
            action (str): The action to perform.

        Returns:
            list: Command to perform the action.
        """
        raise NotImplementedError

    @abstractmethod
    def _parse_output(self, output: str) -> List[Dict[str, str]]:
        """Parse the raw output to extract serial information.

        Args:
            output (str): Raw output from the system command.

        Returns:
            list: Parsed information about detected serial interfaces.
        """
        raise NotImplementedError

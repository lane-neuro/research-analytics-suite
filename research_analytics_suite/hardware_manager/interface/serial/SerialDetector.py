"""
SerialDetector

This module contains the SerialDetector class, which detects serial ports.

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


class SerialDetector:
    def __init__(self, logger):
        self.logger = logger
        self.os_info = platform.system().lower()

    def detect_serial(self):
        """Detect serial ports.

        Returns:
            list: Information about detected serial ports.
        """
        self.logger.info("Detecting serial ports...")

        if self.os_info in ['linux', 'darwin']:
            return self._detect_serial_unix()
        elif self.os_info == 'windows':
            return self._detect_serial_windows()
        else:
            self.logger.error(f"Serial port detection not supported on {self.os_info} platform.")
            return []

    def _detect_serial_unix(self):
        """Detect serial ports on Unix-like systems.

        Returns:
            list: Information about detected serial ports on Unix-like systems.
        """
        try:
            output = self._read_serial_output_unix()
            serial_ports = self._parse_serial_output_unix(output)
            self.logger.info(f"Detected serial ports: {serial_ports}")
            return serial_ports
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect serial ports: {e}")
            return []

    def _read_serial_output_unix(self):
        """Read serial port information on Unix-like systems."""
        result = subprocess.run(['dmesg | grep tty'], capture_output=True, text=True, shell=True, check=True)
        return result.stdout

    def _parse_serial_output_unix(self, output):
        """Parse the output of the dmesg command to find serial ports."""
        return [line for line in output.split('\n') if line.strip()]

    def _detect_serial_windows(self):
        """Detect serial ports on Windows.

        Returns:
            list: Information about detected serial ports on Windows.
        """
        try:
            output = self._read_serial_output_windows()
            serial_ports = self._parse_serial_output_windows(output)
            self.logger.info(f"Detected serial ports: {serial_ports}")
            return serial_ports
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect serial ports: {e}")
            return []

    def _read_serial_output_windows(self):
        """Read serial port information on Windows."""
        result = subprocess.run(['mode'], capture_output=True, text=True, shell=True, check=True)
        return result.stdout

    def _parse_serial_output_windows(self, output):
        """Parse the output of the mode command to find serial ports."""
        serial_ports = []
        current_port = []
        for line in output.split('\n'):
            if 'Status for device' in line:
                if current_port:
                    serial_ports.append('\n'.join(current_port).strip())
                    current_port = []
            current_port.append(line.strip())
        if current_port:
            serial_ports.append('\n'.join(current_port).strip())
        return [port for port in serial_ports if port]

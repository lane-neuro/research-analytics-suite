"""
CPUInstaller

This module contains the CPUInstaller class, which manages CPU detection and task management.

Author: Lane
Copyright: Lane
Credits: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

from ..HardwareDetector import HardwareDetector
from .CPUDetector import CPUDetector


class CPUInstaller(HardwareDetector):
    def detect_hardware(self): ...  # pragma: no cover

    def __init__(self, logger, remote_manager, remote_servers=None):
        super().__init__(logger)
        self.remote_manager = remote_manager
        self.cpu_detector = CPUDetector(logger)
        self.remote_servers = remote_servers or []

    def install(self) -> list[dict]:
        """Detect CPUs and manage tasks.

        Returns:
            list[dict]: Information about detected CPUs.
        """
        try:
            cpu_info = self.cpu_detector.detect_cpus()
        except Exception as e:
            self.logger.error(f"Error during CPU detection: {e}")
            return []

        if not cpu_info:
            self.logger.error("No CPUs detected.")
            return []

        self.logger.info(f"Detected CPUs: {cpu_info}")

        for server in self.remote_servers:
            try:
                self.remote_manager.manage_remote_cpu_server(server)
            except Exception as e:
                self.logger.error(f"Error managing remote server {server}: {e}")

        return cpu_info

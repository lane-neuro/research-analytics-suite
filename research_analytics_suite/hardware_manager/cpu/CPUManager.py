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
from .CPUDetector import CPUDetector


class CPUManager:

    def __init__(self, logger, remote_manager, remote_servers=None):
        self.logger = logger
        self.remote_manager = remote_manager
        self.cpu_detector = CPUDetector(logger)
        self.remote_servers = remote_servers or []
        self.cpus = []

    def detect_hardware(self) -> dict:
        """Detect CPUs and manage tasks.

        Returns:
            dict: Information about detected CPUs.
        """
        try:
            cpu_info = self.cpu_detector.detect_cpu()
        except Exception as e:
            self.logger.error(f"Error during CPU detection: {e}")
            return {}

        if not cpu_info:
            self.logger.error("No CPUs detected.")
            return {}

        for server in self.remote_servers:
            try:
                self.remote_manager.manage_remote_cpu_server(server)
            except Exception as e:
                self.logger.error(f"Error managing remote server {server}: {e}")

        _cpu = {
            "name": cpu_info.get("name", "Unknown CPU"),
            "physical_cores": cpu_info.get("physical_cores", 0),
            "logical_cores": cpu_info.get("logical_cores", 0),
            "frequency": cpu_info.get("frequency", "Unknown"),
            "architecture": cpu_info.get("architecture", "Unknown")
        }
        self.cpus.append(_cpu)
        self.logger.debug(f"Detected CPU: {_cpu['name']} with {_cpu['physical_cores']} physical cores and "
                          f"{_cpu['logical_cores']} logical cores.")

        return cpu_info

    @property
    def cpu_name(self, index: int = 0) -> str:
        """Get the name of the CPU.

        Args:
            index (int): Index of the CPU to get the name for. Defaults to 0.

        Returns:
            str: Name of the CPU.
        """
        return self.cpus[index].name if index < len(self.cpus) else "Unknown CPU"


    @property
    def cpu_core_count(self, index: int = 0) -> int:
        """Get the number of CPU cores.

        Args:
            index (int): Index of the CPU to get the number of cores for. Defaults to 0.

        Returns:
            int: Number of physical cores of the CPU.
        """
        return self.cpus[index].physical_cores if index < len(self.cpus) else 0

    @property
    def cpu_logical_core_count(self, index: int = 0) -> int:
        """Get the number of logical CPU cores.

        Args:
            index (int): Index of the CPU to get the number of logical cores for. Defaults to 0.

        Returns:
            int: Number of logical cores of the CPU.
        """
        return self.cpus[index].logical_cores if index < len(self.cpus) else 0

    @property
    def cpu_frequency(self, index: int = 0) -> str:
        """Get the frequency of the CPU.

        Args:
            index (int): Index of the CPU to get the frequency for. Defaults to 0.

        Returns:
            str: Frequency of the CPU.
        """
        return self.cpus[index].frequency if index < len(self.cpus) else "Unknown Frequency"

    @property
    def cpu_architecture(self, index: int = 0) -> str:
        """Get the architecture of the CPU.

        Args:
            index (int): Index of the CPU to get the architecture for. Defaults to 0.

        Returns:
            str: Architecture of the CPU.
        """
        return self.cpus[index].architecture if index < len(self.cpus) else "Unknown Architecture"

    def list_cpus(self) -> list:
        """List all detected CPUs.

        Returns:
            list: List of CPU names.
        """
        return [cpu['name'] for cpu in self.cpus] if self.cpus else ["No CPUs detected"]

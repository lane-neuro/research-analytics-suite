"""
MemoryInfo

This module contains the MemoryInfo class, which gathers information about the system's memory (RAM).

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import psutil


class MemoryInfo:
    def __init__(self, logger):
        self.logger = logger

    def get_memory_info(self):
        """Get memory information.

        Returns:
            dict: Information about the system's memory.
        """
        memory_info = {
            "total": self.total_memory,
            "available": self.available_memory,
            "percent": self.memory_percent,
            "used": self.used_memory,
            "free": self.free_memory
        }
        return memory_info

    @property
    def total_memory(self):
        """Get total memory in bytes."""
        return psutil.virtual_memory().total

    @property
    def available_memory(self):
        """Get available memory in bytes."""
        return psutil.virtual_memory().available

    @property
    def used_memory(self):
        """Get used memory in bytes."""
        return psutil.virtual_memory().used

    @property
    def free_memory(self):
        """Get free memory in bytes."""
        return psutil.virtual_memory().free

    @property
    def memory_percent(self):
        """Get memory usage percentage."""
        return psutil.virtual_memory().percent


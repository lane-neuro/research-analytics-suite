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
        self.logger.info("Getting memory information...")
        mem = psutil.virtual_memory()
        memory_info = {
            "total": mem.total,
            "available": mem.available,
            "percent": mem.percent,
            "used": mem.used,
            "free": mem.free
        }
        self.logger.info(f"Memory information: {memory_info}")
        return memory_info

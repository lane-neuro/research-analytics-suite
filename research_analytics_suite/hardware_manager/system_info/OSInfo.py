"""
OSInfo

This module contains the OSInfo class, which gathers information about the system's operating system.

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


class OSInfo:
    def __init__(self, logger):
        self.logger = logger

    def get_os_info(self):
        """Get operating system information.

        Returns:
            dict: Information about the system's operating system.
        """
        os_info = {
            "system": platform.system(),
            "node": platform.node(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor()
        }
        return os_info

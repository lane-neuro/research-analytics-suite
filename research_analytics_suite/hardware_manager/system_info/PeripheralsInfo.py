"""
PeripheralsInfo

This module contains the PeripheralsInfo class, which gathers information about the system's connected peripherals.

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


class PeripheralsInfo:
    def __init__(self, logger):
        self.logger = logger

    def get_peripherals_info(self):
        """Get peripherals information.

        Returns:
            list: Information about the system's connected peripherals.
        """
        try:
            result = subprocess.run(['lsusb'], capture_output=True, text=True, check=True)
            peripherals = result.stdout.split('\n')
            return peripherals
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get peripherals information: {e}")
            return []

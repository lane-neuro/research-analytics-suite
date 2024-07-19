"""
InterfaceStatusChecker

This module contains the InterfaceStatusChecker class, which verifies the connected interfaces and their
initialization status.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from ..interface import InterfaceManager


class InterfaceStatusChecker:
    def __init__(self, logger):
        self.logger = logger
        self.interface_manager = InterfaceManager(logger)

    def check_status(self):
        """Check the status of all interfaces.

        Returns:
            dict: The status report of all interfaces.
        """
        self.logger.info("Checking status of all interfaces...")
        interfaces = self.interface_manager.detect_interfaces()
        status_report = {}

        for interface_type, devices in interfaces.items():
            if devices:
                status_report[interface_type] = 'Connected and initialized'
                self.logger.info(f"{interface_type}: {len(devices)} devices connected and initialized.")
            else:
                status_report[interface_type] = 'No devices detected'
                self.logger.warning(f"{interface_type}: No devices detected.")

        return status_report

    def print_status_report(self, status_report):
        """Print the status report of all interfaces.

        Args:
            status_report (dict): The status report of all interfaces.
        """
        self.logger.info("Interface Status Report:")
        for interface_type, status in status_report.items():
            self.logger.info(f"{interface_type}: {status}")

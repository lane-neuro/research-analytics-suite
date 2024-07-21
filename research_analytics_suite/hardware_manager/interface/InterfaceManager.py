"""
InterfaceManager

This module contains the InterfaceManager class, which manages the detection of various hardware interfaces.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.2
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

from .usb.USBInterface import USBInterface
from .usb.USBcInterface import USBcInterface
from .usb.MicroUSBInterface import MicroUSBInterface


class InterfaceManager:
    def __init__(self, logger):
        self.logger = logger
        self.interfaces = {
            'USB': USBInterface(logger),
            'USB-C': USBcInterface(logger),
            'Micro-USB': MicroUSBInterface(logger),
        }

    def detect_interfaces(self):
        """Detect all hardware interfaces.

        Returns:
            dict: Information about detected interfaces.
        """
        detected_interfaces = {}
        for interface_name, interface in self.interfaces.items():
            try:
                self.logger.info(f"Detecting {interface_name} interfaces...")
                detected_interfaces[interface_name] = interface.detect()
            except Exception as e:
                self.logger.error(f"Error detecting {interface_name} interfaces: {e}")
                detected_interfaces[interface_name] = None
        return detected_interfaces

    def add_interface(self, name, interface):
        """Add a new interface for detection.

        Args:
            name (str): The name of the interface.
            interface (BaseInterface): An instance of the interface.
        """
        self.logger.info(f"Adding {name} interface for detection.")
        self.interfaces[name] = interface

    def remove_interface(self, name):
        """Remove an interface from detection.

        Args:
            name (str): The name of the interface.
        """
        if name in self.interfaces:
            self.logger.info(f"Removing {name} interface from detection.")
            del self.interfaces[name]
        else:
            self.logger.warning(f"Interface {name} not found in the list of interfaces.")

    def get_interface(self, name):
        """Get a specific interface.

        Args:
            name (str): The name of the interface.

        Returns:
            BaseInterface: The interface instance.
        """
        return self.interfaces.get(name, None)

    def list_interfaces(self):
        """List all available interfaces.

        Returns:
            list: Names of all available interfaces.
        """
        return list(self.interfaces.keys())

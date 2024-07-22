"""
InterfaceManager

This module contains the InterfaceManager class, which manages the detection of various hardware interfaces.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from asyncio import iscoroutinefunction
from research_analytics_suite.commands import link_class_commands, command

from .usb.USB import USB
from .usb.USBc import USBc
from .usb.MicroUSB import MicroUSB
from .network.Ethernet import Ethernet
from .network.Wireless import Wireless
from .network.Bluetooth import Bluetooth
from .network.Thunderbolt import Thunderbolt


@link_class_commands
class InterfaceManager:
    def __init__(self, logger):
        self.logger = logger
        self.base_interfaces = {
            'USB': USB(logger),
            'USB-C': USBc(logger),
            'Micro-USB': MicroUSB(logger),
            'Ethernet': Ethernet(logger),
            'Wireless': Wireless(logger),
            'Bluetooth': Bluetooth(logger),
            'Thunderbolt': Thunderbolt(logger),
        }
        self.interfaces = {}

    @command
    async def detect_interfaces(self):
        """Detect all hardware interfaces.

        Returns:
            dict: Information about detected interfaces.
        """
        detected_interfaces = {}
        for interface_name, interface in self.base_interfaces.items():
            try:
                self.logger.info(f"Detecting {interface_name} interfaces...")
                detected_interfaces[interface_name] = await interface.detect() if iscoroutinefunction(
                    interface.detect) else interface.detect()
            except Exception as e:
                self.logger.error(f"Error detecting {interface_name} interfaces: {e}")
                detected_interfaces[interface_name] = None
        self.interfaces = detected_interfaces

    def add_interface(self, name, interface):
        """Add a new interface for detection.

        Args:
            name (str): The name of the interface.
            interface (BaseInterface): An instance of the interface.
        """
        self.logger.info(f"Adding {name} interface for detection.")
        self.base_interfaces[name] = interface

    def remove_interface(self, name):
        """Remove an interface from detection.

        Args:
            name (str): The name of the interface.
        """
        if name in self.interfaces:
            self.logger.info(f"Removing {name} interface from detection.")
            del self.base_interfaces[name]
        else:
            self.logger.warning(f"Interface {name} not found in the list of interfaces.")

    @command
    def get_interface(self, name):
        """Get a specific interface.

        Args:
            name (str): The name of the interface.

        Returns:
            BaseInterface: The interface instance.
        """
        return self.interfaces.get(name, None)

    @command
    def list_interfaces(self):
        """List all available interfaces.

        Returns:
            list: Names of all available interfaces.
        """
        return list(self.interfaces.keys())

    @command
    def print_interfaces(self):
        """Print all available interfaces."""
        if not self.interfaces:
            return
        self.logger.info("Available interfaces:")
        for interface_type in self.interfaces:
            for interface in self.interfaces[interface_type]:
                self.logger.info(f"- {interface}")

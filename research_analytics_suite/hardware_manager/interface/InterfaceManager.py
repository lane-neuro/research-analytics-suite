"""
InterfaceManager

This module contains the InterfaceManager class, which manages the detection of various hardware interfaces.

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
import asyncio
from asyncio import iscoroutinefunction

from .usb.USB import USB
from .usb.USBc import USBc
from .usb.MicroUSB import MicroUSB
from .network.Ethernet import Ethernet
from .network.Wireless import Wireless
from .network.Bluetooth import Bluetooth
from .network.Thunderbolt import Thunderbolt
from .display.DisplayPort import DisplayPort
from .display.HDMI import HDMI
from .display.VGA import VGA
from .display.PCI import PCI


class InterfaceManager:
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance') or not cls._instance:
            cls._instance = super(InterfaceManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            from research_analytics_suite.utils import CustomLogger
            self.logger = CustomLogger()
            self.base_interfaces = {
                'USB': USB(self.logger),
                'USB-C': USBc(self.logger),
                'Micro-USB': MicroUSB(self.logger),
                'Ethernet': Ethernet(self.logger),
                'Wireless': Wireless(self.logger),
                'Bluetooth': Bluetooth(self.logger),
                'Thunderbolt': Thunderbolt(self.logger),
                'DisplayPort': DisplayPort(self.logger),
                'HDMI': HDMI(self.logger),
                'VGA': VGA(self.logger),
                'PCI': PCI(self.logger)
            }
            self.interfaces = {}

            self._initialized = True

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
                self.logger.error(Exception(f"Error detecting {interface_name} interfaces: {e}"),
                                  self.__class__.__name__)
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

    def print_interfaces(self):
        """Print all available interfaces."""
        if not self.interfaces:
            return
        self.logger.info("Available interfaces:")
        for interface_type in self.interfaces:
            for interface in self.interfaces[interface_type]:
                self.logger.info(f"- {interface}")

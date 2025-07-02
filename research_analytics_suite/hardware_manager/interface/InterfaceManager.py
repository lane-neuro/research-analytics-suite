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
import asyncio
from asyncio import iscoroutinefunction
from research_analytics_suite.commands import link_class_commands, command

from .usb.USB import USB
from .network.Ethernet import Ethernet
from .network.Wireless import Wireless
from .network.Bluetooth import Bluetooth
from .network.Thunderbolt import Thunderbolt
from .display.DisplayPort import DisplayPort
from .display.HDMI import HDMI
from .display.VGA import VGA
from .display.PCI import PCI
from .serial.Serial import Serial


@link_class_commands
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
                'Ethernet': Ethernet(self.logger),
                'Wireless': Wireless(self.logger),
                'Bluetooth': Bluetooth(self.logger),
                'Thunderbolt': Thunderbolt(self.logger),
                'DisplayPort': DisplayPort(self.logger),
                'HDMI': HDMI(self.logger),
                'VGA': VGA(self.logger),
                'PCI': PCI(self.logger),
                'Serial': Serial(self.logger)
            }
            self.interfaces = {}

            self._initialized = True

    @command
    def detect_interfaces(self):
        """Detect all hardware interfaces.

        Returns:
            dict: Information about detected interfaces.
        """
        detected_interfaces = {}
        for interface_name, interface in self.base_interfaces.items():
            try:
                self.logger.debug(f"Detecting {interface_name} interfaces...", self.__class__.__name__)
                detected_interfaces[interface_name] = interface.detect()
            except Exception as e:
                self.logger.warning(f"Error detecting {interface_name} interfaces, see debug log for details.")
                self.logger.debug(f"Error detecting {interface_name} interfaces: {e}", self.__class__.__name__)
                detected_interfaces[interface_name] = None
        self.interfaces = detected_interfaces

    def add_interface(self, name, interface):
        """Add a new interface for detection.

        Args:
            name (str): The name of the interface.
            interface (BaseInterface): An instance of the interface.
        """
        self.logger.debug(f"Adding {name} interface for detection.", self.__class__.__name__)
        self.base_interfaces[name] = interface

    def remove_interface(self, name):
        """Remove an interface from detection.

        Args:
            name (str): The name of the interface.
        """
        if name in self.interfaces:
            self.logger.debug(f"Removing {name} interface from detection.", self.__class__.__name__)
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
    def get_interfaces_by_type(self, interface_type):
        """Get interfaces by type.

        Args:
            interface_type (str): The type of the interface.

        Returns:
            list: List of interfaces of the specified type.
        """
        return self.interfaces.get(interface_type, [])

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
        self.logger.debug("Available interfaces:", self.__class__.__name__)
        for interface_type in self.interfaces:
            for interface in self.interfaces[interface_type]:
                self.logger.debug(f"- {interface}", self.__class__.__name__)

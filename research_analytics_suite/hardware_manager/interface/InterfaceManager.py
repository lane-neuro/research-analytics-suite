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
from .usb.USBInterface import USBInterface
from .usb.USBcInterface import USBcInterface
from .thunderbolt.ThunderboltInterface import ThunderboltInterface
from .display.HDMI_Interface import HDMIInterface
from .serial.SerialDetector import SerialDetector
from .display.VGADetector import VGADetector
from .display.DisplayPortDetector import DisplayPortDetector
from .network.EthernetDetector import EthernetDetector
from .audio.AudioDetector import AudioDetector


class InterfaceManager:
    def __init__(self, logger):
        self.logger = logger
        self.usb_detector = USBInterface(logger)
        self.usb_c_detector = USBcInterface(logger)
        self.thunderbolt_detector = ThunderboltInterface(logger)
        self.serial_detector = SerialDetector(logger)
        self.vga_detector = VGADetector(logger)
        self.hdmi_detector = HDMIInterface(logger)
        self.displayport_detector = DisplayPortDetector(logger)
        self.ethernet_detector = EthernetDetector(logger)
        self.audio_detector = AudioDetector(logger)

    def detect_interfaces(self):
        """Detect all hardware interfaces.

        Returns:
            dict: Information about detected interfaces.
        """
        interfaces = {}
        interfaces['USB'] = self.usb_detector.detect()
        interfaces['USB-C'] = self.usb_c_detector.detect()
        interfaces['Thunderbolt'] = self.thunderbolt_detector.detect()
        interfaces['Serial'] = self.serial_detector.detect_serial()
        interfaces['VGA'] = self.vga_detector.detect_vga()
        interfaces['HDMI'] = self.hdmi_detector.detect()
        interfaces['DisplayPort'] = self.displayport_detector.detect_displayport()
        interfaces['Ethernet'] = self.ethernet_detector.detect_ethernet()
        interfaces['Audio'] = self.audio_detector.detect_audio()
        return interfaces

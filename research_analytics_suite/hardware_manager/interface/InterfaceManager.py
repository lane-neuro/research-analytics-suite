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
from .usb.USBDetector import USBDetector
from .usb.USBcDetector import USBcDetector
from .thunderbolt.ThunderboltDetector import ThunderboltDetector
from .serial.SerialDetector import SerialDetector
from .display.VGADetector import VGADetector
from .display.HDMIDetector import HDMIDetector
from .display.DisplayPortDetector import DisplayPortDetector
from .network.EthernetDetector import EthernetDetector
from .audio.AudioDetector import AudioDetector


class InterfaceManager:
    def __init__(self, logger):
        self.logger = logger
        self.usb_detector = USBDetector(logger)
        self.usb_c_detector = USBcDetector(logger)
        self.thunderbolt_detector = ThunderboltDetector(logger)
        self.serial_detector = SerialDetector(logger)
        self.vga_detector = VGADetector(logger)
        self.hdmi_detector = HDMIDetector(logger)
        self.displayport_detector = DisplayPortDetector(logger)
        self.ethernet_detector = EthernetDetector(logger)
        self.audio_detector = AudioDetector(logger)

    def detect_interfaces(self):
        """Detect all hardware interfaces.

        Returns:
            dict: Information about detected interfaces.
        """
        interfaces = {}
        interfaces['USB'] = self.usb_detector.detect_usb()
        interfaces['USB-C'] = self.usb_c_detector.detect_usb_c()
        interfaces['Thunderbolt'] = self.thunderbolt_detector.detect_thunderbolt()
        interfaces['Serial'] = self.serial_detector.detect_serial()
        interfaces['VGA'] = self.vga_detector.detect_vga()
        interfaces['HDMI'] = self.hdmi_detector.detect_hdmi()
        interfaces['DisplayPort'] = self.displayport_detector.detect_displayport()
        interfaces['Ethernet'] = self.ethernet_detector.detect_ethernet()
        interfaces['Audio'] = self.audio_detector.detect_audio()
        return interfaces

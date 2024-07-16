"""
USBInput Module

Defines the USBInput class for handling live data input from USB sources.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import serial

from research_analytics_suite.commands import command, link_class_commands
from research_analytics_suite.data_engine.data_streams.BaseInput import BaseInput


@link_class_commands
class USBInput(BaseInput):
    """
    Class for handling live data input from a USB source.

    Attributes:
        port: The USB port.
        baud_rate: The baud rate for the USB connection.
        serial_connection: The serial connection to the USB port.
    """
    def __init__(self, port, baud_rate=9600):
        """
        Initializes the USBInput instance.

        Args:
            port (str): The USB port.
            baud_rate (int): The baud rate for the USB connection. Default is 9600.
        """
        super().__init__(source="USB")
        self.port = port
        self.baud_rate = baud_rate
        self.serial_connection = serial.Serial(port, baud_rate)

    @command
    def read_data(self):
        """
        Reads data from the USB source.

        Returns:
            The data read from the USB source.
        """
        if self.serial_connection.in_waiting:
            return self.serial_connection.readline().decode('utf-8').strip()
        return None

    @command
    def close(self):
        """
        Closes the USB connection.
        """
        if self.serial_connection.is_open:
            self.serial_connection.close()

"""
Bluetooth Module

This module contains the Bluetooth class, which detects and manages Bluetooth devices.

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
from bleak import BleakScanner, BleakClient
from typing import List, Dict


class Bluetooth:
    def __init__(self, logger):
        self.logger = logger
        self.os_info = self._detect_os()

    def _detect_os(self) -> str:
        """Detect the operating system."""
        os_name = platform.system()
        if os_name == 'Linux' or os_name == 'Darwin':
            return os_name.lower()
        elif os_name == 'Windows':
            return 'windows'
        else:
            self.logger.error(f"Unsupported OS: {os_name}")
            return 'unsupported'

    async def detect(self) -> List[Dict[str, str]]:
        """Detect Bluetooth devices.

        Returns:
            list: Information about detected Bluetooth devices.
        """
        devices = await BleakScanner.discover()
        self.logger.debug(f"Detected Bluetooth devices: {devices}")
        return [{'address': device.address, 'name': device.name} for device in devices]

    async def connect(self, address: str) -> BleakClient:
        """Connect to a Bluetooth device.

        Args:
            address (str): The address of the Bluetooth device.

        Returns:
            BleakClient: The BLE client connected to the device.
        """
        client = BleakClient(address)
        await client.connect()
        self.logger.debug(f"Connected to Bluetooth device: {address} with client: {client} "
                          f"and services: {client.services}")
        return client

    async def send_data(self, client: BleakClient, characteristic: str, data: str):
        """Send data over a Bluetooth connection.

        Args:
            client (BleakClient): The BLE client.
            characteristic (str): The characteristic UUID to write to.
            data (str): The data to send.
        """
        self.logger.debug(f"Sending data: {data} to characteristic: {characteristic} on device: {client.address}")
        await client.write_gatt_char(characteristic, data.encode())

    async def receive_data(self, client: BleakClient, characteristic: str) -> str:
        """Receive data over a Bluetooth connection.

        Args:
            client (BleakClient): The BLE client.
            characteristic (str): The characteristic UUID to read from.

        Returns:
            str: The received data.
        """
        self.logger.debug(f"Receiving data from characteristic: {characteristic} on device: {client.address}")
        data = await client.read_gatt_char(characteristic)
        self.logger.debug(f"Received data: {data} from characteristic: {characteristic} on device: {client.address}")
        return data.decode()

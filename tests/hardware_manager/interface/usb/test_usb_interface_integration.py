import subprocess

import pytest
import logging
from unittest import mock
from research_analytics_suite.hardware_manager.interface.usb.USBInterface import USBInterface

class TestUSBInterfaceIntegration:
    @pytest.fixture
    def logger(self):
        logger = logging.getLogger("USBInterfaceIntegrationTest")
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    @pytest.fixture
    def usb_interface(self, logger):
        with mock.patch('platform.system', return_value='Windows'):
            return USBInterface(logger)

    def test_detect_usb_devices(self, usb_interface):
        usb_interface.logger.info("Starting test_detect_usb_devices")
        with mock.patch('subprocess.run', return_value=mock.Mock(stdout="Status OK USB Composite Device\nStatus OK USB Root Hub\n", returncode=0)):
            devices = usb_interface.detect()
            usb_interface.logger.info(f"Detected devices: {devices}")
            assert devices, "No USB devices detected."

    def test_read_usb_device(self, usb_interface):
        usb_interface.logger.info("Starting test_read_usb_device")
        identifier = "USB\\VID_046D&PID_082D"
        with mock.patch('subprocess.run', return_value=mock.Mock(stdout="FriendlyName", returncode=0)):
            data = usb_interface.read(identifier)
            usb_interface.logger.info(f"Read data from device {identifier}: {data}")
            assert data, f"No data read from USB device with identifier {identifier}."

    def test_read_usb_device_failure(self, usb_interface):
        usb_interface.logger.info("Starting test_read_usb_device_failure")
        identifier = "USB\\VID_046D&PID_082D"
        with mock.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'cmd')):
            data = usb_interface.read(identifier)
            usb_interface.logger.info(f"Read data from device {identifier}: {data}")
            assert data == "", f"Data should be empty for failed read from USB device with identifier {identifier}."

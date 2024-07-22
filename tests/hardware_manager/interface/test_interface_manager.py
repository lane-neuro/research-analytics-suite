import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock, call
from research_analytics_suite.hardware_manager.interface.InterfaceManager import InterfaceManager


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.fixture
def mock_interfaces(mock_logger):
    with patch('research_analytics_suite.hardware_manager.interface.usb.USB.USB', autospec=True) as MockUSB, \
            patch('research_analytics_suite.hardware_manager.interface.usb.USBc.USBc', autospec=True) as MockUSBc, \
            patch('research_analytics_suite.hardware_manager.interface.usb.MicroUSB.MicroUSB',
                  autospec=True) as MockMicroUSB, \
            patch('research_analytics_suite.hardware_manager.interface.network.Ethernet.Ethernet',
                  autospec=True) as MockEthernet, \
            patch('research_analytics_suite.hardware_manager.interface.network.Wireless.Wireless',
                  autospec=True) as MockWireless, \
            patch('research_analytics_suite.hardware_manager.interface.network.Bluetooth.Bluetooth',
                  autospec=True) as MockBluetooth, \
            patch('research_analytics_suite.hardware_manager.interface.network.Thunderbolt.Thunderbolt',
                  autospec=True) as MockThunderbolt, \
            patch('research_analytics_suite.hardware_manager.interface.display.DisplayPort.DisplayPort',
                  autospec=True) as MockDisplayPort, \
            patch('research_analytics_suite.hardware_manager.interface.display.HDMI.HDMI', autospec=True) as MockHDMI, \
            patch('research_analytics_suite.hardware_manager.interface.display.VGA.VGA', autospec=True) as MockVGA, \
            patch('research_analytics_suite.hardware_manager.interface.display.PCI.PCI', autospec=True) as MockPCI:
        MockUSB.return_value.detect = AsyncMock(return_value=[{'device': 'USB1'}])
        MockUSBc.return_value.detect = AsyncMock(return_value=[{'device': 'USB-C1'}])
        MockMicroUSB.return_value.detect = AsyncMock(return_value=[{'device': 'MicroUSB1'}])
        MockEthernet.return_value.detect = AsyncMock(return_value=[{'device': 'Ethernet1'}])
        MockWireless.return_value.detect = AsyncMock(return_value=[{'device': 'Wireless1'}])
        MockBluetooth.return_value.detect = AsyncMock(return_value=[{'device': 'Bluetooth1'}])
        MockThunderbolt.return_value.detect = AsyncMock(return_value=[{'device': 'Thunderbolt1'}])
        MockDisplayPort.return_value.detect = AsyncMock(return_value=[{'device': 'DisplayPort1'}])
        MockHDMI.return_value.detect = AsyncMock(return_value=[{'device': 'HDMI1'}])
        MockVGA.return_value.detect = AsyncMock(return_value=[{'device': 'VGA1'}])
        MockPCI.return_value.detect = AsyncMock(return_value=[{'device': 'PCI1'}])

        yield {
            'USB': MockUSB,
            'USB-C': MockUSBc,
            'Micro-USB': MockMicroUSB,
            'Ethernet': MockEthernet,
            'Wireless': MockWireless,
            'Bluetooth': MockBluetooth,
            'Thunderbolt': MockThunderbolt,
            'DisplayPort': MockDisplayPort,
            'HDMI': MockHDMI,
            'VGA': MockVGA,
            'PCI': MockPCI
        }


@pytest.mark.asyncio
class TestInterfaceManager:
    @pytest.fixture(autouse=True)
    async def setup(self, mock_logger, mock_interfaces):
        self.manager = InterfaceManager()
        self.manager.logger = mock_logger
        self.mock_interfaces = mock_interfaces

        self.manager.base_interfaces = {
            'USB': mock_interfaces['USB'](mock_logger),
            'USB-C': mock_interfaces['USB-C'](mock_logger),
            'Micro-USB': mock_interfaces['Micro-USB'](mock_logger),
            'Ethernet': mock_interfaces['Ethernet'](mock_logger),
            'Wireless': mock_interfaces['Wireless'](mock_logger),
            'Bluetooth': mock_interfaces['Bluetooth'](mock_logger),
            'Thunderbolt': mock_interfaces['Thunderbolt'](mock_logger),
            'DisplayPort': mock_interfaces['DisplayPort'](mock_logger),
            'HDMI': mock_interfaces['HDMI'](mock_logger),
            'VGA': mock_interfaces['VGA'](mock_logger),
            'PCI': mock_interfaces['PCI'](mock_logger)
        }

    async def test_singleton(self):
        manager1 = InterfaceManager()
        manager2 = InterfaceManager()
        assert manager1 is manager2

    async def test_detect_interfaces(self):
        await self.manager.detect_interfaces()
        assert self.manager.interfaces == {
            'USB': [{'device': 'USB1'}],
            'USB-C': [{'device': 'USB-C1'}],
            'Micro-USB': [{'device': 'MicroUSB1'}],
            'Ethernet': [{'device': 'Ethernet1'}],
            'Wireless': [{'device': 'Wireless1'}],
            'Bluetooth': [{'device': 'Bluetooth1'}],
            'Thunderbolt': [{'device': 'Thunderbolt1'}],
            'DisplayPort': [{'device': 'DisplayPort1'}],
            'HDMI': [{'device': 'HDMI1'}],
            'VGA': [{'device': 'VGA1'}],
            'PCI': [{'device': 'PCI1'}]
        }

    async def test_add_interface(self):
        mock_new_interface = MagicMock()
        mock_new_interface.detect = AsyncMock(return_value=[{'device': 'NewInterface1'}])
        self.manager.add_interface('NewInterface', mock_new_interface)
        await self.manager.detect_interfaces()
        assert self.manager.interfaces['NewInterface'] == [{'device': 'NewInterface1'}]

    async def test_remove_interface(self):
        mock_new_interface = MagicMock()
        mock_new_interface.detect = AsyncMock(return_value=[{'device': 'NewInterface1'}])
        self.manager.add_interface('NewInterface', mock_new_interface)
        await self.manager.detect_interfaces()
        assert 'NewInterface' in self.manager.interfaces
        self.manager.remove_interface('NewInterface')
        await self.manager.detect_interfaces()
        assert 'NewInterface' not in self.manager.interfaces

    async def test_list_interfaces(self):
        await self.manager.detect_interfaces()
        interfaces_list = self.manager.list_interfaces()
        assert interfaces_list == [
            'USB', 'USB-C', 'Micro-USB', 'Ethernet', 'Wireless', 'Bluetooth', 'Thunderbolt',
            'DisplayPort', 'HDMI', 'VGA', 'PCI'
        ]

    async def test_get_interface(self):
        await self.manager.detect_interfaces()
        usb_interface = self.manager.get_interface('USB')
        assert usb_interface == [{'device': 'USB1'}]

    @pytest.mark.asyncio
    async def test_print_interfaces(self):
        await self.manager.detect_interfaces()
        self.manager.print_interfaces()
        expected_calls = [
            call.info("Available interfaces:"),
            call.info("- {'device': 'USB1'}"),
            call.info("- {'device': 'USB-C1'}"),
            call.info("- {'device': 'MicroUSB1'}"),
            call.info("- {'device': 'Ethernet1'}"),
            call.info("- {'device': 'Wireless1'}"),
            call.info("- {'device': 'Bluetooth1'}"),
            call.info("- {'device': 'Thunderbolt1'}"),
            call.info("- {'device': 'DisplayPort1'}"),
            call.info("- {'device': 'HDMI1'}"),
            call.info("- {'device': 'VGA1'}"),
            call.info("- {'device': 'PCI1'}")
        ]
        self.manager.logger.assert_has_calls(expected_calls, any_order=True)

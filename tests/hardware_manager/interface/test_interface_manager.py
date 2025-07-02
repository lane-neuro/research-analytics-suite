import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock, call, Mock
from research_analytics_suite.hardware_manager.interface.InterfaceManager import InterfaceManager


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.fixture
def mock_interfaces(mock_logger):
    with patch('research_analytics_suite.hardware_manager.interface.usb.USB.USB', autospec=True) as MockUSB, \
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
            patch('research_analytics_suite.hardware_manager.interface.display.PCI.PCI', autospec=True) as MockPCI, \
            patch('research_analytics_suite.hardware_manager.interface.serial.Serial.Serial', autospec=True) as MockSerial:
        MockUSB.return_value.detect = Mock(return_value=[{'device': 'USB1'}])
        MockEthernet.return_value.detect = Mock(return_value=[{'device': 'Ethernet1'}])
        MockWireless.return_value.detect = Mock(return_value=[{'device': 'Wireless1'}])
        MockBluetooth.return_value.detect = Mock(return_value=[{'device': 'Bluetooth1'}])
        MockThunderbolt.return_value.detect = Mock(return_value=[{'device': 'Thunderbolt1'}])
        MockDisplayPort.return_value.detect = Mock(return_value=[{'device': 'DisplayPort1'}])
        MockHDMI.return_value.detect = Mock(return_value=[{'device': 'HDMI1'}])
        MockVGA.return_value.detect = Mock(return_value=[{'device': 'VGA1'}])
        MockPCI.return_value.detect = Mock(return_value=[{'device': 'PCI1'}])
        MockSerial.return_value.detect = Mock(return_value=[{'device': 'Serial1'}])

        yield {
            'USB': MockUSB,
            'Ethernet': MockEthernet,
            'Wireless': MockWireless,
            'Bluetooth': MockBluetooth,
            'Thunderbolt': MockThunderbolt,
            'DisplayPort': MockDisplayPort,
            'HDMI': MockHDMI,
            'VGA': MockVGA,
            'PCI': MockPCI,
            'Serial': MockSerial
        }


class TestInterfaceManager:
    @pytest.fixture(autouse=True)
    def setup(self, mock_logger, mock_interfaces):
        self.manager = InterfaceManager()
        self.manager.logger = mock_logger
        self.mock_interfaces = mock_interfaces

        self.manager.base_interfaces = {
            'USB': mock_interfaces['USB'](mock_logger),
            'Ethernet': mock_interfaces['Ethernet'](mock_logger),
            'Wireless': mock_interfaces['Wireless'](mock_logger),
            'Bluetooth': mock_interfaces['Bluetooth'](mock_logger),
            'Thunderbolt': mock_interfaces['Thunderbolt'](mock_logger),
            'DisplayPort': mock_interfaces['DisplayPort'](mock_logger),
            'HDMI': mock_interfaces['HDMI'](mock_logger),
            'VGA': mock_interfaces['VGA'](mock_logger),
            'PCI': mock_interfaces['PCI'](mock_logger),
            'Serial': mock_interfaces['Serial'](mock_logger)
        }

    def test_singleton(self):
        manager1 = InterfaceManager()
        manager2 = InterfaceManager()
        assert manager1 is manager2

    def test_detect_interfaces(self):
        self.manager.detect_interfaces()
        assert self.manager.interfaces == {
            'USB': [{'device': 'USB1'}],
            'Ethernet': [{'device': 'Ethernet1'}],
            'Wireless': [{'device': 'Wireless1'}],
            'Bluetooth': [{'device': 'Bluetooth1'}],
            'Thunderbolt': [{'device': 'Thunderbolt1'}],
            'DisplayPort': [{'device': 'DisplayPort1'}],
            'HDMI': [{'device': 'HDMI1'}],
            'VGA': [{'device': 'VGA1'}],
            'PCI': [{'device': 'PCI1'}],
            'Serial': [{'device': 'Serial1'}]
        }

    def test_add_interface(self):
        mock_new_interface = MagicMock()
        mock_new_interface.detect = Mock(return_value=[{'device': 'NewInterface1'}])
        self.manager.add_interface('NewInterface', mock_new_interface)
        self.manager.detect_interfaces()
        assert self.manager.interfaces['NewInterface'] == [{'device': 'NewInterface1'}]

    def test_remove_interface(self):
        mock_new_interface = MagicMock()
        mock_new_interface.detect = Mock(return_value=[{'device': 'NewInterface1'}])
        self.manager.add_interface('NewInterface', mock_new_interface)
        self.manager.detect_interfaces()
        assert 'NewInterface' in self.manager.interfaces
        self.manager.remove_interface('NewInterface')
        self.manager.detect_interfaces()
        assert 'NewInterface' not in self.manager.interfaces

    def test_list_interfaces(self):
        self.manager.detect_interfaces()
        interfaces_list = self.manager.list_interfaces()
        assert interfaces_list == [
            'USB', 'Ethernet', 'Wireless', 'Bluetooth', 'Thunderbolt',
            'DisplayPort', 'HDMI', 'VGA', 'PCI', 'Serial'
        ]

    def test_get_interface(self):
        self.manager.detect_interfaces()
        usb_interface = self.manager.get_interface('USB')
        assert usb_interface == [{'device': 'USB1'}]

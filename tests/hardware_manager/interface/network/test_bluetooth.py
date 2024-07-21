import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from bleak import BleakClient, BleakScanner
from research_analytics_suite.hardware_manager.interface.network.Bluetooth import Bluetooth


@pytest.fixture
def logger():
    return MagicMock()


@pytest.fixture
@patch('platform.system', return_value='Linux')
def bluetooth_interface(mock_platform_system, logger):
    return Bluetooth(logger)


class TestBluetooth:
    @patch('platform.system', return_value='Linux')
    def test_detect_os_linux(self, mock_platform_system, logger):
        interface = Bluetooth(logger)
        assert interface.os_info == 'linux'

    @patch('platform.system', return_value='Windows')
    def test_detect_os_windows(self, mock_platform_system, logger):
        interface = Bluetooth(logger)
        assert interface.os_info == 'windows'

    @patch('platform.system', return_value='UnsupportedOS')
    def test_detect_os_unsupported(self, mock_platform_system, logger):
        interface = Bluetooth(logger)
        assert interface.os_info == 'unsupported'
        interface.logger.error.assert_called_with('Unsupported OS: UnsupportedOS')

    @pytest.mark.asyncio
    @patch.object(BleakScanner, 'discover', new_callable=AsyncMock)
    async def test_detect_success(self, mock_discover, logger):
        mock_device_1 = MagicMock()
        mock_device_1.address = '00:11:22:33:44:55'
        mock_device_1.name = 'Device 1'

        mock_device_2 = MagicMock()
        mock_device_2.address = '66:77:88:99:AA:BB'
        mock_device_2.name = 'Device 2'

        mock_discover.return_value = [mock_device_1, mock_device_2]

        interface = Bluetooth(logger)
        devices = await interface.detect()

        expected_devices = [
            {'address': '00:11:22:33:44:55', 'name': 'Device 1'},
            {'address': '66:77:88:99:AA:BB', 'name': 'Device 2'}
        ]

        assert devices == expected_devices

    @pytest.mark.asyncio
    @patch.object(BleakClient, 'connect', new_callable=AsyncMock)
    async def test_connect(self, mock_connect, logger):
        interface = Bluetooth(logger)
        client = await interface.connect('00:11:22:33:44:55')
        assert isinstance(client, BleakClient)
        mock_connect.assert_awaited_once()

    @pytest.mark.asyncio
    @patch.object(BleakClient, 'write_gatt_char', new_callable=AsyncMock)
    async def test_send_data(self, mock_write_gatt_char, logger):
        interface = Bluetooth(logger)
        client = AsyncMock(spec=BleakClient)
        await interface.send_data(client, 'characteristic_uuid', 'test data')
        client.write_gatt_char.assert_awaited_once_with('characteristic_uuid', b'test data')

    @pytest.mark.asyncio
    @patch.object(BleakClient, 'read_gatt_char', new_callable=AsyncMock)
    async def test_receive_data(self, mock_read_gatt_char, logger):
        mock_read_gatt_char.return_value = b'test data'
        interface = Bluetooth(logger)
        client = AsyncMock(spec=BleakClient)
        client.read_gatt_char.return_value = mock_read_gatt_char.return_value
        data = await interface.receive_data(client, 'characteristic_uuid')
        assert data == 'test data'
        client.read_gatt_char.assert_awaited_once_with('characteristic_uuid')

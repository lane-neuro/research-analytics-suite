import pytest
from unittest import mock
from research_analytics_suite.data_engine.data_streams.USBInput import USBInput


@pytest.fixture
def mock_serial():
    with mock.patch('serial.Serial') as mock_serial_class:
        yield mock_serial_class


class TestUSBInput:
    @pytest.fixture(autouse=True)
    def setup_method(self, mock_serial):
        self.mock_serial_instance = mock_serial.return_value
        self.mock_serial_instance.in_waiting = False
        self.usb_input = USBInput(port="COM3", baud_rate=9600)

    def test_initialization(self, mock_serial):
        mock_serial.assert_called_once_with("COM3", 9600)
        assert self.usb_input.port == "COM3"
        assert self.usb_input.baud_rate == 9600
        assert self.usb_input.serial_connection == self.mock_serial_instance

    def test_read_data_no_data(self):
        self.mock_serial_instance.in_waiting = False
        assert self.usb_input.read_data() is None

    def test_read_data_with_data(self):
        self.mock_serial_instance.in_waiting = True
        self.mock_serial_instance.readline.return_value = b"test_data\n"
        assert self.usb_input.read_data() == "test_data"

    def test_close(self):
        self.mock_serial_instance.is_open = True
        self.usb_input.close()
        self.mock_serial_instance.close.assert_called_once()

    def test_close_already_closed(self):
        self.mock_serial_instance.is_open = False
        self.usb_input.close()
        self.mock_serial_instance.close.assert_not_called()

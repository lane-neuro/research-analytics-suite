import pytest
from unittest import mock

from research_analytics_suite.data_engine.data_streams import LiveDataHandler
from research_analytics_suite.data_engine.data_streams import BaseInput
from research_analytics_suite.data_engine import UniversalDataEngine
from research_analytics_suite.utils import CustomLogger


class TestLiveDataHandler:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.mock_data_engine = mock.create_autospec(UniversalDataEngine)
        self.mock_logger = mock.create_autospec(CustomLogger)
        self.live_data_handler = LiveDataHandler(self.mock_data_engine)
        self.live_data_handler._logger = self.mock_logger

    def test_add_live_input(self):
        mock_live_input = mock.create_autospec(BaseInput)
        self.live_data_handler.add_live_input(mock_live_input)
        assert mock_live_input in self.live_data_handler.live_inputs

    def test_start_all(self):
        mock_live_input_1 = mock.create_autospec(BaseInput)
        mock_live_input_2 = mock.create_autospec(BaseInput)
        self.live_data_handler.add_live_input(mock_live_input_1)
        self.live_data_handler.add_live_input(mock_live_input_2)

        self.live_data_handler.start_all()
        mock_live_input_1.start.assert_called_once()
        mock_live_input_2.start.assert_called_once()

    def test_stop_all(self):
        mock_live_input_1 = mock.create_autospec(BaseInput)
        mock_live_input_2 = mock.create_autospec(BaseInput)
        self.live_data_handler.add_live_input(mock_live_input_1)
        self.live_data_handler.add_live_input(mock_live_input_2)

        self.live_data_handler.stop_all()
        mock_live_input_1.stop.assert_called_once()
        mock_live_input_2.stop.assert_called_once()

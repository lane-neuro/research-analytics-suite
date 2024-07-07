# test_base_data.py

import pytest

from research_analytics_suite.data_engine import BaseData


class TestBaseData:

    def test_initial_data(self):
        data = 10
        base_data_instance = BaseData(data)
        assert base_data_instance.get_data() == data, "Initial data should be equal to the data provided during initialization."

    def test_get_data(self):
        data = "test"
        base_data_instance = BaseData(data)
        assert base_data_instance.get_data() == data, "get_data method should return the correct data."

    def test_set_data(self):
        initial_data = 20
        new_data = 30
        base_data_instance = BaseData(initial_data)
        base_data_instance.set_data(new_data)
        assert base_data_instance.get_data() == new_data, "set_data method should correctly update the data."

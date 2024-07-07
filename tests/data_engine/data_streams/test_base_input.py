import pytest
from research_analytics_suite.data_engine.data_streams import BaseInput


class TestBaseInput:

    @pytest.fixture
    def base_input(self):
        """Fixture for a BaseInput instance."""
        return BaseInput(source="TestSource")

    def test_initialization(self, base_input):
        """Test initialization of BaseInput."""
        assert base_input.source == "TestSource"

    def test_start_not_implemented(self, base_input):
        """Test that start method raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            base_input.start()

    def test_stop_not_implemented(self, base_input):
        """Test that stop method raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            base_input.stop()

    def test_read_not_implemented(self, base_input):
        """Test that read method raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            base_input.read()

    def test_source_property(self, base_input):
        """Test the source property."""
        assert base_input.source == "TestSource"
        base_input.source = "NewSource"
        assert base_input.source == "NewSource"

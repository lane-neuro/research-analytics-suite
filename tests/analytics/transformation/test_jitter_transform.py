import pytest
from unittest.mock import patch

from research_analytics_suite.analytics.preloaded.transformations import JitterTransform


class TestJitterTransform:

    @pytest.fixture
    def mock_datapoint(self):
        # Mocking a datapoint object with x and y attributes
        class MockDatapoint:
            def __init__(self):
                self.x = 0
                self.y = 0

        return MockDatapoint()

    @pytest.fixture
    def extreme_datapoint(self):
        # Mocking a datapoint object with extreme x and y attributes
        class ExtremeDatapoint:
            def __init__(self):
                self.x = 1e6
                self.y = -1e6

        return ExtremeDatapoint()

    def test_non_numeric_datapoint_x(self):
        # Mocking a datapoint object with a non-numeric x attribute
        class MockDatapoint:
            def __init__(self):
                self.x = "not-a-number"
                self.y = 0

        datapoint = MockDatapoint()
        jt = JitterTransform()

        with pytest.raises(TypeError):
            jt.transform(datapoint)

    def test_non_numeric_datapoint_y(self):
        # Mocking a datapoint object with a non-numeric y attribute
        class MockDatapoint:
            def __init__(self):
                self.x = 0
                self.y = "not-a-number"

        datapoint = MockDatapoint()
        jt = JitterTransform()

        with pytest.raises(TypeError):
            jt.transform(datapoint)

    @patch('numpy.random.uniform')
    def test_transform(self, mock_uniform, mock_datapoint):
        jitter_strength = 0.1
        jt = JitterTransform(jitter_strength)

        # Mocking the np.random.uniform to return a specific sequence of values
        mock_uniform.side_effect = [0.01, 0.02]

        transformed_datapoint = jt.transform(mock_datapoint)

        # Checking if the jitter transformation is applied correctly
        assert mock_datapoint.x == 0.01
        assert mock_datapoint.y == 0.02

    @patch('numpy.random.uniform')
    def test_transform_with_extreme_values(self, mock_uniform, extreme_datapoint):
        jitter_strength = 0.1
        jt = JitterTransform(jitter_strength)

        # Mocking the np.random.uniform to return a specific sequence of values
        mock_uniform.side_effect = [0.01, -0.02]

        transformed_datapoint = jt.transform(extreme_datapoint)

        # Checking if the jitter transformation is applied correctly
        assert extreme_datapoint.x == 1e6 + 0.01
        assert extreme_datapoint.y == -1e6 - 0.02

    @patch('numpy.random.uniform')
    def test_transform_with_zero_jitter_strength(self, mock_uniform, mock_datapoint):
        jitter_strength = 0.0
        jt = JitterTransform(jitter_strength)

        # Mocking the np.random.uniform to return a specific sequence of values
        mock_uniform.side_effect = [0.0, 0.0]

        transformed_datapoint = jt.transform(mock_datapoint)

        # Checking if the jitter transformation is applied correctly
        assert mock_datapoint.x == 0
        assert mock_datapoint.y == 0

    def test_invalid_jitter_strength(self):
        with pytest.raises(ValueError):
            JitterTransform(jitter_strength=-0.1)

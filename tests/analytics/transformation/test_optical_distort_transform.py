import pytest

from research_analytics_suite.analytics.preloaded.transformations import OpticalDistortTransform


class MockCoord:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class MockFrame:
    def __init__(self, coords):
        self.coords = coords


class MockDatapoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class TestOpticalDistortTransform:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_pose_frames = [MockFrame([MockCoord(0, 0), MockCoord(10, 10)])]
        self.mock_datapoint = MockDatapoint(5, 5)
        self.extreme_datapoint = MockDatapoint(1e6, -1e6)
        self.odt = OpticalDistortTransform(self.mock_pose_frames)

    def test_non_numeric_datapoint_x(self):
        datapoint = MockDatapoint("not-a-number", 0)

        with pytest.raises(TypeError):
            self.odt.transform(datapoint)

    def test_non_numeric_datapoint_y(self):
        datapoint = MockDatapoint(0, "not-a-number")

        with pytest.raises(TypeError):
            self.odt.transform(datapoint)

    def test_transform(self):
        transformed_datapoint = self.odt.transform(self.mock_datapoint)

        x = float(self.mock_datapoint.x) - self.odt.x_center
        y = float(self.mock_datapoint.y) - self.odt.y_center
        r2 = x ** 2 + y ** 2
        distortion_factor = 1 + self.odt.k1 * r2
        expected_x = x * distortion_factor + self.odt.x_center
        expected_y = y * distortion_factor + self.odt.y_center

        assert transformed_datapoint.x == pytest.approx(expected_x, rel=1e-5)
        assert transformed_datapoint.y == pytest.approx(expected_y, rel=1e-5)

    def test_transform_with_zero_k1(self):
        odt = OpticalDistortTransform(self.mock_pose_frames, k1=0.0)
        transformed_datapoint = odt.transform(self.mock_datapoint)

        assert transformed_datapoint.x == self.mock_datapoint.x
        assert transformed_datapoint.y == self.mock_datapoint.y

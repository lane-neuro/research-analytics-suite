import pytest
from unittest import mock
from research_analytics_suite.hardware_manager.cpu.CPUDetector import CPUDetector


class TestCPUDetector:
    @pytest.fixture
    def logger(self):
        with mock.patch('research_analytics_suite.utils.CustomLogger') as logger:
            yield logger

    @pytest.fixture
    def cpu_detector(self, logger):
        return CPUDetector(logger)

    def test_initialization(self, cpu_detector, logger):
        assert cpu_detector.logger == logger

    def test_detect_cpus(self, cpu_detector, logger):
        with mock.patch('psutil.cpu_count', side_effect=[4, 8]):
            with mock.patch('platform.machine', return_value='x86_64'):
                result = cpu_detector.detect_cpus()
                expected = [{
                    "physical_cores": 4,
                    "logical_cores": 8,
                    "architecture": 'x86_64'
                }]
                assert result == expected

    def test_detect_cpus_no_physical_cores(self, cpu_detector, logger):
        with mock.patch('psutil.cpu_count', side_effect=[None, 8]):
            with mock.patch('platform.machine', return_value='x86_64'):
                result = cpu_detector.detect_cpus()
                expected = [{
                    "physical_cores": None,
                    "logical_cores": 8,
                    "architecture": 'x86_64'
                }]
                assert result == expected

    def test_detect_cpus_no_logical_cores(self, cpu_detector, logger):
        with mock.patch('psutil.cpu_count', side_effect=[4, None]):
            with mock.patch('platform.machine', return_value='x86_64'):
                result = cpu_detector.detect_cpus()
                expected = [{
                    "physical_cores": 4,
                    "logical_cores": None,
                    "architecture": 'x86_64'
                }]
                assert result == expected

    def test_detect_cpus_exception(self, cpu_detector, logger):
        with mock.patch('psutil.cpu_count', side_effect=Exception("psutil error")):
            with mock.patch('platform.machine', return_value='x86_64'):
                result = cpu_detector.detect_cpus()
                expected = [{
                    "physical_cores": None,
                    "logical_cores": None,
                    "architecture": 'x86_64'
                }]
                assert result == expected
                logger.error.assert_called_with("Error detecting CPUs: psutil error")

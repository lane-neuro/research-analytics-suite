import pytest
from unittest import mock
from research_analytics_suite.hardware_manager.gpu.GPUDetector import GPUDetector


class TestGPUDetector:
    @pytest.fixture
    def logger(self):
        with mock.patch('research_analytics_suite.utils.CustomLogger') as logger:
            yield logger

    @pytest.fixture
    def gpu_detector(self, logger):
        return GPUDetector(logger)

    def test_logger_integration(self, gpu_detector, logger):
        with mock.patch('torch.cuda.is_available', return_value=True):
            with mock.patch('torch.cuda.device_count', return_value=1):
                with mock.patch('torch.cuda.get_device_name', return_value='GPU1'):
                    result = gpu_detector.detect_gpu_torch()
                    assert result == [{'name': 'GPU1', 'index': 0}]
                    logger.info.assert_called_with('Detected GPU using torch: GPU1')

    def test_detect_gpu_torch_no_gpu(self, gpu_detector):
        with mock.patch('torch.cuda.is_available', return_value=False):
            assert gpu_detector.detect_gpu_torch() == []

    def test_detect_gpu_torch_with_gpus(self, gpu_detector):
        with mock.patch('torch.cuda.is_available', return_value=True):
            with mock.patch('torch.cuda.device_count', return_value=2):
                with mock.patch('torch.cuda.get_device_name', side_effect=['GPU1', 'GPU2']):
                    expected = [
                        {'name': 'GPU1', 'index': 0},
                        {'name': 'GPU2', 'index': 1},
                    ]
                    assert gpu_detector.detect_gpu_torch() == expected

    def test_detect_gpu_torch_exception(self, gpu_detector):
        with mock.patch('torch.cuda.is_available', side_effect=Exception('Torch detection error')):
            with mock.patch.object(gpu_detector.logger, 'error') as mock_logger_error:
                result = gpu_detector.detect_gpu_torch()
                assert result == []
                mock_logger_error.assert_called_once_with('Torch detection error')

    def test_detect_gpu_pynvml_no_gpu(self, gpu_detector):
        with mock.patch('pynvml.nvmlInit', return_value=None):
            with mock.patch('pynvml.nvmlDeviceGetCount', return_value=0):
                with mock.patch('pynvml.nvmlShutdown', return_value=None):
                    assert gpu_detector.detect_gpu_pynvml() == []

    def test_detect_gpu_pynvml_with_gpus(self, gpu_detector):
        with mock.patch('pynvml.nvmlInit', return_value=None):
            with mock.patch('pynvml.nvmlDeviceGetCount', return_value=2):
                with mock.patch('pynvml.nvmlDeviceGetHandleByIndex', side_effect=[mock.Mock(), mock.Mock()]):
                    with mock.patch('pynvml.nvmlDeviceGetName', side_effect=[b'GPU1', b'GPU2']):
                        with mock.patch('pynvml.nvmlShutdown', return_value=None):
                            expected = [
                                {'name': 'GPU1', 'index': 0},
                                {'name': 'GPU2', 'index': 1},
                            ]
                            assert gpu_detector.detect_gpu_pynvml() == expected

    def test_detect_gpu_pynvml_exception(self, gpu_detector):
        with mock.patch('pynvml.nvmlInit', side_effect=Exception('pynvml initialization error')):
            with mock.patch.object(gpu_detector.logger, 'error') as mock_logger_error:
                result = gpu_detector.detect_gpu_pynvml()
                assert result == []
                mock_logger_error.assert_called_once_with('pynvml initialization error')

    def test_detect_mps_gpu_available(self, gpu_detector, logger):
        with mock.patch('platform.system', return_value='darwin'):
            with mock.patch('torch.backends.mps.is_available', return_value=True):
                with mock.patch('torch.backends.mps.is_built', return_value=True):
                    expected = [{'name': 'MPS', 'index': 0}]
                    assert gpu_detector.detect_mps_gpu() == expected
                    logger.info.assert_called_with("MPS backend is available.")

    def test_detect_mps_gpu_unavailable(self, gpu_detector, logger):
        with mock.patch('platform.system', return_value='darwin'):
            with mock.patch('torch.backends.mps.is_available', return_value=False):
                with mock.patch('torch.backends.mps.is_built', return_value=False):
                    with mock.patch('platform.mac_ver', return_value=['10.15.7']):
                        with mock.patch('platform.processor', return_value='Intel'):
                            assert gpu_detector.detect_mps_gpu() == []
                            logger.warning.assert_called_with("MPS backend is not available.")
                            logger.info.assert_called_with("macOS version: 10.15.7, Chip: Intel")

    def test_detect_gpus_linux_windows(self, gpu_detector):
        with mock.patch('platform.system', return_value='linux'):
            with mock.patch.object(gpu_detector, 'detect_gpu_torch', return_value=[{'name': 'GPU1', 'index': 0}]):
                with mock.patch.object(gpu_detector, 'detect_gpu_pynvml', return_value=[{'name': 'GPU2', 'index': 1}]):
                    expected = [
                        {'name': 'GPU1', 'index': 0},
                        {'name': 'GPU2', 'index': 1},
                    ]
                    assert gpu_detector.detect_gpus() == expected

    def test_detect_gpus_macos(self, gpu_detector):
        with mock.patch('platform.system', return_value='darwin'):
            # Reinitialize gpu_detector to apply the platform mock
            gpu_detector = GPUDetector(mock.Mock())

            with mock.patch.object(gpu_detector, 'detect_mps_gpu',
                                   return_value=[{'name': 'MPS', 'index': 0}]) as mock_detect_mps_gpu:
                with mock.patch.object(gpu_detector, 'detect_gpu_torch', return_value=[]):
                    with mock.patch.object(gpu_detector, 'detect_gpu_pynvml', return_value=[]):
                        expected = [{'name': 'MPS', 'index': 0}]
                        result = gpu_detector.detect_gpus()
                        print(f"Result from detect_gpus: {result}")
                        assert result == expected
                        mock_detect_mps_gpu.assert_called_once()

    def test_detect_gpus_unsupported_os(self, gpu_detector):
        with mock.patch('platform.system', return_value='unsupported_os'):
            # Reinitialize gpu_detector to apply the platform mock
            gpu_detector = GPUDetector(mock.Mock())

            with mock.patch.object(gpu_detector, 'detect_mps_gpu', return_value=[]):
                with mock.patch.object(gpu_detector, 'detect_gpu_torch', return_value=[]):
                    with mock.patch.object(gpu_detector, 'detect_gpu_pynvml', return_value=[]):
                        expected = []
                        result = gpu_detector.detect_gpus()
                        assert result == expected

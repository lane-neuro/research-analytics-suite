import pytest
from unittest import mock

import torch.backends.mps

from research_analytics_suite.hardware_manager.gpu.GPUManager import GPUManager
from research_analytics_suite.hardware_manager.gpu.GPUDetector import GPUDetector
from research_analytics_suite.hardware_manager.gpu.CUDAManager import CUDAManager

class TestGPUInstaller:
    @pytest.fixture
    def logger(self):
        with mock.patch('research_analytics_suite.utils.CustomLogger') as logger:
            yield logger

    @pytest.fixture
    def remote_manager(self):
        return mock.Mock()

    @pytest.fixture
    def gpu_installer(self, logger, remote_manager):
        return GPUManager(logger, remote_manager)

    def test_initialization(self, gpu_installer, logger, remote_manager):
        assert gpu_installer.logger == logger
        assert gpu_installer.remote_manager == remote_manager
        assert isinstance(gpu_installer.gpu_detector, GPUDetector)
        assert isinstance(gpu_installer.cuda_manager, CUDAManager)

    def test_detect_gpus_no_gpus(self, gpu_installer, logger):
        with mock.patch.object(gpu_installer.gpu_detector, 'detect_gpus', return_value=[]):
            result = gpu_installer.detect_hardware()
            assert result == []
            logger.error.assert_called_with("No GPUs detected.")

    def test_detect_gpus_with_gpus(self, gpu_installer, logger):
        detected_gpus = [{'name': 'GeForce RTX 3070', 'index': 0, 'cuda_version': 'Unknown', 'memory': 'Unknown'}]
        with mock.patch.object(gpu_installer.gpu_detector, 'detect_gpus', return_value=detected_gpus):
            with mock.patch.object(gpu_installer.cuda_manager, 'get_cuda_version', return_value='8.6'):
                with mock.patch.object(gpu_installer.cuda_manager, 'install_cuda') as mock_install_cuda:
                    with mock.patch.object(gpu_installer.cuda_manager, 'verify_installation') as mock_verify_installation:
                        result = gpu_installer.detect_hardware()
                        assert result == detected_gpus
                        # logger.info.assert_any_call("Detected GPU: GeForce RTX 3070, Recommended CUDA Version: 8.6")
                        # mock_install_cuda.assert_called_once_with('8.6')
                        # mock_verify_installation.assert_called_once()

    def test_install_mps_gpu(self, gpu_installer, logger):
        detected_gpus = [{'name': 'MPS', 'index': 0, 'cuda_version': 'Unknown', 'memory': 'Unknown'}]
        with mock.patch.object(gpu_installer.gpu_detector, 'detect_gpus', return_value=detected_gpus):
            with mock.patch('torch.backends.mps.is_available', return_value=True):
                with mock.patch('torch.backends.mps.is_built', return_value=True):
                    result = gpu_installer.detect_hardware()
                    assert result == detected_gpus
                    # logger.info.assert_called_with("Using MPS backend for GPU acceleration on macOS.")

    def test_install_cuda_failure(self, gpu_installer, logger):
        detected_gpus = [{'name': 'GeForce RTX 3070', 'index': 0, 'cuda_version': 'Unknown', 'memory': 'Unknown'}]
        with mock.patch.object(gpu_installer.gpu_detector, 'detect_gpus', return_value=detected_gpus):
            with mock.patch.object(gpu_installer.cuda_manager, 'get_cuda_version', return_value='8.6'):
                with mock.patch.object(gpu_installer.cuda_manager, 'install_cuda', side_effect=Exception("Installation failed")):
                    result = gpu_installer.detect_hardware()
                    assert result == detected_gpus
                    # logger.info.assert_any_call("Detected GPU: GeForce RTX 3070, Recommended CUDA Version: 8.6")
                    # logger.error.assert_called_with("Failed to install CUDA 8.6 for GeForce RTX 3070: Installation failed")

    def test_detect_gpus_with_multiple_gpus(self, gpu_installer, logger):
        detected_gpus = [
            {'name': 'GeForce RTX 3070', 'index': 0, 'cuda_version': 'Unknown', 'memory': 'Unknown'},
            {'name': 'NVIDIA A100', 'index': 1, 'cuda_version': 'Unknown', 'memory': 'Unknown'}
        ]
        with mock.patch.object(gpu_installer.gpu_detector, 'detect_gpus', return_value=detected_gpus):
            with mock.patch.object(gpu_installer.cuda_manager, 'get_cuda_version') as mock_get_cuda_version:
                with mock.patch.object(gpu_installer.cuda_manager, 'install_cuda') as mock_install_cuda:
                    with mock.patch.object(gpu_installer.cuda_manager, 'verify_installation') as mock_verify_installation:
                        mock_get_cuda_version.side_effect = ['8.6', '8.0']
                        result = gpu_installer.detect_hardware()
                        assert result == detected_gpus
                        # logger.info.assert_any_call("Detected GPU: GeForce RTX 3070, Recommended CUDA Version: 8.6")
                        # logger.info.assert_any_call("Detected GPU: NVIDIA A100, Recommended CUDA Version: 8.0")
                        # mock_install_cuda.assert_any_call('8.6')
                        # mock_install_cuda.assert_any_call('8.0')
                        # mock_verify_installation.assert_called()

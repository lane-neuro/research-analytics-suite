import subprocess
import pytest
from unittest import mock
import platform

from research_analytics_suite.hardware_manager.gpu.CUDAManager import CUDAManager


class TestCUDAManager:
    @pytest.fixture
    def logger(self):
        with mock.patch('research_analytics_suite.utils.CustomLogger') as logger:
            yield logger

    @pytest.fixture
    def cuda_manager(self, logger):
        return CUDAManager(logger)

    def test_initialization(self, cuda_manager):
        assert cuda_manager.os_info == platform.system().lower()

    def test_get_cuda_version_known_gpu(self, cuda_manager):
        assert cuda_manager.get_cuda_version("Tesla V100") == "7.0"
        assert cuda_manager.get_cuda_version("GeForce RTX 3070") == "8.6"

    def test_get_cuda_version_unknown_gpu(self, cuda_manager):
        assert cuda_manager.get_cuda_version("Unknown GPU") == "Unknown"

    def test_check_permissions_linux(self, cuda_manager):
        with mock.patch('platform.system', return_value='Linux'):
            try:
                with mock.patch('os.geteuid', return_value=0):
                    cuda_manager = CUDAManager(mock.Mock())
                    assert cuda_manager.check_permissions() is True
            except AttributeError:
                # Handle cases where `geteuid` doesn't exist, such as on Windows
                pass

    @pytest.mark.skipif(platform.system() != 'Windows', reason="Test only applicable to Windows")
    @mock.patch('platform.system', return_value='Windows')
    def test_check_permissions_windows(self, mock_platform):
        with mock.patch('ctypes.windll.shell32.IsUserAnAdmin', return_value=True):
            cuda_manager = CUDAManager(logger=None)  # Replace logger with a mock or real logger as needed
            assert cuda_manager.check_permissions() is True

    # @pytest.mark.skipif(platform.system() != 'Linux', reason="Test only applicable to Linux")
    # def test_install_cuda_supported_gpu_linux(self, logger):
    #     with mock.patch('platform.system', return_value='Linux'):
    #         cuda_manager = CUDAManager(logger)
    #         with mock.patch.object(cuda_manager, 'install_cuda_linux'):
    #             cuda_manager.install_cuda("10.1")
    #             cuda_manager.install_cuda_linux.assert_called_once_with("10.1")

    def test_install_cuda_unsupported_gpu(self, cuda_manager, logger):
        with mock.patch('platform.system', return_value='Linux'):
            cuda_manager = CUDAManager(logger)
            cuda_manager.install_cuda("Unknown")
            logger.error.assert_called_with("Unsupported GPU for automatic CUDA installation.")

    def test_install_cuda_linux(self, cuda_manager, logger):
        with mock.patch('platform.system', return_value='Linux'):
            cuda_manager = CUDAManager(logger)
            with mock.patch('subprocess.run', return_value=mock.Mock()) as run:
                cuda_manager.install_cuda_linux("10.1")
                run.assert_any_call(["wget", "https://developer.download.nvidia.com/compute/cuda/10.1/Prod/local_installers/cuda_10.1_linux.run"], check=True)
                run.assert_any_call(["sudo", "sh", "cuda_10.1_linux.run"], check=True)

    def test_install_cuda_linux_various_versions(self, cuda_manager, logger):
        with mock.patch('platform.system', return_value='Linux'):
            cuda_manager = CUDAManager(logger)
            with mock.patch('subprocess.run', return_value=mock.Mock()) as run:
                versions = ["10.1", "10.2", "11.0", "11.1"]
                for version in versions:
                    cuda_manager.install_cuda_linux(version)
                    run.assert_any_call(["wget", f"https://developer.download.nvidia.com/compute/cuda/{version}/Prod/local_installers/cuda_{version}_linux.run"], check=True)
                    run.assert_any_call(["sudo", "sh", f"cuda_{version}_linux.run"], check=True)

    def test_install_cuda_windows(self, cuda_manager, logger):
        with mock.patch('platform.system', return_value='Windows'):
            cuda_manager = CUDAManager(logger)
            with mock.patch('subprocess.run', return_value=mock.Mock()) as run:
                cuda_manager.install_cuda_windows("10.1")
                run.assert_any_call(["powershell", "Start-Process", "-Wait", "https://developer.download.nvidia.com/compute/cuda/10.1/Prod/network_installers/cuda_10.1_win10.exe"], check=True)

    def test_install_cuda_windows_various_versions(self, cuda_manager, logger):
        with mock.patch('platform.system', return_value='Windows'):
            cuda_manager = CUDAManager(logger)
            with mock.patch('subprocess.run', return_value=mock.Mock()) as run:
                versions = ["10.1", "10.2", "11.0", "11.1"]
                for version in versions:
                    cuda_manager.install_cuda_windows(version)
                    run.assert_any_call(["powershell", "Start-Process", "-Wait", f"https://developer.download.nvidia.com/compute/cuda/{version}/Prod/network_installers/cuda_{version}_win10.exe"], check=True)

    def test_uninstall_cuda_linux(self, cuda_manager, logger):
        with mock.patch('platform.system', return_value='Linux'):
            cuda_manager = CUDAManager(logger)
            with mock.patch('subprocess.run', return_value=mock.Mock()) as run:
                cuda_manager.uninstall_cuda()
                run.assert_called_with(["sudo", "apt-get", "remove", "--purge", "cuda"])

    def test_uninstall_cuda_windows(self, cuda_manager, logger):
        with mock.patch('platform.system', return_value='Windows'):
            cuda_manager = CUDAManager(logger)
            with mock.patch('subprocess.run', return_value=mock.Mock()) as run:
                cuda_manager.uninstall_cuda()
                run.assert_called_with(["powershell", "Get-WmiObject -Class Win32_Product | Where-Object { $_.Name -like 'NVIDIA CUDA*' } | ForEach-Object { $_.Uninstall() }"])

    def test_verify_installation_success(self, cuda_manager, logger):
        with mock.patch('subprocess.run', return_value=mock.Mock(returncode=0, stdout='CUDA version')):
            cuda_manager.verify_installation()
            logger.info.assert_called_with('CUDA version')

    def test_verify_installation_failure(self, cuda_manager, logger):
        with mock.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'nvcc')):
            cuda_manager.verify_installation()
            logger.error.assert_called_with("CUDA installation verification failed.")

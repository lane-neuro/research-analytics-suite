"""
GPUInstaller

This module contains the GPUInstaller class, which manages GPU detection and CUDA installation.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from ..HardwareDetector import HardwareDetector
from .GPUDetector import GPUDetector
from .CUDAManager import CUDAManager


class GPUInstaller(HardwareDetector):
    def detect_hardware(self): ...  # pragma: no cover

    def __init__(self, logger, remote_manager, remote_servers=None):
        super().__init__(logger)
        self.remote_manager = remote_manager
        self.gpu_detector = GPUDetector(logger)
        self.cuda_manager = CUDAManager(logger)
        self.remote_servers = remote_servers or []

    def install(self) -> list[dict]:
        """Detect GPUs and install CUDA if necessary.

        Returns:
            list[dict]: Information about detected GPUs.
        """
        gpu_info = self.gpu_detector.detect_gpus()
        if not gpu_info:
            self.logger.error("No GPUs detected.")
            return []

        for gpu in gpu_info:
            if gpu['name'] == 'MPS':
                self.logger.info("Using MPS backend for GPU acceleration on macOS.")
            else:
                cuda_version = self.cuda_manager.get_cuda_version(gpu['name'])
                self.logger.info(f"Detected GPU: {gpu['name']}, Recommended CUDA Version: {cuda_version}")
                try:
                    self.cuda_manager.install_cuda(cuda_version)
                    self.cuda_manager.verify_installation()
                except Exception as e:
                    self.logger.error(f"Failed to install CUDA {cuda_version} for {gpu['name']}: {e}")

        return gpu_info

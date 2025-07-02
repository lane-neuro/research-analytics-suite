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
from .GPUDetector import GPUDetector
from .CUDAManager import CUDAManager


class GPUManager:

    def __init__(self, logger, remote_manager, remote_servers=None):
        self.logger = logger
        self.remote_manager = remote_manager
        self.gpu_detector = GPUDetector(logger)
        self.cuda_manager = CUDAManager(logger)
        self.remote_servers = remote_servers or []
        self.gpus = []

    def detect_hardware(self) -> list[dict]:
        """Detect GPUs and install CUDA if necessary.

        Returns:
            list[dict]: Information about detected GPUs.
        """
        try:
            gpu_info = self.gpu_detector.detect_gpus()
        except Exception as e:
            self.logger.error(f"Error during GPU detection: {e}")
            return []

        if not gpu_info:
            self.logger.error("No GPUs detected.")
            return []

        for gpu in gpu_info:
            if gpu['name'] == 'MPS':
                self.logger.debug("Using MPS backend for GPU acceleration on macOS.")
                _gpu = {
                    "name": gpu.get('name', 'MPS'),
                    "index": gpu.get('index', 0),
                    "cuda_version": gpu.get('cuda_version', 'Unknonwn'),
                    "memory": gpu.get('memory', 'Unknown'),
                }
                self.gpus.append(_gpu)
            else:
                # cuda_version = self.cuda_manager.get_cuda_version(gpu['name'])
                # self.logger.debug(f"Detected GPU: {gpu['name']}")
                # try:
                #     self.cuda_manager.install_cuda(cuda_version)
                #     self.cuda_manager.verify_installation()
                # except Exception as e:
                #     self.logger.error(f"Failed to install CUDA {cuda_version} for {gpu['name']}: {e}")

                _gpu = {
                    "name": gpu.get('name', 'Unknown GPU'),
                    "index": gpu.get('index', 0),
                    "cuda_version": gpu.get('cuda_version', 'Unknown'),
                    "memory": gpu.get('memory', 'Unknown'),
                }
                self.gpus.append(_gpu)

        return self.gpus

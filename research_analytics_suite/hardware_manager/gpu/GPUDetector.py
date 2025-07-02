"""
GPUDetector

This module contains the GPUDetector class, which detects GPU devices.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import platform
import torch
import pynvml
from typing import List, Dict


class GPUDetector:
    def __init__(self, logger):
        self.logger = logger
        self.os_info = platform.system().lower()

    def detect_gpus(self) -> List[Dict[str, str]]:
        """Detect GPUs using available methods based on the operating system.

        Returns:
            list: Information about detected GPUs.
        """
        if self.os_info == 'darwin':
            result = self.detect_mps_gpu()
            return result
        else:
            result_torch = self.detect_gpu_torch()
            result_pynvml = self.detect_gpu_pynvml()
            return result_torch + result_pynvml

    def detect_gpu_torch(self) -> List[Dict[str, str]]:
        """Detect GPUs using torch.

        Returns:
            list: Information about detected GPUs using torch.
        """
        try:
            gpu_info = []
            if torch.cuda.is_available():
                num_gpus = torch.cuda.device_count()
                for i in range(num_gpus):
                    gpu_name = torch.cuda.get_device_name(i)
                    gpu_info.append({"name": gpu_name, "index": i})
                    # self.logger.info(f'Detected GPU using torch: {gpu_name}')
            return gpu_info
        except Exception as e:
            self.logger.error(str(e))
            return []

    def detect_gpu_pynvml(self) -> List[Dict[str, str]]:
        """Detect GPUs using pynvml.

        Returns:
            list: Information about detected GPUs using pynvml.
        """
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpu_info = []
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                gpu_name = pynvml.nvmlDeviceGetName(handle)
                cuda_version = pynvml.nvmlSystemGetCudaDriverVersion()
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpu_info.append({"name": gpu_name, "index": i, "cuda_version": cuda_version,
                                 "memory": memory_info.total})
                # self.logger.info(f'Detected GPU using pynvml: {gpu_name}')
            pynvml.nvmlShutdown()
            return gpu_info
        except Exception as e:
            self.logger.error(str(e))
            return []

    def detect_mps_gpu(self) -> List[Dict[str, str]]:
        """Check for MPS (Metal Performance Shaders) availability on macOS.

        Returns:
            list: Information about detected MPS GPUs.
        """
        mac_ver = platform.mac_ver()[0]
        chip = platform.processor()
        if torch.backends.mps.is_available() and torch.backends.mps.is_built():
            # self.logger.info("MPS backend is available.")
            return [{"name": "MPS", "index": 0}]
        else:
            self.logger.warning("MPS backend is not available.")
            # self.logger.info(f"macOS version: {mac_ver}, Chip: {chip}")
            return []

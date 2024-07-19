"""
CUDAManager

This module contains the CUDAManager class, which manages the installation and verification of CUDA.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

import os
import subprocess
import ctypes
import platform


class CUDAManager:
    def __init__(self, logger):
        self.logger = logger
        self.cuda_version_map = {
            "NVIDIA H100": "9.0",
            "NVIDIA L40": "8.9",
            "NVIDIA A100": "8.0",
            "NVIDIA A30": "8.0",
            "NVIDIA A10": "8.6",
            "NVIDIA A16": "8.6",
            "NVIDIA A40": "8.6",
            "NVIDIA A100X": "8.0",
            "NVIDIA V100S": "7.0",
            "Tesla V100": "7.0",
            "NVIDIA P100": "6.0",
            "NVIDIA T4": "7.5",
            "Tesla P40": "6.1",
            "Tesla P4": "6.1",
            "Tesla K80": "3.7",
            "Tesla K40": "3.5",
            "Tesla K20": "3.5",
            "Tesla K10": "3.0",
            "Tesla C2075": "2.0",
            "Tesla C2050": "2.0",
            "Tesla C2070": "2.0",
            "Tesla M60": "5.2",
            "Tesla M40": "5.2",
            "Quadro RTX 8000": "7.5",
            "Quadro RTX 6000": "7.5",
            "Quadro RTX 5000": "7.5",
            "Quadro P6000": "6.1",
            "Quadro P5000": "6.1",
            "Quadro P4000": "6.1",
            "Quadro GP100": "6.0",
            "Quadro K6000": "3.5",
            "Quadro K5200": "3.0",
            "Quadro K4200": "3.0",
            "Quadro K2200": "5.0",
            "Quadro K2000D": "3.0",
            "Quadro K2000": "3.0",
            "Quadro K1200": "5.0",
            "Quadro K620": "5.0",
            "Quadro K600": "3.0",
            "Quadro K420": "3.0",
            "GeForce RTX 3090": "8.6",
            "GeForce RTX 3080 Ti": "8.6",
            "GeForce RTX 3080": "8.6",
            "GeForce RTX 3070 Ti": "8.6",
            "GeForce RTX 3070": "8.6",
            "GeForce RTX 3060 Ti": "8.6",
            "GeForce RTX 3060": "8.6",
            "GeForce RTX 2080 Ti": "7.5",
            "GeForce RTX 2080 SUPER": "7.5",
            "GeForce RTX 2080": "7.5",
            "GeForce RTX 2070 SUPER": "7.5",
            "GeForce RTX 2070": "7.5",
            "GeForce RTX 2060 SUPER": "7.5",
            "GeForce RTX 2060": "7.5",
            "GeForce GTX 1660 Ti": "7.5",
            "GeForce GTX 1660 SUPER": "7.5",
            "GeForce GTX 1660": "7.5",
            "GeForce GTX 1080 Ti": "6.1",
            "GeForce GTX 1080": "6.1",
            "GeForce GTX 1070 Ti": "6.1",
            "GeForce GTX 1070": "6.1",
            "GeForce GTX 1060 6GB": "6.1",
            "GeForce GTX 1060 3GB": "6.1",
            "GeForce GTX 1050 Ti": "6.1",
            "GeForce GTX 1050": "6.1",
            "GeForce GTX TITAN Xp": "6.1",
            "GeForce GTX TITAN X": "6.1",
            "GeForce GTX TITAN Z": "3.5",
            "GeForce GTX TITAN Black": "3.5",
            "GeForce GTX TITAN": "3.5",
            "NVIDIA L4": "8.9",
            "NVIDIA A2": "8.6",
            "Quadro M6000 24GB": "5.2",
            "Quadro M6000": "5.2",
            "Quadro M5000": "5.2",
            "Quadro M4000": "5.2",
            "Quadro M2000": "5.2",
            "GeForce RTX 4090": "8.9",
            "GeForce RTX 4080": "8.9",
            "GeForce RTX 4070 Ti": "8.9",
            "GeForce RTX 4060 Ti": "8.9",
            "NVIDIA TITAN V": "7.0"
        }
        self.os_info = platform.system().lower()

    def get_cuda_version(self, gpu_name: str) -> str:
        """Get the recommended CUDA version for a given GPU name.

        Args:
            gpu_name (str): The name of the GPU.

        Returns:
            str: The recommended CUDA version.
        """
        return self.cuda_version_map.get(gpu_name, "Unknown")

    def check_permissions(self) -> bool:
        """Check if the script has administrative permissions.

        Returns:
            bool: True if the script has administrative permissions, False otherwise.
        """
        if self.os_info in ["linux", "darwin"]:
            return os.geteuid() == 0
        elif self.os_info == "windows":
            try:
                is_admin = os.getuid() == 0
            except AttributeError:
                is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            return is_admin
        else:
            return False

    def install_cuda(self, cuda_version: str):
        """Download and install CUDA for the detected OS.

        Args:
            cuda_version (str): The CUDA version to install.
        """
        if cuda_version == "Unknown":
            self.logger.error("Unsupported GPU for automatic CUDA installation.")
            return

        self.logger.info(f"Installing CUDA {cuda_version} for {self.os_info}...")
        if self.os_info == "linux":
            self.install_cuda_linux(cuda_version)
        elif self.os_info == "darwin":
            self.logger.warning("CUDA installation on MacOS is not officially supported by NVIDIA.")
        elif self.os_info == "windows":
            self.install_cuda_windows(cuda_version)
        else:
            self.logger.error("Unsupported operating system.")

    def install_cuda_linux(self, cuda_version: str):
        """Install CUDA on Linux.

        Args:
            cuda_version (str): The CUDA version to install.
        """
        try:
            cuda_url = (f"https://developer.download.nvidia.com/compute/cuda/{cuda_version}"
                        f"/Prod/local_installers/cuda_{cuda_version}_linux.run")
            subprocess.run(["wget", cuda_url], check=True)
            subprocess.run(["sudo", "sh", f"cuda_{cuda_version}_linux.run"], check=True)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install CUDA {cuda_version} on Linux: {e}")

    def install_cuda_windows(self, cuda_version: str):
        """Install CUDA on Windows.

        Args:
            cuda_version (str): The CUDA version to install.
        """
        try:
            cuda_url = (f"https://developer.download.nvidia.com/compute/cuda/{cuda_version}"
                        f"/Prod/network_installers/cuda_{cuda_version}_win10.exe")
            subprocess.run(["powershell", "Start-Process", "-Wait", cuda_url], check=True)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install CUDA {cuda_version} on Windows: {e}")

    def uninstall_cuda(self):
        """Uninstall CUDA from the system."""
        self.logger.info("Uninstalling CUDA...")
        if self.os_info.lower() == "linux":
            subprocess.run(["sudo", "apt-get", "remove", "--purge", "cuda"])
        elif self.os_info.lower() == "windows":
            subprocess.run(["powershell", "Get-WmiObject -Class Win32_Product | Where-Object { $_.Name -like 'NVIDIA "
                                          "CUDA*' } | ForEach-Object { $_.Uninstall() }"])
        else:
            self.logger.error("Unsupported operating system for CUDA uninstallation.")

    def verify_installation(self):
        """Verify the installation of CUDA."""
        try:
            result = subprocess.run(["nvcc", "--version"], capture_output=True, text=True, check=True)
            self.logger.info("CUDA installation verified.")
            self.logger.info(result.stdout)
        except subprocess.CalledProcessError:
            self.logger.error("CUDA installation verification failed.")

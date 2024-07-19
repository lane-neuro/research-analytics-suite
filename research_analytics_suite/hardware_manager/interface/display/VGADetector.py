"""
VGADetector

This module contains the VGADetector class, which detects VGA connections.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import subprocess


class VGADetector:
    def __init__(self, logger):
        self.logger = logger

    def detect_vga(self):
        """Detect VGA connections.

        Returns:
            list: Information about detected VGA connections.
        """
        self.logger.info("Detecting VGA connections...")
        try:
            result = subprocess.run(['lspci | grep VGA'], capture_output=True, text=True, shell=True, check=True)
            vga_connections = result.stdout.split('\n')
            self.logger.info(f"Detected VGA connections: {vga_connections}")
            return vga_connections
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect VGA connections: {e}")
            return []

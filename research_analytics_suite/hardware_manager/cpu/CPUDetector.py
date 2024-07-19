"""
CPUDetector

This module contains the CPUDetector class, which detects CPU devices.

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
import psutil
from typing import List, Dict


class CPUDetector:
    def __init__(self, logger):
        self.logger = logger

    def detect_cpus(self) -> List[Dict[str, str]]:
        """Detect CPUs using psutil.

        Returns:
            list: Information about detected CPUs.
        """
        cpu_info = []
        try:
            physical_cores = psutil.cpu_count(logical=False)
            logical_cores = psutil.cpu_count(logical=True)
        except Exception as e:
            self.logger.error(f"Error detecting CPUs: {e}")
            physical_cores = None
            logical_cores = None

        cpu_info.append({
            "physical_cores": physical_cores,
            "logical_cores": logical_cores,
            "architecture": platform.machine()
        })
        return cpu_info

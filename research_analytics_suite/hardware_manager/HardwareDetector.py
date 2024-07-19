"""
Hardware Detector

This module contains the HardwareDetector class, an abstract base class for detecting hardware components.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from abc import ABC, abstractmethod


class HardwareDetector(ABC):
    def __init__(self, logger):
        self.logger = logger

    @abstractmethod
    def detect_hardware(self):
        """Abstract method to detect hardware components."""
        pass

"""
HDMIDetector

This module contains the HDMIDetector class, which detects HDMI connections.

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


class HDMIDetector:
    def __init__(self, logger):
        self.logger = logger

    def detect_hdmi(self):
        """Detect HDMI connections.

        Returns:
            list: Information about detected HDMI connections.
        """
        self.logger.info("Detecting HDMI connections...")
        try:
            result = subprocess.run(['xrandr | grep " connected"'],
                                    capture_output=True, text=True, shell=True, check=True)
            hdmi_connections = [line for line in result.stdout.split('\n') if 'HDMI' in line]
            self.logger.info(f"Detected HDMI connections: {hdmi_connections}")
            return hdmi_connections
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect HDMI connections: {e}")
            return []

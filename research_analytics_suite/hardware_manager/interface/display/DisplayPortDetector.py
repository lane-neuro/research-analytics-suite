"""
DisplayPortDetector

This module contains the DisplayPortDetector class, which detects DisplayPort connections.

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


class DisplayPortDetector:
    def __init__(self, logger):
        self.logger = logger

    def detect_displayport(self):
        """Detect DisplayPort connections.

        Returns:
            list: Information about detected DisplayPort connections.
        """
        self.logger.info("Detecting DisplayPort connections...")
        try:
            result = subprocess.run(['xrandr | grep " connected"'],
                                    capture_output=True, text=True, shell=True, check=True)
            displayport_connections = [line for line in result.stdout.split('\n') if 'DisplayPort' in line]
            self.logger.info(f"Detected DisplayPort connections: {displayport_connections}")
            return displayport_connections
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect DisplayPort connections: {e}")
            return []

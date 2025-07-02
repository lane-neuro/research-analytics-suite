"""
BatteryInfo

This module contains the BatteryInfo class, which gathers information about the system's battery (if available).

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import psutil


class BatteryInfo:
    def __init__(self, logger):
        self.logger = logger

    def get_battery_info(self):
        """Get battery information.

        Returns:
            dict: Information about the system's battery.
        """
        battery = psutil.sensors_battery()
        if battery:
            battery_info = {
                "percent": battery.percent,
                "secsleft": battery.secsleft,
                "power_plugged": battery.power_plugged
            }
        else:
            battery_info = "No battery detected"
        return battery_info

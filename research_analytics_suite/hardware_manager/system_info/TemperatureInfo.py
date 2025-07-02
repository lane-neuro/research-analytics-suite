"""
TemperatureInfo

This module contains the TemperatureInfo class, which gathers information about the system's component temperatures.

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


class TemperatureInfo:
    def __init__(self, logger):
        self.logger = logger

    def get_temperature_info(self):
        """Get temperature information.

        Returns:
            dict: Information about the system's component temperatures.
        """
        if not hasattr(psutil, "sensors_temperatures"):
            return {}

        temps = psutil.sensors_temperatures()
        temperature_info = {sensor: temps[sensor] for sensor in temps if temps[sensor]}
        return temperature_info

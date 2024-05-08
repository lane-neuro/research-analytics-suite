"""
A module for the resource_monitor function, which monitors the usage of CPU and memory.

This function continuously checks the usage of CPU and memory. If the usage of either resource
exceeds the specified thresholds, an error is handled by the ErrorHandler.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype

This file is part of Neurobehavioral Analytics Suite project. For more information,
please refer to the project documentation: https://github.com/lane-neuro/neurobehavioral_analytics_suite
"""

import asyncio
import psutil
from ErrorHandler import ErrorHandler


async def resource_monitor(cpu_threshold=90, memory_threshold=90):
    """
    Monitors the usage of CPU and memory.

    If the usage of CPU or memory exceeds the specified thresholds, an error is handled by the ErrorHandler.

    Args:
        cpu_threshold (int): The CPU usage threshold.
        memory_threshold (int): The memory usage threshold.
    """
    error_handler = ErrorHandler()

    while True:
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent

        if cpu_usage > cpu_threshold:
            error_handler.handle_error(Exception(f"CPU usage has exceeded {cpu_threshold}%: current usage is {cpu_usage}%"), "resource_monitor")

        if memory_usage > memory_threshold:
            error_handler.handle_error(Exception(f"Memory usage has exceeded {memory_threshold}%: current usage is {memory_usage}%"), "resource_monitor")

        await asyncio.sleep(1)  # sleep for 1 second before checking again

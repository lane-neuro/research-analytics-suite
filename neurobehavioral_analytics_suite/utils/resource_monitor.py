"""
This module contains the `resource_monitor` function, which continuously monitors the usage of CPU and memory.

The `resource_monitor` function checks the usage of CPU and memory at regular intervals. If the usage of either
resource exceeds the specified thresholds, an error is handled by the `ErrorHandler`.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype

This file is part of the Neurobehavioral Analytics Suite project. For more information,
please refer to the project documentation: https://github.com/lane-neuro/neurobehavioral_analytics_suite
"""

import asyncio
import psutil
from ErrorHandler import ErrorHandler


async def resource_monitor(error_handler: ErrorHandler, cpu_threshold=90, memory_threshold=90):
    """
    Asynchronously monitors the usage of CPU and memory.

    This function runs indefinitely, checking the usage of CPU and memory every 500 milliseconds. If the usage of
    either resource exceeds the specified thresholds, an error is handled by the `ErrorHandler`.

    Args:
        error_handler (ErrorHandler): An instance of `ErrorHandler` to handle any exceptions that occur.
        cpu_threshold (int, optional): The CPU usage threshold. Defaults to 90.
        memory_threshold (int, optional): The memory usage threshold. Defaults to 90.
    """

    while True:
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent

        # If CPU usage exceeds the threshold, handle the error
        if cpu_usage > cpu_threshold:
            error_handler.handle_error(Exception(f"CPU usage has exceeded {cpu_threshold}%: "
                                                 f"current usage is {cpu_usage}%"), "resource_monitor")

        # If memory usage exceeds the threshold, handle the error
        if memory_usage > memory_threshold:
            error_handler.handle_error(Exception(f"Memory usage has exceeded {memory_threshold}%: "
                                                 f"current usage is {memory_usage}%"), "resource_monitor")

        # Sleep for 500 milliseconds before checking again
        await asyncio.sleep(.5)
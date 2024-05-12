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

from neurobehavioral_analytics_suite.operation_handler.Operation import Operation
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler


class ResourceMonitorOperation(Operation):
    def __init__(self, error_handler: ErrorHandler, cpu_threshold=90, memory_threshold=90):
        """
        
    
        Args:
            error_handler (ErrorHandler): An instance of `ErrorHandler` to handle any exceptions that occur.
            cpu_threshold (int, optional): The CPU usage threshold. Defaults to 90.
            memory_threshold (int, optional): The memory usage threshold. Defaults to 90.
        """
        operation = Operation(self, error_handler)
        super().__init__(operation, error_handler)

        self.error_handler = error_handler
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold

    async def start(self):
        """
        Asynchronously monitors the usage of CPU and memory.

        This function runs indefinitely, checking the usage of CPU and memory every 500 milliseconds. If the usage of
        either resource exceeds the specified thresholds, an error is handled by the `ErrorHandler`.
        """

        while True:
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent

            print(f"CPU Usage: {cpu_usage}%" + f"\nMemory Usage: {memory_usage}%")

            # If CPU usage exceeds the threshold, handle the error
            if cpu_usage > self.cpu_threshold:
                self.error_handler.handle_error(Exception(f"CPU usage has exceeded {self.cpu_threshold}%: "
                                                          f"current usage is {cpu_usage}%"), "resource_monitor")

            # If memory usage exceeds the threshold, handle the error
            if memory_usage > self.memory_threshold:
                self.error_handler.handle_error(Exception(f"Memory usage has exceeded {self.memory_threshold}%: "
                                                          f"current usage is {memory_usage}%"), "resource_monitor")

            # Sleep for 500 milliseconds before checking again
            await asyncio.sleep(.5)

    def status(self):
        """
        Returns the status of the operation.

        Returns:
            str: The status of the operation.
        """
        return "ResourceMonitorOperation - Running"

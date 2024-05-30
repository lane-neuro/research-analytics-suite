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

from neurobehavioral_analytics_suite.operation_manager.operation.Operation import Operation
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler


class ResourceMonitorOperation(Operation):

    def __init__(self, error_handler: ErrorHandler, cpu_threshold=90, memory_threshold=95):
        """
        
    
        Args:
            error_handler (ErrorHandler): An instance of `ErrorHandler` to handle any exceptions that occur.
            cpu_threshold (int, optional): The CPU usage threshold. Defaults to 90.
            memory_threshold (int, optional): The memory usage threshold. Defaults to 90.
        """
        super().__init__(name="ResourceMonitorOperation", error_handler=error_handler, persistent=True)
        self.cpu_usage = 0
        self.cpu_threshold = cpu_threshold
        self.memory_usage = 0
        self.memory_threshold = memory_threshold
        self.persistent = True
        self.error_handler = error_handler
        self.task = None
        self.name = "ResourceMonitorOperation"
        self._status = "idle"

    async def execute(self) -> None:
        """
        Asynchronously monitors the usage of CPU and memory.
        """

        self._status = "running"

        while True:
            self.cpu_usage = psutil.cpu_percent()
            self.memory_usage = psutil.virtual_memory().percent

            # print(f"CPU Usage: {cpu_usage}%" + f"\nMemory Usage: {memory_usage}%")

            if self.cpu_usage > self.cpu_threshold:
                self.error_handler.handle_error(Exception(f"CPU usage has exceeded {self.cpu_threshold}%: "
                                                          f"current usage is {self.cpu_usage}%"), "resource_monitor")

            if self.memory_usage > self.memory_threshold:
                self.error_handler.handle_error(Exception(f"Memory usage has exceeded {self.memory_threshold}%: "
                                                          f"current usage is {self.memory_usage}%"), "resource_monitor")

            await asyncio.sleep(.5)

    def progress(self) -> str:
        if self.task:
            return "ResourceMonitorOperation - Running"
        else:
            return "ResourceMonitorOperation - Not Running"

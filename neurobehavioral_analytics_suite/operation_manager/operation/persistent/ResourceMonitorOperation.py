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
import cProfile
import os
import sys

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
        super().__init__(name="ResourceMonitorOperation", error_handler=error_handler, persistent=True,
                         func=self.execute)
        self.cpu_usage = 0
        self.cpu_threshold = cpu_threshold
        self.total_memory_usage = 0
        self.process_memory_usage = 0
        self.memory_threshold = memory_threshold
        self.persistent = True
        self.error_handler = error_handler
        self.task = None
        self.name = "ResourceMonitorOperation"
        self._status = "idle"
        self.type = type(self)

        self.process = psutil.Process(os.getpid())
        self.profiler = cProfile.Profile()
        self.profiler.enable()

    async def execute(self) -> None:
        """
        Asynchronously monitors the usage of CPU and memory.
        """

        self._status = "running"

        while True:
            self.cpu_usage = self.process.cpu_percent() / psutil.cpu_count()
            self.total_memory_usage = psutil.virtual_memory().percent
            self.process_memory_usage = self.process.memory_info().rss / (1024 ** 3)  # Corrected to output in GB
            if self.cpu_usage > self.cpu_threshold:
                self.error_handler.handle_error(Exception(f"CPU usage has exceeded {self.cpu_threshold}%: "
                                                          f"current usage is {self.cpu_usage}%"), "resource_monitor")

            if self.total_memory_usage > self.memory_threshold:
                self.error_handler.handle_error(Exception(f"Memory usage has exceeded {self.memory_threshold}%: "
                                                          f"current usage is {self.total_memory_usage}%"),
                                                "resource_monitor")

            await asyncio.sleep(.05)

    def progress(self) -> str:
        if self.task:
            return "ResourceMonitorOperation - Running"
        else:
            return "ResourceMonitorOperation - Not Running"

    def print_memory_usage(self):
        self.profiler.print_stats('calls')
        print(f"CPU Usage: {self.cpu_usage}% across {psutil.cpu_count()} cores")
        print(f"Total Memory Usage: {self.total_memory_usage}% -- Process: {round(self.process.memory_percent(),3)}% ({round(self.process_memory_usage, 3)} GB / "
              f"{round(psutil.virtual_memory().total / (1024 ** 3), 3)} GB)")

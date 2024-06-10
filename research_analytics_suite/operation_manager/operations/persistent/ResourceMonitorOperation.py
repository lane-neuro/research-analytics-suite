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
please refer to the project documentation: https://github.com/lane-neuro/research_analytics_suite
"""

import asyncio
import cProfile
import os
from typing import List

import psutil

from research_analytics_suite.operation_manager.operations.ABCOperation import ABCOperation


class ResourceMonitorOperation(ABCOperation):

    def __init__(self, *args, **kwargs):
        """
        Initializes the `ResourceMonitorOperation` with the specified error handler and thresholds for
        CPU and memory usage
    
        Args:
            cpu_threshold (int, optional): The CPU usage threshold. Defaults to 90.
            memory_threshold (int, optional): The memory usage threshold. Defaults to 90.
        """
        self.cpu_threshold = kwargs.pop("cpu_threshold", 90)
        self.memory_threshold = kwargs.pop("memory_threshold", 95)

        super().__init__(*args, **kwargs, name="ResourceMonitorOperation", func=self.execute)

        self.cpu_usage = 0
        self.total_memory_usage = 0
        self.process_memory_usage = 0

        self.process = psutil.Process(os.getpid())
        self.profiler = cProfile.Profile()
        self.profiler.enable()

    async def execute(self) -> None:
        """
        Asynchronously monitors the usage of CPU and memory.
        """

        self._status = "running"
        self.add_log_entry(f"[RUN] {self._name}")

        while True:
            self.cpu_usage = self.process.cpu_percent()
            self.total_memory_usage = psutil.virtual_memory().percent
            self.process_memory_usage = self.process.memory_info().rss / (1024 ** 3)  # Corrected to output in GB
            if (self.cpu_usage / psutil.cpu_count()) > self.cpu_threshold:
                self._handle_error(Exception(f"CPU usage has exceeded {self.cpu_threshold}%: "
                                             f"current usage is {self.cpu_usage}%"))

            if self.total_memory_usage > self.memory_threshold:
                self._handle_error(Exception(f"Memory usage has exceeded {self.memory_threshold}%: "
                                             f"current usage is {self.total_memory_usage}%"))

            await asyncio.sleep(.01)

    def get_cpu_formatted(self) -> str:
        return (f"Total CPU Usage: {round(self.cpu_usage, 3)}% [{psutil.cpu_count()} cores]"
                f"({round(self.cpu_usage / psutil.cpu_count(), 3)}%/core)\n"
                f"RAS: {round(self.process.cpu_percent(), 3)}% "
                f"({round(self.process.cpu_percent() / psutil.cpu_count(), 3)}%/core)")

    def get_memory_formatted(self) -> str:
        return (f"Total Memory Usage: {self.total_memory_usage}%\n"
                f"RAS: {round(self.process.memory_percent(), 3)}% "
                f"({round(self.process_memory_usage, 3)} GB / "
                f"{round(psutil.virtual_memory().total / (1024 ** 3), 3)} GB)")

    def output_memory_usage(self) -> List[str]:
        return [self.profiler.print_stats('calls'),
                self.get_cpu_formatted(),
                self.get_memory_formatted()]

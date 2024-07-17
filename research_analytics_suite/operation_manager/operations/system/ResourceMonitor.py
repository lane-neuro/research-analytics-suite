"""
ResourceMonitor Module

The ResourceMonitor class is designed to monitor the usage of CPU and memory. It provides methods for formatting the
output of CPU and memory usage.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

import asyncio
import cProfile
import os
from typing import List

import psutil

from research_analytics_suite.commands import command, link_class_commands
from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation


@link_class_commands
class ResourceMonitor(BaseOperation):
    name = "sys_ResourceMonitor"
    version = "0.0.1"
    description = "Monitors the usage of CPU and memory."
    category_id = -1
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {}
    parent_operation = None
    inheritance = []
    is_loop = True
    is_cpu_bound = False
    parallel = True

    def __init__(self, *args, **kwargs):
        """
        Initializes the `ResourceMonitor` with the specified error handler and thresholds for
        CPU and memory usage.

        Args:
            cpu_threshold (int, optional): The CPU usage threshold. Defaults to 90.
            memory_threshold (int, optional): The memory usage threshold. Defaults to 90.
        """
        self.process = None
        self.profiler = None

        self.cpu_threshold = kwargs.pop("cpu_threshold", 90)
        self.memory_threshold = kwargs.pop("memory_threshold", 95)

        self.cpu_usage = 0
        self.total_memory_usage = 0
        self.process_memory_usage = 0

        super().__init__(*args, **kwargs)

    async def initialize_operation(self) -> None:
        await super().initialize_operation()
        self.process = psutil.Process(os.getpid())
        self.profiler = cProfile.Profile()
        self.profiler.enable()

        self.is_ready = True

    async def execute(self) -> None:
        """
        Asynchronously monitors the usage of CPU and memory.
        """
        while self.parallel and self.is_loop:
            self.cpu_usage = self.process.cpu_percent()
            self.total_memory_usage = psutil.virtual_memory().percent
            self.process_memory_usage = self.process.memory_info().rss / (1024 ** 3)  # Output in GB

            if (self.cpu_usage / psutil.cpu_count()) > self.cpu_threshold:
                self.handle_error(Exception(f"CPU usage has exceeded {self.cpu_threshold}%: "
                                            f"current usage is {self.cpu_usage}%"))

            if self.total_memory_usage > self.memory_threshold:
                self.handle_error(Exception(f"Memory usage has exceeded {self.memory_threshold}%: "
                                            f"current usage is {self.total_memory_usage}%"))

            await asyncio.sleep(0.001)

    @command
    def get_cpu_formatted(self) -> str:
        return (f"Total CPU Usage:\t{round(self.cpu_usage, 2)}%\t[{psutil.cpu_count()} cores]\n"
                f"RAS:\t{round(self.process.cpu_percent(), 2)}%")

    @command
    def get_memory_formatted(self) -> str:
        return (f"Total Memory Usage:\t{self.total_memory_usage}%\n"
                f"RAS:\t{round(self.process.memory_percent(), 2)}% "
                f"({round(self.process_memory_usage, 2)} GB\t/\t"
                f"{round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB)")

    @command
    def output_memory_usage(self) -> List[str]:
        return [self.profiler.print_stats('calls'),
                self.get_cpu_formatted(),
                self.get_memory_formatted()]

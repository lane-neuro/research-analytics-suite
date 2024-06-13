"""
ResourceMonitorDialog Module.

This module defines the ResourceMonitorDialog class, which is responsible for managing the dialog for monitoring system 
resources within the research analytics suite. It initializes the resource monitor, handles CPU and memory usage 
displays, and updates these displays continuously.

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
from typing import Optional, Any

import dearpygui.dearpygui as dpg

from research_analytics_suite.operation_manager.OperationControl import OperationControl
from research_analytics_suite.operation_manager.operations.ABCOperation import ABCOperation
from research_analytics_suite.operation_manager.operations.persistent.ResourceMonitorOperation import (
    ResourceMonitorOperation)
from research_analytics_suite.utils.CustomLogger import CustomLogger


class ResourceMonitorDialog:
    """A class to manage the dialog for monitoring system resources."""

    SLEEP_DURATION = 0.05
    MAX_DATA_POINTS = 100

    def __init__(self, operation_control: OperationControl, launcher):
        """
        Initializes the ResourceMonitorDialog with the given operation control, launcher, and logger.

        Args:
            operation_control (OperationControl): Control interface for operations.
            launcher: Launcher instance for initiating tasks.
        """
        self.operation_control = operation_control
        self.launcher = launcher
        self._logger = CustomLogger()

        self.resource_monitor_operation = None
        self.update_operation = None

        self.window = dpg.add_child_window(tag="resource_window", parent="bottom_pane")

        with dpg.group(horizontal=True, parent=self.window):
            self.cpu_container = dpg.add_child_window(parent=self.window)
            self.memory_container = dpg.add_child_window(parent=self.window)

        self.memory_text = None
        self.cpu_text = None

        self.setup_cpu_monitor(self.cpu_container)
        self.setup_memory_monitor(self.memory_container)

    async def initialize(self) -> None:
        """Initializes the resource monitor by adding the update operation."""
        while self.resource_monitor_operation is None:
            self.resource_monitor_operation = self.operation_control.queue.get_operation_by_type(
                ResourceMonitorOperation)
            await asyncio.sleep(0.1)  # Sleep for a short time to prevent busy waiting

        self.update_operation = await self.add_update_operation()

    async def add_update_operation(self) -> Optional[Any]:
        """
        Adds an update operation to the operation manager.

        Returns:
            CustomOperation: The created update operations or None if an error occurred.
        """
        try:
            operation = await self.operation_control.operation_manager.add_operation(
                operation_type=ABCOperation, name="gui_ResourceUpdateTask",
                func=self.update_resource_usage, persistent=True, concurrent=True)
            operation.is_ready = True
            return operation
        except Exception as e:
            self._logger.error(e, self)
        return None

    def setup_cpu_monitor(self, parent: int) -> None:
        """
        Sets up the CPU monitor display.

        Args:
            parent (int): The parent GUI element to attach to.
        """
        self.cpu_text = dpg.add_text("CPU Usage: 0%", parent=parent)

    def setup_memory_monitor(self, parent: int) -> None:
        """
        Sets up the memory monitor display.

        Args:
            parent (int): The parent GUI element to attach to.
        """
        self.memory_text = dpg.add_text("Memory Usage: 0%", parent=parent)

    async def update_resource_usage(self) -> None:
        """Continuously updates the resource usage displays."""
        while self.update_operation.concurrent and self.update_operation.persistent:
            await self.update_cpu_usage()
            await self.update_memory_usage()
            await asyncio.sleep(self.SLEEP_DURATION)

    async def update_cpu_usage(self) -> None:
        """Updates the CPU usage display."""
        if self.resource_monitor_operation is None:
            return

        dpg.set_value(self.cpu_text, f"{self.resource_monitor_operation.get_cpu_formatted()}")

    async def update_memory_usage(self) -> None:
        """Updates the memory usage display."""
        if self.resource_monitor_operation is None:
            return

        dpg.set_value(self.memory_text, f"{self.resource_monitor_operation.get_memory_formatted()}")

    def update_layout(self) -> None:
        """Updates the layout of the resource monitor dialog."""
        window_width = dpg.get_item_width(self.window)
        container_width = window_width // 2
        container_height = dpg.get_item_height(self.cpu_container)

        # Configure the size and position of the containers
        dpg.configure_item(self.cpu_container, pos=(0, 20), width=container_width, height=container_height)
        dpg.configure_item(self.memory_container, pos=(container_width, 20), width=container_width,
                           height=container_height)

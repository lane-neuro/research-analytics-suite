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
import dearpygui.dearpygui as dpg

from research_analytics_suite.gui.GUIBase import GUIBase
from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation
from research_analytics_suite.operation_manager.operations.system.ResourceMonitorOperation import (
    ResourceMonitorOperation)


class ResourceMonitorDialog(GUIBase):
    """A class to manage the dialog for monitoring system resources."""

    SLEEP_DURATION = 0.001
    MAX_DATA_POINTS = 100

    def __init__(self, width: int, height: int, parent):
        """
        Initializes the ResourceMonitorDialog with the given operation control, launcher, and logger.

        Args:
            width (int): The width of the dialog.
            height (int): The height of the dialog.
            parent: The parent GUI element to attach to.
        """
        super().__init__(width, height, parent)

        self._resource_monitor_operation = None

        self._cpu_container = None
        self._cpu_text = None

        self._memory_container = None
        self._memory_text = None

    async def initialize_gui(self) -> None:
        """Initializes the resource monitor by adding the update operation."""
        self._update_operation = await self._operation_control.operation_manager.add_operation_with_parameters(
                operation_type=BaseOperation, name="gui_ResourceUpdateTask",
                action=self._update_async, is_loop=True, parallel=True)
        self._update_operation.is_ready = True

    async def _update_async(self) -> None:
        """Continuously updates the resource usage displays."""
        while self._resource_monitor_operation is None:
            self._resource_monitor_operation = self._operation_control.sequencer.get_operation_by_type(
                ResourceMonitorOperation)
            await asyncio.sleep(0.001)

        while True:
            dpg.set_value(value=f"{self._resource_monitor_operation.get_cpu_formatted()}", item="cpu_text")
            dpg.set_value(value=f"{self._resource_monitor_operation.get_memory_formatted()}", item="memory_text")
            await asyncio.sleep(self.SLEEP_DURATION)

    def draw(self) -> None:
        with dpg.group(horizontal=False, parent=self._parent):
            dpg.add_text("CPU Usage: 0%", tag="cpu_text", bullet=True)
            dpg.add_text("Memory Usage: 0%", tag="memory_text", bullet=True)

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        pass

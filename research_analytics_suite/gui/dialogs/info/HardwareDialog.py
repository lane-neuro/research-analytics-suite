"""
HardwareDialog Module

This module defines the HardwareDialog class, which is responsible for managing the hardware configuration dialog in the GUI.

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
from research_analytics_suite.operation_manager.operations.system.UpdateMonitor import UpdateMonitor


class HardwareDialog(GUIBase):
    """
    The HardwareDialog class is responsible for managing the hardware configuration dialog in the GUI.
    It allows users to view and configure hardware settings, including CPU and GPU configurations.
    """

    def __init__(self, width: int, height: int, parent, hardware_manager):
        super().__init__(width, height, parent)

        self._hardware_mgr = hardware_manager

    async def initialize_gui(self) -> None:
        """Initializes the GUI components for the advanced slot view."""
        try:
            self._update_operation = await self._operation_control.operation_manager.create_operation(
                operation_type=UpdateMonitor, name=f"gui_HardwareDialog",
                action=self._update_async)
            self._update_operation.is_ready = True
        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    def draw(self):
        """Display the hardware dialog."""
        _interfaces = self._hardware_mgr.interfaces

        dpg.add_text("Hardware", parent=self._parent)
        dpg.add_separator()

        # RAM & Processor Information
        dpg.add_collapsing_header(label="RAM", tag="memory_header")
        dpg.add_text(f"{self._hardware_mgr.ram_size} GB", tag="ram_total", parent="memory_header")

        # CPU Information
        dpg.add_collapsing_header(label="CPU(s)", tag="cpu_header")
        for cpu in self._hardware_mgr.cpus:
            dpg.add_text(f"{cpu['name']}", parent="cpu_header", bullet=True)
            dpg.add_text(f"Physical Cores: {cpu['physical_cores']}", parent="cpu_header")
            dpg.add_text(f"Logical Cores: {cpu['logical_cores']}", parent="cpu_header")
            dpg.add_text(f"Frequency: {cpu['frequency']} MHz", parent="cpu_header")

        # GPU Information
        dpg.add_collapsing_header(label="GPU(s)", tag="gpu_header")
        for gpu in self._hardware_mgr.gpus:
            dpg.add_text(f"{gpu['name']}", parent="gpu_header", bullet=True)
            dpg.add_text(f"CUDA Version: {gpu.get('cuda_version', 'N/A')}", parent="gpu_header")
            dpg.add_text(f"Memory: {self._hardware_mgr.gpu_size} GB", parent="gpu_header")

        # USB Information
        dpg.add_collapsing_header(label="USB", tag="usb_header")
        for usb in self._hardware_mgr.get_interfaces_by_type("USB"):
            dpg.add_text(f"{usb['friendly_name']}", parent="usb_header", bullet=True)
            dpg.add_text(f"Status: {usb['status']}", parent="usb_header")
            dpg.add_text(f"Type: {usb['class']}", parent="usb_header")

    async def _update_async(self) -> None:
        """Continuously checks for hardware updates and refreshes the GUI."""
        while self._update_operation.is_ready:
            await asyncio.sleep(.1)

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        """Resizes the GUI."""
        self.width = new_width
        self.height = new_height

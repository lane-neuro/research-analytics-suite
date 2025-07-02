"""
AdvancedSlotView Module

This module defines the AdvancedSlotView class, which is responsible for managing the detailed GUI representation of individual slots.
"""
import asyncio

import dearpygui.dearpygui as dpg
from research_analytics_suite.data_engine.memory.MemorySlot import MemorySlot
from research_analytics_suite.gui.GUIBase import GUIBase
from research_analytics_suite.operation_manager.operations.system.UpdateMonitor import UpdateMonitor


class AdvancedSlotView(GUIBase):
    """A class to manage the detailed GUI representation of individual slots."""

    def __init__(self, width: int, height: int, parent, slot: MemorySlot):
        """
        Initializes the AdvancedSlotView with the given slot.

        Args:
            parent (str): The parent GUI element ID.
            slot (MemorySlot): The memory slot to represent.
        """
        super().__init__(width, height, parent)

        from research_analytics_suite.data_engine.memory.MemoryManager import MemoryManager
        self._memory_manager = MemoryManager()

        self._slot = slot
        self._slot_group_tag = f"adv_slot_{slot.memory_id}"

    async def initialize_gui(self) -> None:
        """Initializes the GUI components for the advanced slot view."""
        try:
            self._update_operation = await self._operation_control.operation_manager.create_operation(
                operation_type=UpdateMonitor, name=f"gui_{self._slot_group_tag}",
                action=self._update_async)
            self._update_operation.is_ready = True
        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    def draw(self):
        """Draws the advanced slot view elements."""
        dpg.add_child_window(tag=self._slot_group_tag, parent=self._parent, height=self.height, width=self.width,
                             border=True, horizontal_scrollbar=True)
        dpg.add_text(f"Name: {self._slot.name}", parent=self._slot_group_tag,
                     tag=f"slot_name_{self._slot.memory_id}")
        dpg.add_text(f"Memory ID: {self._slot.memory_id}", parent=self._slot_group_tag,
                     tag=f"slot_id_{self._slot.memory_id}")

        from research_analytics_suite.gui import left_aligned_combo
        left_aligned_combo(label="Pointer", tag=f"gui_pointer_{self._slot.memory_id}", parent=self._slot_group_tag,
                           items=self._memory_manager.get_all_slot_ids(), callback=self.combo_callback,
                            user_data=self._slot.memory_id)

        dpg.add_text(f"Type: {self._slot.data_type}", parent=self._slot_group_tag,
                     tag=f"slot_type_{self._slot.memory_id}")
        dpg.add_text(f"Data: {self._slot.data}", parent=self._slot_group_tag,
                     tag=f"slot_data_{self._slot.memory_id}")

        # Export functionality
        with dpg.group(horizontal=True, parent=self._slot_group_tag):
            dpg.add_button(label="Export as CSV", callback=self.export_csv)
            dpg.add_button(label="Export as JSON", callback=self.export_json)

    async def _update_async(self) -> None:
        """Updates the advanced slot view elements."""
        while not self._update_operation.is_running:
            await asyncio.sleep(.1)

        while True:
            await asyncio.sleep(.01)
            dpg.set_value(item=f"slot_name_{self._slot.memory_id}", value=f"Name: {self._slot.name}")
            dpg.set_value(item=f"slot_id_{self._slot.memory_id}", value=f"Memory ID: {self._slot.memory_id}")
            dpg.set_value(item=f"slot_type_{self._slot.memory_id}", value=f"Type: {self._slot.data_type}")
            dpg.set_value(item=f"slot_data_{self._slot.memory_id}", value=f"Data: {self._slot.data}")

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        """Resizes the GUI."""
        self.width = new_width
        self.height = new_height

    def combo_callback(self, sender, app_data, user_data):
        """Callback function for the combo box."""
        _sender = user_data
        _selected_slot_id = dpg.get_value(sender)
        self._logger.debug(f"Updating slot {_sender} with pointer to slot {_selected_slot_id}")
        _slot = self._memory_manager.get_slot(_sender)
        _slot.pointer = self._memory_manager.get_slot(_selected_slot_id)
        self._logger.debug(f"Slot: {_slot.memory_id}  Pointer: {_slot.pointer}  Data: {_slot.data}")

    def remove(self):
        """Removes the advanced slot view elements from the GUI."""
        if dpg.does_item_exist(self._slot_group_tag):
            dpg.delete_item(self._slot_group_tag)

    def export_csv(self):
        """Callback function for exporting slot data as CSV."""
        self._slot.export_as_csv()


    def export_json(self):
        """Callback function for exporting slot data as JSON."""
        ...

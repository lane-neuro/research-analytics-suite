"""
MemorySlotPreview Module

This module defines the MemorySlotPreview class, which is responsible for managing the GUI representation of individual slots.
"""
import uuid
import dearpygui.dearpygui as dpg
from research_analytics_suite.data_engine.memory.MemorySlot import MemorySlot


class MemorySlotPreview:
    """A class to manage the GUI representation of individual slots."""

    def __init__(self, parent, slot: MemorySlot, width: int, height: int):
        """
        Initializes the MemorySlotPreview with the given slot.

        Args:
            parent (str): The parent GUI element ID.
            slot (MemorySlot): The memory slot to represent.
            width (int): The width of the slot preview.
            height (int): The height of the slot preview.
        """
        self._runtime_id = f"{uuid.uuid4().hex[:6]}"

        self.parent = parent
        self.slot = slot
        self.width = width
        self.height = height

        self.slot_group_tag = f"slot_group_{slot.memory_id}"

    def draw(self):
        """Draws the slot preview elements."""
        with dpg.group(tag=self.slot_group_tag, parent=self.parent, horizontal=True):
            # Slot name
            dpg.add_text(f"Slot: {self.slot.name}", parent=self.slot_group_tag)

            # Key-Value pairs preview
            for key, value in self.slot.data.items():
                dpg.add_text(f"{key}: {value}", parent=self.slot_group_tag)

            # Operation required indicator
            operation_status = "Yes" if self.slot.operation_required else "No"
            dpg.add_text(f"Operation Required: {operation_status}", parent=self.slot_group_tag)

    def update(self, slot: MemorySlot):
        """Updates the slot preview elements."""
        self.slot = slot
        if dpg.does_item_exist(self.slot_group_tag):
            dpg.delete_item(self.slot_group_tag)
        self.draw()

    def remove(self):
        """Removes the slot preview elements from the GUI."""
        if dpg.does_item_exist(self.slot_group_tag):
            dpg.delete_item(self.slot_group_tag)

    @property
    def runtime_id(self) -> str:
        """Get the runtime ID of the slot preview."""
        return self._runtime_id

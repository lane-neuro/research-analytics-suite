"""
AdvancedSlotView: Inspector-style rendering for a single MemorySlot.
"""
import asyncio
import dearpygui.dearpygui as dpg

from research_analytics_suite.data_engine.memory.MemorySlot import MemorySlot
from research_analytics_suite.gui.utils.type_formatting import format_type_for_display
from research_analytics_suite.gui.GUIBase import GUIBase
from research_analytics_suite.operation_manager.operations.system.UpdateMonitor import UpdateMonitor


class AdvancedSlotView(GUIBase):
    def __init__(self, width: int, height: int, parent, slot: MemorySlot, temp_view: bool = False):
        super().__init__(width, height, parent)
        from research_analytics_suite.data_engine.memory.MemoryManager import MemoryManager
        self._memory_manager = MemoryManager()

        self._slot = slot
        self._temp_view = temp_view
        self._root = f"inspector_{slot.memory_id}" + ("_temp" if temp_view else "")

    async def initialize_gui(self) -> None:
        try:
            self._update_operation = await self._operation_control.operation_manager.create_operation(
                operation_type=UpdateMonitor,
                name=f"gui_{self._root}",
                action=self._update_async
            )
            self._update_operation.is_ready = True
        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    def draw(self):
        if dpg.does_item_exist(self._root):
            dpg.delete_item(self._root)

        with dpg.group(tag=self._root, parent=self._parent):
            # Header
            dpg.add_text(f"Slot: {self._slot.name} [{self._slot.memory_id}]",
                         tag=f"{self._root}_title")
            dpg.add_separator()

            # Details
            with dpg.collapsing_header(label="Details", default_open=True):
                dpg.add_text(tag=f"{self._root}_dtype",
                             default_value=f"Type: {format_type_for_display(self._slot.data_type)}")
                dpg.add_text(tag=f"{self._root}_shape", default_value=self._shape_text(self._slot.data))
                dpg.add_text(tag=f"{self._root}_pointer", default_value=self._pointer_text(self._slot))

            # Data (preview + pointer combo)
            with dpg.collapsing_header(label="Data", default_open=True, tag=f"{self._root}_data_header"):
                from research_analytics_suite.gui import left_aligned_combo
                left_aligned_combo(
                    label="Pointer",
                    tag=f"{self._root}_pointer_combo",
                    items=self._memory_manager.format_slot_name_id(),
                    callback=self._on_pointer_changed,
                    user_data=self._slot.memory_id,
                    width=-1,
                    parent=f"{self._root}_data_header"
                )

                # Preview text (lightweight). If you want a table, plug a renderer here.
                dpg.add_text(tag=f"{self._root}_preview", default_value=self._preview_text(self._slot.data_object), wrap=0)
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Edit...", callback=self._open_edit_modal)
                    dpg.add_button(label="Validate", callback=self._validate)
                    dpg.add_button(label="Snapshot", callback=self._snapshot)

            # Export
            with dpg.collapsing_header(label="Backup & Export", default_open=True):
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Export CSV", callback=self._export_csv)
                    dpg.add_button(label="Export JSON", callback=self._export_json)

            # Warnings / provenance placeholders (wire to your engine as needed)
            with dpg.collapsing_header(label="Provenance / Warnings", default_open=False):
                dpg.add_text("Source: (not recorded)")
                dpg.add_text("Hash: (not recorded)")
                dpg.add_text("Warnings: none")

    # ------------------------------- UPDATE LOOP ------------------------------

    async def _update_async(self) -> None:
        while not self._update_operation.is_running:
            await asyncio.sleep(0.1)
        while True:
            await asyncio.sleep(0.25)
            try:
                slot = self._memory_manager.get_slot(self._slot.memory_id)
            except KeyError:
                continue
            self._slot = slot  # keep reference fresh

            if not dpg.does_item_exist(f"{self._root}_title"):
                continue

            dpg.set_value(f"{self._root}_title", f"Slot: {slot.name} [{slot.memory_id}]")
            dpg.set_value(f"{self._root}_dtype", f"Type: {format_type_for_display(slot.data_type)}")
            dpg.set_value(f"{self._root}_shape", self._shape_text(slot.data))
            dpg.set_value(f"{self._root}_pointer", self._pointer_text(slot))
            dpg.set_value(f"{self._root}_preview", self._preview_text(slot.data_object))

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        """Resizes the GUI."""
        self.width = new_width
        self.height = new_height

    # ------------------------------- ACTIONS ----------------------------------

    def _on_pointer_changed(self, sender, app_data, user_data):
        target_slot_id = str(user_data)
        selected = dpg.get_value(sender)
        if not selected:
            return
        # extract id from "name [id]"
        try:
            selected_id = selected.split("[")[-1].split("]")[0]
            slot = self._memory_manager.get_slot(target_slot_id)
            slot.pointer = self._memory_manager.get_slot(selected_id)
            self._logger.debug(f"Pointer set: {slot.memory_id} -> {slot.pointer.memory_id}")
        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    # Edit modal keeps mutations explicit
    def _open_edit_modal(self):
        tag = f"{self._root}_edit_modal"
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)

        with dpg.window(tag=tag, label=f"Edit: {self._slot.name}", modal=True, width=540, height=380):
            dpg.add_text("Edit value (JSON/py-literal):")
            dpg.add_input_text(tag=f"{tag}_input", multiline=True, width=-1, height=250,
                               default_value=self._preview_text(self._slot.data))
            with dpg.group(horizontal=True):
                dpg.add_button(label="Apply",
                               callback=lambda: self._apply_edit(tag))
                dpg.add_button(label="Cancel", callback=lambda: dpg.hide_item(tag))

    def _apply_edit(self, modal_tag):
        try:
            raw = dpg.get_value(f"{modal_tag}_input")
            # NOTE: if you prefer strict JSON, replace with json.loads
            import ast
            new_val = ast.literal_eval(raw)
            slot = self._memory_manager.get_slot(self._slot.memory_id)
            slot.data = new_val
            dpg.hide_item(modal_tag)
        except Exception as e:
            self._logger.error(Exception(f"Edit failed: {e}", self))

    def _validate(self):
        # Hook: wire in schema checks or type checks here
        self._logger.info(f"Validate requested for {self._slot.name}")

    def _snapshot(self):
        # Hook: create immutable copy as new slot with suffix
        try:
            asyncio.create_task(self._snapshot_async())
        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    async def _snapshot_async(self):
        await self._memory_manager.create_slot(
            name=f"{self._slot.name}_snapshot",
            d_type=self._slot.data_type,
            data=self._slot.data
        )
        self._logger.info(f"Snapshot created: {self._slot.name}_snapshot")

    def _export_csv(self):
        try:
            if hasattr(self._slot, "export_as_csv"):
                self._slot.export_as_csv()
            else:
                self._logger.info("CSV export not supported for this slot type.")
        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    def _export_json(self):
        try:
            if hasattr(self._slot, "export_as_json"):
                self._slot.export_as_json()
            else:
                # Generic JSON dump dialog fallback (optional)
                self._logger.info("JSON export not supported for this slot type.")
        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    # ------------------------------- HELPERS ----------------------------------

    @staticmethod
    def _shape_text(data) -> str:
        try:
            import numpy as np
            import pandas as pd
            if hasattr(data, "shape"):
                return f"Shape: {getattr(data, 'shape', None)}"
            if isinstance(data, (list, dict, set)):
                return f"Size: {len(data)}"
            if isinstance(data, (pd.DataFrame, pd.Series, np.ndarray)):
                return f"Shape: {data.shape}"
        except Exception:
            pass
        return "Shape/Size: n/a"

    @staticmethod
    def _preview_text(data) -> str:
        # Keep it cheap—avoid giant dumps
        try:
            import pandas as pd
            if hasattr(data, "head") and isinstance(data, pd.DataFrame):
                return str(data.head(20))
            txt = str(data)
            return txt if len(txt) < 4000 else txt[:4000] + " …"
        except Exception:
            txt = str(data)
            return txt if len(txt) < 4000 else txt[:4000] + " …"

    @staticmethod
    def _pointer_text(slot: MemorySlot) -> str:
        try:
            p = getattr(slot, "pointer", None)
            return f"Pointer: {p.name} [{p.memory_id}]" if p else "Pointer: (none)"
        except Exception:
            return "Pointer: (none)"

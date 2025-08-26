from __future__ import annotations

import asyncio
import os
import ast

import dearpygui.dearpygui as dpg

from research_analytics_suite.gui.GUIBase import GUIBase
from research_analytics_suite.operation_manager.operations.system.UpdateMonitor import UpdateMonitor


class DataManagementDialog(GUIBase):
    """Data Management region: slot list (left) + single inspector (right)."""

    def __init__(self, width: int, height: int, parent):
        super().__init__(width, height, parent)

        from research_analytics_suite.data_engine.memory.MemoryManager import MemoryManager
        from research_analytics_suite.data_engine import Workspace

        self._memory_manager = MemoryManager()
        self._workspace = Workspace()

        self._selected_slot_id = None
        self._last_rendered_slot_id = None
        self._last_slot_count = -1

        self.add_var_dialog_id = None

    # ------------------------------- LIFECYCLE --------------------------------

    async def initialize_gui(self) -> None:
        try:
            self._update_operation = await self._operation_control.operation_manager.create_operation(
                operation_type=UpdateMonitor,
                name="gui_DataManUpdate",
                action=self._update_async
            )
            self._update_operation.is_ready = True
        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    def draw(self) -> None:
        # Toolbar
        with dpg.group(parent=self._parent, horizontal=True):
            dpg.add_button(label="Add Variable", callback=lambda: asyncio.create_task(self.open_add_var_dialog()))
            dpg.add_button(label="Data Import", callback=self.show_data_import)
            # dpg.add_spacer(width=12)
            dpg.add_input_text(tag="dm_search_input", hint="Search slots…", width=260, callback=self._on_search_change)

        # Main split: left list / right inspector
        with dpg.child_window(tag="dm_main_split", parent=self._parent, width=-1, height=-1, border=False):
            with dpg.group(horizontal=True):
                # LEFT: slot list
                dpg.add_child_window(tag="dm_slot_list_panel", width=280, height=-1, border=True)
                # RIGHT: inspector
                dpg.add_child_window(tag="dm_inspector_panel", width=-1, height=-1, border=True)

        # Containers inside the two panels
        with dpg.group(tag="dm_slot_list_group", parent="dm_slot_list_panel", horizontal=False):
            dpg.add_text("Memory Slots")
            dpg.add_separator()
            dpg.add_text(tag="dm_slot_count_text", default_value="–")
            dpg.add_spacer(height=4)
            dpg.add_child_window(tag="dm_slot_list_scroll", width=-1, height=-1, border=False)

        with dpg.group(tag="dm_inspector_group", parent="dm_inspector_panel"):
            dpg.add_text("Inspector")
            dpg.add_separator()
            # dedicated mount for dynamic content
            with dpg.group(tag="dm_inspector_mount"):
                dpg.add_text(tag="dm_inspector_placeholder",
                             default_value="...Select a slot from the list")

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        self.width, self.height = new_width, new_height
        dpg.configure_item("dm_main_split", width=self.width, height=self.height)

    # ------------------------------- UPDATE LOOP ------------------------------

    async def _update_async(self) -> None:
        while not self._update_operation.is_running:
            await asyncio.sleep(0.1)

        while True:
            await asyncio.sleep(0.15)

            slots = self._memory_manager.list_slots()
            slot_count = len(slots)

            # Refresh the left list only if size changed or search changed
            search_q = (dpg.get_value("dm_search_input") or "").strip().lower()
            needs_list_refresh = (slot_count != self._last_slot_count) or getattr(self, "_force_list_refresh", False)
            if needs_list_refresh:
                self._refresh_slot_list(slots, search_q)
                self._last_slot_count = slot_count
                self._force_list_refresh = False

            # Render inspector only when selection changes
            if self._selected_slot_id != self._last_rendered_slot_id:
                self._render_inspector(self._selected_slot_id)
                self._last_rendered_slot_id = self._selected_slot_id

            # Keep the slot count text fresh
            dpg.set_value("dm_slot_count_text", f"{slot_count} slot(s) loaded")

    # ------------------------------- UI HELPERS -------------------------------

    def _on_search_change(self, *_):
        self._force_list_refresh = True  # Trigger a list rerender on next tick

    def _refresh_slot_list(self, slots, search_q: str) -> None:
        """Rebuilds the left slot list window with selectable items + drag handles."""
        if dpg.does_item_exist("dm_slot_list_inner"):
            dpg.delete_item("dm_slot_list_inner")

        with dpg.group(tag="dm_slot_list_inner", parent="dm_slot_list_scroll"):
            groups: dict[str, list] = {"Data": [], "Meta": [], "Path": [], "Other": []}
            for s in slots:
                label = "Other"
                dt = str(s.data_type).lower()
                if "dataframe" in dt or "list" in dt or "ndarray" in dt:
                    label = "Data"
                elif "dict" in dt or "mapping" in dt:
                    label = "Meta"
                elif "path" in s.name.lower() or (isinstance(s.data, str) and os.path.exists(str(s.data))):
                    label = "Path"
                groups[label].append(s)

            for group_name, items in groups.items():
                if not items:
                    continue

                # collapsing group
                with dpg.collapsing_header(label=f"{group_name} ({len(items)})", default_open=True) as hdr_tag:
                    table_tag = f"dm_table_{group_name}"
                    if dpg.does_item_exist(table_tag):
                        dpg.delete_item(table_tag)

                    # 3 columns: drag | selectable label | delete
                    with dpg.table(tag=table_tag,
                                   header_row=False,
                                   policy=dpg.mvTable_SizingStretchProp,
                                   resizable=False,
                                   borders_innerH=True, borders_innerV=False,
                                   borders_outerH=False, borders_outerV=False,
                                   row_background=False):
                        dpg.add_table_column(init_width_or_weight=0.0, width_fixed=True)  # drag
                        dpg.add_table_column(init_width_or_weight=1.0)  # label/selectable
                        dpg.add_table_column(init_width_or_weight=0.0, width_fixed=True)  # delete

                        for s in items:
                            text_name = f"{s.name} [{s.memory_id}]"
                            if search_q and search_q not in text_name.lower():
                                continue

                            with dpg.table_row():
                                # COL 1: drag handle
                                drag_id = f"dm_drag_{s.memory_id}"
                                dpg.add_text(">", tag=drag_id)
                                with dpg.drag_payload(parent=drag_id, drag_data=s.memory_id, payload_type="SLOT_ID"):
                                    dpg.add_text(f"Slot: {s.name}")

                                # COL 2: selectable (exclusive selection behavior preserved)
                                select_tag = f"dm_slot_select_{s.memory_id}"
                                dpg.add_selectable(label=text_name,
                                                   tag=select_tag,
                                                   callback=self._on_select_slot,
                                                   user_data=s.memory_id)
                                if s.memory_id == self._selected_slot_id:
                                    dpg.set_value(select_tag, True)

                                # COL 3: delete x button + tooltip
                                del_btn_tag = f"dm_slot_del_{s.memory_id}"
                                dpg.add_button(label="x",
                                               tag=del_btn_tag,
                                               width=22, height=22,
                                               callback=self._on_click_delete,
                                               user_data=s.memory_id)
                                with dpg.tooltip(del_btn_tag):
                                    dpg.add_text(f"Delete '{s.name}'")

    def _on_select_slot(self, sender, app_data, user_data):
        """Make selection exclusive: unselect previous, force current True."""
        current_id = str(user_data)
        current_tag = sender  # sender is the selectable's tag

        # Unselect the previously selected row (if different)
        prev_id = self._selected_slot_id
        if prev_id and prev_id != current_id:
            prev_tag = f"dm_slot_select_{prev_id}"
            if dpg.does_item_exist(prev_tag):
                dpg.set_value(prev_tag, False)

        # Force current to True (prevents toggling off on second click)
        dpg.set_value(current_tag, True)

        # Update selection model
        self._selected_slot_id = current_id

    def _on_click_delete(self, sender, app_data, user_data):
        """Open a confirmation modal for deleting a slot."""
        slot_id = str(user_data)
        slot = self._memory_manager.get_slot(slot_id)
        name = slot.name if slot else slot_id

        modal_tag = f"dm_del_modal_{slot_id}"
        if dpg.does_item_exist(modal_tag):
            dpg.delete_item(modal_tag)

        with dpg.window(tag=modal_tag, label="Delete Memory Slot?", modal=True, width=420, height=150, no_resize=True,
                        show=True):
            dpg.add_text(f"Are you sure you want to delete '{name}'?")
            dpg.add_text(f"This action cannot be undone.", color=(255, 0, 0))
            dpg.add_separator()
            with dpg.group(horizontal=True):
                dpg.add_button(label="Delete",
                               callback=lambda: asyncio.create_task(self._delete_slot(slot_id, modal_tag)))
                dpg.add_button(label="Cancel", callback=lambda: dpg.hide_item(modal_tag))

    async def _delete_slot(self, slot_id: str, modal_tag: str):
        """Delete the slot, clear selection if needed, refresh UI."""
        try:
            # If this slot is selected, clear selection + inspector
            if self._selected_slot_id == slot_id:
                self._selected_slot_id = None
                self._last_rendered_slot_id = None  # force inspector refresh

            await self._memory_manager.delete_slot(slot_id)

            # Close modal and refresh list
            if dpg.does_item_exist(modal_tag):
                dpg.hide_item(modal_tag)

            self._force_list_refresh = True

            # Optional: show placeholder immediately (next tick will re-render anyway)
            if dpg.does_item_exist("dm_inspector_placeholder"):
                dpg.set_value("dm_inspector_placeholder", "...Select a slot from the list")
                dpg.configure_item("dm_inspector_placeholder", show=True)

        except Exception as e:
            self._logger.error(Exception(f"Failed to delete slot '{slot_id}': {e}", self))

    def _render_inspector(self, slot_id: str | None) -> None:
        """Clears inspector mount and installs the selected slot view."""
        # Clear mount except the placeholder
        children = dpg.get_item_children("dm_inspector_mount", 1) or []
        for ch in children:
            alias = dpg.get_item_alias(ch)  # convert id -> alias
            if alias != "dm_inspector_placeholder":
                dpg.delete_item(ch)

        # If nothing selected, just show placeholder
        if not slot_id:
            if dpg.does_item_exist("dm_inspector_placeholder"):
                dpg.configure_item("dm_inspector_placeholder", show=True)
            return

        slot = self._memory_manager.get_slot(slot_id)
        if not slot:
            if dpg.does_item_exist("dm_inspector_placeholder"):
                dpg.set_value("dm_inspector_placeholder", "Slot not found.")
                dpg.configure_item("dm_inspector_placeholder", show=True)
            return

        # hide placeholder and mount the inspector view
        if dpg.does_item_exist("dm_inspector_placeholder"):
            dpg.configure_item("dm_inspector_placeholder", show=False)

        from research_analytics_suite.gui.modules.AdvancedSlotView import AdvancedSlotView
        view = AdvancedSlotView(width=-1, height=-1, parent="dm_inspector_mount", slot=slot, temp_view=True)
        asyncio.create_task(view.initialize_gui())
        view.draw()

    # ------------------------------- ACTIONS ----------------------------------

    def show_data_import(self, sender, app_data, user_data):
        if dpg.does_item_exist("selected_file"):
            dpg.delete_item("selected_file")

        with dpg.file_dialog(show=True,
                             default_path=f"{os.path.expanduser('~')}\\Research-Analytics-Suite\\workspaces\\"
                                          f"{self._config.WORKSPACE_NAME}\\data",
                             callback=self._import_data,
                             tag="selected_file",
                             width=500, height=500, modal=True):
            for ext in (".csv", ".json", ".xlsx", ".txt", ".tsv", ".xml", ".hd5"):
                dpg.add_file_extension(ext, color=(255, 255, 255, 255))

    def _import_data(self, sender, app_data, user_data):
        selections = list(app_data.get("selections", {}).values())
        if not selections:
            return

        async def _do():
            for file in selections:
                file_path = os.path.normpath(file)
                data, d_type = self._workspace.get_default_data_engine().load_data(file_path)
                if data is not None:
                    name = os.path.basename(file_path)
                    await self.add_variable(name=name, d_type=d_type, value=data)
        asyncio.run(_do())

    async def add_variable(self, name, d_type, value) -> None:
        try:
            _slot_id, _, _ = await self._memory_manager.create_slot(name=name, d_type=d_type, data=value)
            self._selected_slot_id = _slot_id
            self._force_list_refresh = True
        except Exception as e:
            self._logger.error(Exception(f"Failed to add variable '{name}': {e}", self))

    async def open_add_var_dialog(self) -> None:
        if dpg.does_item_exist(self.add_var_dialog_id):
            dpg.delete_item(self.add_var_dialog_id)

        self.add_var_dialog_id = dpg.generate_uuid()
        with dpg.window(label="Add Memory Slot", modal=True, tag=self.add_var_dialog_id, width=420):
            dpg.add_input_text(label="Name", tag="var_name_input")
            dpg.add_combo(label="Data Type", tag="var_data_type_input",
                          items=["int", "float", "str", "list", "dict", "set", "bool"],
                          callback=self.update_var_value_input)
            dpg.add_input_text(label="Value", tag="var_value_input", hint="e.g., 42, 3.14, 'abc', [1,2], {'a':1}")
            with dpg.group(horizontal=True):
                dpg.add_button(label="Add", callback=lambda: asyncio.create_task(self.add_user_variable_from_dialog()))
                dpg.add_button(label="Cancel", callback=lambda: dpg.hide_item(self.add_var_dialog_id))

    def update_var_value_input(self, sender, app_data):
        data_type = dpg.get_value("var_data_type_input")
        defaults = {
            "int": "0", "float": "0.0", "str": "", "list": "[]",
            "dict": "{}", "set": "set()", "bool": "True"
        }
        dpg.configure_item("var_value_input", default_value=defaults.get(data_type, ""))

    async def add_user_variable_from_dialog(self) -> None:
        try:
            name = dpg.get_value("var_name_input") or "unnamed"
            value_text = dpg.get_value("var_value_input")
            data_type_str = dpg.get_value("var_data_type_input")

            type_map = {"int": int, "float": float, "str": str, "list": list, "dict": dict, "set": set, "bool": bool}
            d_type = type_map.get(data_type_str, str)

            # Safe conversion
            if d_type in (list, dict, set, bool) and value_text not in (None, ""):
                # literal_eval handles lists, dicts, sets, booleans safely
                value = ast.literal_eval(value_text)
                if d_type is set and not isinstance(value, set):
                    value = set(value)
            elif d_type in (int, float):
                value = d_type(value_text)
            elif d_type is str:
                value = "" if value_text is None else str(value_text)
            else:
                value = value_text

            await self.add_variable(name=name, d_type=d_type, value=value)
            dpg.hide_item(self.add_var_dialog_id)

        except Exception as e:
            self._logger.error(Exception(f"Error adding user variable: {e}", self))

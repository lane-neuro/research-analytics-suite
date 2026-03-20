"""
DataManagementDialog Module

The DataManagementDialog class provides a user interface for managing memory slots, including adding, deleting, and
inspecting slots. It features a searchable list of slots and an inspector panel for detailed views.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from __future__ import annotations

import asyncio
import os
import ast

import dearpygui.dearpygui as dpg

from research_analytics_suite.gui.GUIBase import GUIBase
from research_analytics_suite.operation_manager.operations.system.UpdateMonitor import UpdateMonitor


class DataManagementDialog(GUIBase):
    """Data Inspector & Controls: operation chain viewer, operation details, data preview, and memory slots."""

    def __init__(self, width: int, height: int, parent):
        super().__init__(width, height, parent)

        from research_analytics_suite.data_engine.memory.MemoryManager import MemoryManager
        from research_analytics_suite.data_engine import Workspace

        self._memory_manager = MemoryManager()
        self._workspace = Workspace()

        self._selected_slot_id = None
        self._last_rendered_slot_id = None
        self._last_slot_count = -1
        self._selected_operation = None
        self._last_rendered_operation = None

        self.add_var_dialog_id = None
        self._subset_states = {}  # {slot_id: {"count": int, "filter_column_items": list, "conditions_group_tag": str}}

        # Operation manager layout for viewing operation chains
        self._operation_manager_layout = None

    # ------------------------------- LIFECYCLE --------------------------------

    async def initialize_gui(self) -> None:
        try:
            from research_analytics_suite.gui.modules.NotificationBus import notification_bus
            notification_bus.subscribe("operation_selected", self._on_operation_selected)

            # Create operation manager layout for operation chain viewing
            from research_analytics_suite.gui.modules.OperationManagerLayout import OperationManagerLayout
            op_layout_container_id = f"dm_op_layout_container_{self._runtime_id}"
            self._operation_manager_layout = OperationManagerLayout(
                width=self.width,
                height=380,
                parent=op_layout_container_id
            )
            await self._operation_manager_layout.initialize_gui()

            self._update_operation = await self._operation_control.operation_manager.create_operation(
                operation_type=UpdateMonitor,
                name="gui_DataManUpdate",
                action=self._update_async
            )
            self._update_operation.is_ready = True
        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    def draw(self) -> None:
        with dpg.child_window(tag="dm_main_container", parent=self._parent, width=-1, height=-1, border=False):
            # SECTION 1: Operation Chain Viewer & Details
            with dpg.collapsing_header(label="Operation Chain Viewer & Controls", default_open=False, parent="dm_main_container") as op_chain_header:
                # Draw operation manager layout (tree view + detail panel) as direct child of collapsing header
                with dpg.child_window(tag=f"dm_op_layout_container_{self._runtime_id}",
                                     width=-1,
                                     height=400,
                                     border=True,
                                     parent=op_chain_header):
                    if self._operation_manager_layout:
                        self._operation_manager_layout.draw()

            dpg.add_separator(parent="dm_main_container")

            # SECTION 2: Memory Slot Management
            with dpg.collapsing_header(label="Memory Slots", default_open=False, parent="dm_main_container"):
                self._draw_memory_section()

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        self.width, self.height = new_width, new_height
        if dpg.does_item_exist("dm_main_split"):
            dpg.configure_item("dm_main_split", width=self.width, height=self.height)

        # Resize operation manager layout
        if self._operation_manager_layout:
            await self._operation_manager_layout.resize_gui(new_width, 400)

    # ------------------------------- SECTION RENDERERS ------------------------

    def _draw_memory_section(self) -> None:
        """Draw memory slot management section (existing functionality)."""
        # Header with search and actions
        with dpg.group(horizontal=True):
            dpg.add_input_text(hint="Search slots...", tag="dm_search_input", width=200,
                              callback=self._on_search_change)
            dpg.add_button(label="Import Data", callback=self.show_data_import)
            dpg.add_button(label="+ Add Slot", callback=lambda: asyncio.create_task(self.open_add_var_dialog()))
            dpg.add_text("0 slot(s) loaded", tag="dm_slot_count_text")

        dpg.add_separator()

        # Split: Left = slot list, Right = inspector
        with dpg.group(tag="dm_main_split", horizontal=True):
            # LEFT: scrollable slot list
            with dpg.child_window(tag="dm_slot_list_scroll", width=300, height=250, border=True):
                dpg.add_group(tag="dm_slot_list_inner")

            # RIGHT: inspector mount
            with dpg.child_window(tag="dm_inspector_mount", width=-1, height=250, border=True):
                dpg.add_text("Select a slot from the list", tag="dm_inspector_placeholder", color=(150, 150, 150))

    def _on_operation_selected(self, operation_id: str) -> None:
        """Callback when an operation is selected from NotificationPanel or other sources."""
        try:
            from research_analytics_suite.operation_manager.control import OperationControl
            op_control = OperationControl()
            operation = op_control.operation_manager.get_operation(operation_id)

            if operation and self._operation_manager_layout:
                # Use OperationManagerLayout's detail panel to display the selected operation
                detail_panel = self._operation_manager_layout.get_detail_panel()
                if detail_panel:
                    detail_panel.set_operation(operation)
                self._selected_operation = operation_id
                self._logger.debug(f"Selected operation from notification: {operation.name}")
            else:
                self._logger.warning(f"Operation {operation_id} not found")

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

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
            if dpg.does_item_exist("dm_slot_count_text"):
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
                        dpg.add_table_column(init_width_or_weight=0.0, width_fixed=True)  # subset
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

                                # COL 3: subset button + tooltip
                                subset_btn_tag = f"dm_slot_subset_{s.memory_id}"
                                dpg.add_button(label="s",
                                               tag=subset_btn_tag,
                                               width=22, height=22,
                                               callback=self._on_click_subset,
                                               user_data=s.memory_id)
                                with dpg.tooltip(subset_btn_tag):
                                    dpg.add_text(f"Create subset of '{s.name}'")

                                # COL 4: delete x button + tooltip
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

        # Publish memory slot selection event for visualization workspace
        from research_analytics_suite.gui.modules.NotificationBus import notification_bus
        notification_bus.publish("memory_slot_selected", current_id)

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

    def _get_slot_columns(self, slot) -> list:
        """Return column names/indices from a slot's data for the filter dropdown."""
        try:
            import pandas as pd
            import numpy as np
            from research_analytics_suite.data_engine.core.DataContext import DataContext

            data_obj = slot.data_object if slot else None
            if data_obj is None:
                return []
            data = data_obj.data if isinstance(data_obj, DataContext) else data_obj

            if isinstance(data, pd.DataFrame):
                return [str(col) for col in data.columns]
            elif isinstance(data, np.ndarray) and data.ndim == 2:
                return [f"col_{i}" for i in range(data.shape[1])]
            elif isinstance(data, dict):
                return [str(k) for k in data.keys()]
            elif isinstance(data, list) and data and isinstance(data[0], dict):
                # list-of-dicts: use keys from the first row
                return [str(k) for k in data[0].keys()]
        except Exception as exc:
            self._logger.warning(f"_get_slot_columns failed: {exc}")
        return []

    def _on_click_subset(self, sender, app_data, user_data):
        """Open subset creation dialog for a slot."""
        slot_id = str(user_data)
        slot = self._memory_manager.get_slot(slot_id)
        name = slot.name if slot else slot_id

        modal_tag = f"dm_subset_modal_{slot_id}"
        if dpg.does_item_exist(modal_tag):
            dpg.delete_item(modal_tag)

        columns_available = self._get_slot_columns(slot)

        combinator_tag       = f"subset_combinator_{slot_id}"
        conditions_group_tag = f"subset_cond_group_{slot_id}"

        self._subset_states[slot_id] = {
            "count": 0,
            "filter_column_items": ["-- none --"] + columns_available,
            "conditions_group_tag": conditions_group_tag,
        }

        with dpg.window(tag=modal_tag, label=f"Create Subset - {name}", modal=True,
                        width=600, height=460, no_resize=True, show=True):

            dpg.add_text(f"Create a subset of '{name}'")
            dpg.add_separator()

            # New slot name
            dpg.add_text("New Slot Name:")
            name_input_tag = f"subset_name_{slot_id}"
            dpg.add_input_text(tag=name_input_tag, default_value=f"{name}_subset", width=200)

            dpg.add_separator()

            # Column selection
            dpg.add_text("Select Columns (leave empty for all):")
            columns_input_tag = f"subset_columns_{slot_id}"
            dpg.add_input_text(tag=columns_input_tag,
                               hint="e.g., column1,column2,column3",
                               multiline=True, height=60, width=400)

            dpg.add_separator()

            # Multi-condition row filter
            dpg.add_text("Keep rows where (optional):")
            with dpg.group(horizontal=True):
                dpg.add_text("Match:")
                dpg.add_combo(tag=combinator_tag, items=["AND", "OR"],
                              default_value="AND", width=65)

            # Scrollable container for condition rows
            with dpg.child_window(tag=conditions_group_tag, height=120, border=False):
                pass

            self._add_condition_row(slot_id)
            dpg.add_button(label="+ Add Condition",
                           callback=lambda: self._add_condition_row(slot_id))

            dpg.add_separator()

            # Row range selection
            with dpg.group(horizontal=True):
                dpg.add_text("Row Range (optional):")
                start_row_tag = f"subset_start_{slot_id}"
                end_row_tag   = f"subset_end_{slot_id}"
                dpg.add_input_int(tag=start_row_tag, label="Start", default_value=0, width=80)
                dpg.add_input_int(tag=end_row_tag,   label="End",   default_value=100, width=80)
                dpg.add_checkbox(tag=f"subset_use_range_{slot_id}", label="Use Range")

            dpg.add_separator()

            # Buttons
            with dpg.group(horizontal=True):
                dpg.add_button(label="Create Subset",
                               callback=lambda: asyncio.create_task(
                                   self._create_subset(slot_id, modal_tag, name_input_tag,
                                                       columns_input_tag, combinator_tag,
                                                       start_row_tag, end_row_tag,
                                                       f"subset_use_range_{slot_id}")
                               ))
                dpg.add_button(label="Cancel", callback=lambda: dpg.hide_item(modal_tag))

    def _add_condition_row(self, slot_id: str) -> None:
        """Append a new condition row inside the scrollable conditions container."""
        state = self._subset_states.get(slot_id)
        if state is None:
            return
        idx = state["count"]
        state["count"] += 1

        row_tag = f"subset_cond_row_{slot_id}_{idx}"
        col_tag = f"subset_cond_col_{slot_id}_{idx}"
        op_tag  = f"subset_cond_op_{slot_id}_{idx}"
        val_tag = f"subset_cond_val_{slot_id}_{idx}"

        with dpg.group(tag=row_tag, horizontal=True,
                       parent=state["conditions_group_tag"]):
            dpg.add_combo(tag=col_tag,
                          items=state["filter_column_items"],
                          default_value="-- none --", width=165)
            dpg.add_combo(tag=op_tag,
                          items=["<", ">", "==", "!=", "<=", ">="],
                          default_value="<", width=60)
            dpg.add_input_float(tag=val_tag, default_value=0.0,
                                width=110, format="%.4f")
            dpg.add_button(label="x", width=22,
                           callback=lambda t=row_tag: dpg.delete_item(t))

    async def _create_subset(self, source_slot_id: str, modal_tag: str,
                             name_input_tag: str, columns_input_tag: str,
                             combinator_tag: str,
                             start_row_tag: str, end_row_tag: str, use_range_tag: str):
        """Create a new memory slot with subset data."""
        try:
            import pandas as pd
            import numpy as np
            from dataclasses import replace as dc_replace
            from research_analytics_suite.data_engine.core.DataContext import DataContext

            new_name     = dpg.get_value(name_input_tag).strip()
            columns_text = dpg.get_value(columns_input_tag).strip()
            combinator   = dpg.get_value(combinator_tag)  # "AND" or "OR"
            start_row    = dpg.get_value(start_row_tag)
            end_row      = dpg.get_value(end_row_tag)
            use_range    = dpg.get_value(use_range_tag)

            if not new_name:
                new_name = f"subset_{source_slot_id[:8]}"

            source_slot = self._memory_manager.get_slot(source_slot_id)
            if not source_slot:
                raise ValueError(f"Source slot {source_slot_id} not found")

            stored_object = source_slot.data_object
            context = stored_object if isinstance(stored_object, DataContext) else None
            data = context.data if context else stored_object

            # --- Collect active conditions ---
            state = self._subset_states.get(source_slot_id, {})
            conditions = []
            for i in range(state.get("count", 0)):
                col_tag = f"subset_cond_col_{source_slot_id}_{i}"
                op_tag  = f"subset_cond_op_{source_slot_id}_{i}"
                val_tag = f"subset_cond_val_{source_slot_id}_{i}"
                if not dpg.does_item_exist(col_tag):
                    continue  # row was deleted via X button
                col = dpg.get_value(col_tag)
                if not col or col == "-- none --":
                    continue
                conditions.append((col, dpg.get_value(op_tag), float(dpg.get_value(val_tag))))

            self._logger.info(
                f"[Subset] data type={type(data).__name__}, "
                f"{combinator} of {len(conditions)} condition(s)"
            )

            # --- Row filter (multi-condition) ---
            _ops = {
                "<":  lambda a, b: a < b,
                ">":  lambda a, b: a > b,
                "==": lambda a, b: a == b,
                "!=": lambda a, b: a != b,
                "<=": lambda a, b: a <= b,
                ">=": lambda a, b: a >= b,
            }

            rows_before = (
                len(data) if isinstance(data, (list, dict)) else
                data.shape[0] if hasattr(data, "shape") else "?"
            )

            if isinstance(data, pd.DataFrame) and conditions:
                combined = pd.Series([combinator == "AND"] * len(data), index=data.index)
                for col, op, val in conditions:
                    col_match = col if col in data.columns else next(
                        (c for c in data.columns if str(c) == col), None)
                    if col_match is None:
                        self._logger.warning(f"[Subset] column {col!r} not in DataFrame")
                        continue
                    numeric = pd.to_numeric(data[col_match], errors="coerce")
                    mask = numeric.apply(lambda v: _ops[op](v, val) if v == v else False)
                    combined = (combined & mask) if combinator == "AND" else (combined | mask)
                data = data[combined].reset_index(drop=True)

            elif isinstance(data, np.ndarray) and data.ndim == 2 and conditions:
                combined = np.full(len(data), combinator == "AND", dtype=bool)
                for col, op, val in conditions:
                    try:
                        idx = int(col.replace("col_", ""))
                        col_vals = data[:, idx].astype(float)
                        mask = np.array([_ops[op](v, val) for v in col_vals])
                        combined = (combined & mask) if combinator == "AND" else (combined | mask)
                    except (ValueError, IndexError) as exc:
                        self._logger.warning(f"[Subset] ndarray filter error: {exc}")
                data = data[combined]

            elif isinstance(data, dict) and conditions:
                n = max((len(v) for v in data.values()), default=0)
                combined = [combinator == "AND"] * n
                for col, op, val in conditions:
                    if col not in data:
                        continue
                    for i, v in enumerate(data[col]):
                        try:
                            result = _ops[op](float(v), val) if v is not None else False
                        except (TypeError, ValueError):
                            result = False
                        combined[i] = (combined[i] and result) if combinator == "AND" else (combined[i] or result)
                data = {k: [v for v, keep in zip(vals, combined) if keep]
                        for k, vals in data.items()}

            elif isinstance(data, list) and data and isinstance(data[0], dict) and conditions:
                filtered = []
                for row in data:
                    keep = (combinator == "AND")
                    for col, op, val in conditions:
                        v = row.get(col)
                        try:
                            result = v is not None and _ops[op](float(v), val)
                        except (TypeError, ValueError):
                            result = False
                        keep = (keep and result) if combinator == "AND" else (keep or result)
                    if keep:
                        filtered.append(row)
                data = filtered

            rows_after = (
                len(data) if isinstance(data, (list, dict)) else
                data.shape[0] if hasattr(data, "shape") else "?"
            )
            if conditions:
                self._logger.info(
                    f"[Subset] {combinator} of {len(conditions)} condition(s): "
                    f"{rows_before} --> {rows_after} rows"
                )

            # --- Column selection ---
            if columns_text:
                columns = [c.strip() for c in columns_text.split(',') if c.strip()]
                if columns and isinstance(data, pd.DataFrame):
                    valid = [c for c in columns if c in data.columns]
                    if valid:
                        data = data[valid]

            # --- Row range ---
            if use_range:
                if isinstance(data, pd.DataFrame):
                    data = data.iloc[start_row:end_row].reset_index(drop=True)
                elif isinstance(data, np.ndarray):
                    data = data[start_row:end_row]
                elif isinstance(data, list):
                    data = data[start_row:end_row]
                elif isinstance(data, dict):
                    data = {k: v[start_row:end_row] for k, v in data.items()}

            # Wrap back into a DataContext, preserving original profile/schema
            result = dc_replace(context, data=data) if context else data

            await self._memory_manager.create_slot(
                name=new_name,
                data=result,
                d_type=type(result)
            )

            if dpg.does_item_exist(modal_tag):
                dpg.hide_item(modal_tag)

            self._subset_states.pop(source_slot_id, None)
            self._force_list_refresh = True
            self._logger.info(f"Created subset '{new_name}' from '{source_slot.name}'")

        except Exception as e:
            self._logger.error(f"Failed to create subset: {e}")

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
                context = await self._workspace.load_data(file_path)
                if context and context.data is not None:
                    name = os.path.basename(file_path)
                    # Store the entire DataContext (includes data, profile, and schema)
                    await self.add_variable(
                        name=name,
                        d_type=type(context),
                        value=context
                    )
        asyncio.run(_do())

    async def add_variable(self, name, d_type, value) -> None:
        """
        Add a variable to memory.

        Args:
            name: Variable name
            d_type: Data type (can be DataContext type)
            value: Value to store (can be DataContext with all metadata)
        """
        try:
            _slot_id, _, _ = await self._memory_manager.create_slot(
                name=name, d_type=d_type, data=value
            )
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

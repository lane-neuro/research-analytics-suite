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
        self._last_updated_modified_at = None  # Track last modified_at we updated from

    async def initialize_gui(self) -> None:
        try:
            self._update_operation = await self._operation_control.operation_manager.create_operation(
                operation_type=UpdateMonitor,
                name=f"gui_{self._root}",
                action=self._update_async
            )
            self._update_operation.is_ready = True

            # Initialize data view panel
            if hasattr(self, '_data_view_panel'):
                await self._data_view_panel.initialize_gui()
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
                             default_value=f"Type: {self._get_display_type()}")
                dpg.add_text(tag=f"{self._root}_shape", default_value=self._shape_text(self._slot.raw_data))
                dpg.add_text(tag=f"{self._root}_pointer", default_value=self._pointer_text(self._slot))

            # Data (preview + pointer combo)
            with dpg.collapsing_header(label="Data", default_open=True, tag=f"{self._root}_data_header"):
                self._render_data_section()

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
        previous_has_data = self._slot.has_own_data
        previous_pointer = self._slot.pointer

        while not self._update_operation.is_running:
            await asyncio.sleep(0.1)
        while True:
            await asyncio.sleep(0.25)
            try:
                slot = self._memory_manager.get_slot(self._slot.memory_id)
            except KeyError:
                continue
            self._slot = slot

            if not dpg.does_item_exist(f"{self._root}_title"):
                continue

            dpg.set_value(f"{self._root}_title", f"Slot: {slot.name} [{slot.memory_id}]")
            dpg.set_value(f"{self._root}_dtype", f"Type: {self._get_display_type(slot)}")
            dpg.set_value(f"{self._root}_shape", self._shape_text(slot.raw_data))
            dpg.set_value(f"{self._root}_pointer", self._pointer_text(slot))

            if slot.has_own_data != previous_has_data:
                previous_has_data = slot.has_own_data
                if dpg.does_item_exist(f"{self._root}_data_header"):
                    dpg.delete_item(f"{self._root}_data_header", children_only=True)
                    self._render_data_section()

            if slot.pointer != previous_pointer:
                previous_pointer = slot.pointer
                if dpg.does_item_exist(f"{self._root}_data_header"):
                    dpg.delete_item(f"{self._root}_data_header", children_only=True)
                    self._render_data_section()

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
        stored_data = self._slot.data_object
        await self._memory_manager.create_slot(
            name=f"{self._slot.name}_snapshot",
            d_type=type(stored_data),
            data=stored_data
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

    def _format_column_name(self, col, max_length=None, show_levels=True):
        """Format multi-level column names into readable strings."""
        if isinstance(col, tuple):
            if show_levels:
                parts = [str(part) for part in col if str(part).strip()]
                col_str = " > ".join(parts)
            else:
                col_str = str(col[-1])
        else:
            col_str = str(col)

        if max_length and len(col_str) > max_length:
            return col_str[:max_length-3] + "..."
        return col_str

    def _render_data_selector_ui(self):
        """Render UI for selecting data subset when pointer is set."""
        import pandas as pd
        import numpy as np
        from research_analytics_suite.data_engine.core.DataContext import DataContext

        try:
            if not self._slot.pointer:
                return

            target_slot = self._slot.pointer
            target_data = target_slot._data

            if isinstance(target_data, DataContext):
                target_data = target_data.data

            columns_to_show = []
            is_dataframe = isinstance(target_data, pd.DataFrame)
            is_2d_array = isinstance(target_data, np.ndarray) and target_data.ndim == 2
            is_2d_list = isinstance(target_data, list) and len(target_data) > 0 and isinstance(target_data[0], (list, tuple))

            if is_dataframe:
                columns_to_show = [(col, col) for col in target_data.columns]
            elif is_2d_array:
                num_cols = target_data.shape[1]
                columns_to_show = [(i, f"Column {i}") for i in range(num_cols)]
            elif is_2d_list:
                num_cols = len(target_data[0])
                columns_to_show = [(i, f"Column {i}") for i in range(num_cols)]
            else:
                return

            with dpg.collapsing_header(label="Data Selection", default_open=True, parent=f"{self._root}_data_header"):
                dpg.add_text("Select columns to use:", color=(180, 180, 180))
                dpg.add_spacer(height=3)

                all_column_keys = [col[0] for col in columns_to_show]
                current_selection = self._slot.data_selector.get('columns', []) if self._slot.data_selector else []

                with dpg.group(horizontal=True):
                    dpg.add_button(label="Select All", small=True,
                                 callback=lambda: self._on_column_selection_changed(all_column_keys))
                    dpg.add_button(label="Clear", small=True,
                                 callback=lambda: self._on_column_selection_changed([]))

                dpg.add_spacer(height=3)

                for col_key, col_raw in columns_to_show:
                    is_selected = col_key in current_selection if current_selection else False

                    col_label = self._format_column_name(col_raw, max_length=50)
                    full_name = self._format_column_name(col_raw, max_length=None)

                    checkbox = dpg.add_checkbox(
                        label=col_label,
                        default_value=is_selected,
                        callback=lambda s, a, u: self._on_column_toggle(u),
                        user_data=col_key,
                        tag=f"{self._root}_col_select_{col_key}"
                    )

                    if len(full_name) > 50:
                        with dpg.tooltip(checkbox):
                            dpg.add_text(full_name, wrap=400)

        except Exception as e:
            self._logger.error(f"Error rendering data selector UI: {e}", self.__class__.__name__)

    def _on_column_selection_changed(self, columns):
        """Handle column selection change."""
        try:
            slot = self._memory_manager.get_slot(self._slot.memory_id)
            if columns:
                slot.data_selector = {'columns': columns}
            else:
                slot.data_selector = None

            self._slot = slot

            if dpg.does_item_exist(f"{self._root}_data_header"):
                dpg.delete_item(f"{self._root}_data_header", children_only=True)
                self._render_data_section()
        except Exception as e:
            self._logger.error(f"Error updating column selection: {e}", self.__class__.__name__)

    def _on_column_toggle(self, column):
        """Toggle a single column in the selection."""
        try:
            slot = self._memory_manager.get_slot(self._slot.memory_id)
            current_selector = slot.data_selector or {}
            current_columns = list(current_selector.get('columns', []))

            if column in current_columns:
                current_columns.remove(column)
            else:
                current_columns.append(column)

            if current_columns:
                slot.data_selector = {'columns': current_columns}
            else:
                slot.data_selector = None

            self._slot = slot
        except Exception as e:
            self._logger.error(f"Error toggling column: {e}", self.__class__.__name__)

    def _render_data_section(self):
        """Render the data section with pointer control and data view."""
        if self._slot.has_own_data:
            with dpg.group(horizontal=True, parent=f"{self._root}_data_header"):
                dpg.add_text("Pointer:", color=(180, 180, 180))
                dpg.add_text("(disabled - slot contains data)", color=(150, 150, 100))
        else:
            from research_analytics_suite.gui import left_aligned_combo

            current_pointer_value = ""
            if self._slot.pointer:
                current_pointer_value = f"{self._slot.pointer.name} [{self._slot.pointer.memory_id}]"

            left_aligned_combo(
                label="Pointer",
                tag=f"{self._root}_pointer_combo",
                items=self._memory_manager.format_slot_name_id(),
                callback=self._on_pointer_changed,
                user_data=self._slot.memory_id,
                width=-1,
                parent=f"{self._root}_data_header",
                default_value=current_pointer_value
            )

        if self._slot.pointer:
            dpg.add_spacer(height=5, parent=f"{self._root}_data_header")
            self._render_data_selector_ui()

        from research_analytics_suite.gui.modules.DataViewPanel import DataViewPanel
        self._data_view_panel = DataViewPanel(
            width=self._width,
            height=400,
            parent=f"{self._root}_data_header",
            slot=self._slot
        )
        self._data_view_panel.draw()

        with dpg.group(horizontal=True, parent=f"{self._root}_data_header"):
            dpg.add_button(label="Validate", callback=self._validate)
            dpg.add_button(label="Snapshot", callback=self._snapshot)

    def _get_display_type(self, slot=None) -> str:
        """Get the display type, unwrapping DataContext if present."""
        from research_analytics_suite.data_engine.core.DataContext import DataContext

        target_slot = slot if slot is not None else self._slot
        stored_object = target_slot.data_object

        if isinstance(stored_object, DataContext):
            return format_type_for_display(type(stored_object.data))

        return format_type_for_display(target_slot.data_type)

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
        """
        Generate preview text for various data types.
        Supports: DataFrames, DataContext, numpy arrays, tensors, dicts, lists, etc.
        """
        from research_analytics_suite.data_engine.core.DataContext import DataContext

        try:
            # Unwrap DataContext if present
            if isinstance(data, DataContext):
                actual_data = data.data
                schema_info = data.schema
            else:
                actual_data = data
                schema_info = None

            # Handle pandas DataFrames
            import pandas as pd
            if isinstance(actual_data, pd.DataFrame):
                preview_lines = []
                if schema_info:
                    preview_lines.append(f"Columns: {', '.join(map(str, schema_info.get('columns', [])))}")
                    preview_lines.append(f"Shape: {schema_info.get('shape', 'N/A')}")
                    preview_lines.append("")

                # Show head of DataFrame with better formatting
                head_data = actual_data.head(20)
                preview_lines.append(head_data.to_string())

                if len(actual_data) > 20:
                    preview_lines.append(f"\n... {len(actual_data) - 20} more rows")

                return "\n".join(preview_lines)

            # Handle pandas Series
            if isinstance(actual_data, pd.Series):
                preview_lines = [f"Series: {actual_data.name or 'unnamed'}"]
                preview_lines.append(f"Length: {len(actual_data)}")
                preview_lines.append("")
                preview_lines.append(str(actual_data.head(20)))
                if len(actual_data) > 20:
                    preview_lines.append(f"\n... {len(actual_data) - 20} more values")
                return "\n".join(preview_lines)

            # Handle numpy arrays
            import numpy as np
            if isinstance(actual_data, np.ndarray):
                preview_lines = [f"NumPy Array"]
                preview_lines.append(f"Shape: {actual_data.shape}")
                preview_lines.append(f"Dtype: {actual_data.dtype}")
                preview_lines.append("")

                # Show array content based on dimensionality
                if actual_data.ndim == 1:
                    preview_lines.append(str(actual_data[:20]))
                    if len(actual_data) > 20:
                        preview_lines.append(f"... {len(actual_data) - 20} more values")
                elif actual_data.ndim == 2:
                    preview_lines.append(str(actual_data[:20, :]))
                    if actual_data.shape[0] > 20:
                        preview_lines.append(f"... {actual_data.shape[0] - 20} more rows")
                else:
                    preview_lines.append(str(actual_data))

                return "\n".join(preview_lines)

            # Handle PyTorch tensors
            try:
                import torch
                if isinstance(actual_data, torch.Tensor):
                    preview_lines = [f"PyTorch Tensor"]
                    preview_lines.append(f"Shape: {actual_data.shape}")
                    preview_lines.append(f"Dtype: {actual_data.dtype}")
                    preview_lines.append(f"Device: {actual_data.device}")
                    preview_lines.append("")

                    # Convert to numpy for display
                    np_data = actual_data.cpu().detach().numpy()
                    if np_data.ndim <= 2:
                        preview_lines.append(str(np_data[:20]))
                    else:
                        preview_lines.append(f"Tensor with {np_data.ndim} dimensions")

                    return "\n".join(preview_lines)
            except ImportError:
                pass

            # Handle dictionaries
            if isinstance(actual_data, dict):
                preview_lines = [f"Dictionary with {len(actual_data)} keys"]
                preview_lines.append("")

                # Show first few key-value pairs
                items = list(actual_data.items())[:10]
                for key, value in items:
                    value_str = str(value)
                    if len(value_str) > 100:
                        value_str = value_str[:100] + "..."
                    preview_lines.append(f"{key}: {value_str}")

                if len(actual_data) > 10:
                    preview_lines.append(f"... {len(actual_data) - 10} more entries")

                return "\n".join(preview_lines)

            # Handle lists and tuples
            if isinstance(actual_data, (list, tuple)):
                type_name = "List" if isinstance(actual_data, list) else "Tuple"
                preview_lines = [f"{type_name} with {len(actual_data)} items"]
                preview_lines.append("")

                # Show first few items
                items = actual_data[:20]
                for i, item in enumerate(items):
                    item_str = str(item)
                    if len(item_str) > 100:
                        item_str = item_str[:100] + "..."
                    preview_lines.append(f"[{i}]: {item_str}")

                if len(actual_data) > 20:
                    preview_lines.append(f"... {len(actual_data) - 20} more items")

                return "\n".join(preview_lines)

            # Fallback: convert to string
            txt = str(actual_data)
            return txt if len(txt) < 4000 else txt[:4000] + " …"

        except Exception as e:
            # Ultimate fallback
            txt = str(data)
            return txt if len(txt) < 4000 else txt[:4000] + " …"

    @staticmethod
    def _pointer_text(slot: MemorySlot) -> str:
        try:
            p = getattr(slot, "pointer", None)
            return f"Pointer: {p.name} [{p.memory_id}]" if p else "Pointer: (none)"
        except Exception:
            return "Pointer: (none)"

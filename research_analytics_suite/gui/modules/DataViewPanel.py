"""
DataViewPanel Module

Interactive data viewer with row/column selection controls for various data types.
Supports DataFrames, arrays, tensors, dictionaries, lists, and more.
"""
import asyncio
import dearpygui.dearpygui as dpg

from research_analytics_suite.gui.GUIBase import GUIBase
from research_analytics_suite.data_engine.memory.MemorySlot import MemorySlot
from research_analytics_suite.operation_manager.operations.system.UpdateMonitor import UpdateMonitor


class DataViewPanel(GUIBase):
    """
    Interactive data viewer panel with controls for selecting visible rows/columns.
    """

    def __init__(self, width: int, height: int, parent, slot: MemorySlot):
        super().__init__(width, height, parent)
        self._slot = slot
        self._root = f"data_view_{slot.memory_id}"
        self._last_updated_modified_at = None

        # View state
        self._start_row = 0
        self._end_row = 100
        self._visible_columns = None  # None means show all
        self._max_rows_to_display = 100
        self._max_cols_to_display = 20

    async def initialize_gui(self) -> None:
        """Initialize the update operation for the data view."""
        try:
            self._update_operation = await self._operation_control.operation_manager.create_operation(
                operation_type=UpdateMonitor,
                name=f"data_view_{self._slot.memory_id}",
                action=self._update_async
            )
            self._update_operation.is_ready = True
        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    def draw(self):
        """Draw the interactive data view panel."""
        if dpg.does_item_exist(self._root):
            dpg.delete_item(self._root)

        with dpg.group(tag=self._root, parent=self._parent):
            with dpg.child_window(tag=f"{self._root}_display", height=self._height, border=True):
                self._create_controls()
                self._render_data()

    def _create_controls(self):
        """Create interactive controls for row/column selection."""
        pass

    def _on_row_range_changed(self, sender, app_data):
        """Handle row range changes."""
        self._start_row = dpg.get_value(f"{self._root}_start_row")
        self._end_row = dpg.get_value(f"{self._root}_end_row")
        self._force_refresh()

    def _force_refresh(self, sender=None, app_data=None):
        """Force a refresh of the data display."""
        if dpg.does_item_exist(f"{self._root}_data_container"):
            dpg.delete_item(f"{self._root}_data_container")
        self._render_data()

    def _render_data(self):
        """Render the data based on its type."""
        from research_analytics_suite.data_engine.core.DataContext import DataContext

        if self._slot.pointer:
            data = self._slot.pointer.raw_data
        else:
            data = self._slot.raw_data

        try:
            # Unwrap DataContext if present
            if isinstance(data, DataContext):
                actual_data = data.data
                schema_info = data.schema
            else:
                actual_data = data
                schema_info = None

            # Dispatch to appropriate renderer
            import pandas as pd
            if isinstance(actual_data, pd.DataFrame):
                self._render_dataframe(actual_data, schema_info)
            elif isinstance(actual_data, pd.Series):
                self._render_series(actual_data)
            else:
                import numpy as np
                if isinstance(actual_data, np.ndarray):
                    self._render_array(actual_data)
                else:
                    # Try torch tensor
                    try:
                        import torch
                        if isinstance(actual_data, torch.Tensor):
                            np_data = actual_data.cpu().detach().numpy()
                            self._render_tensor(np_data, actual_data)
                            return
                    except ImportError:
                        pass

                    # Handle other types
                    if isinstance(actual_data, dict):
                        self._render_dict(actual_data)
                    elif isinstance(actual_data, (list, tuple)):
                        self._render_list(actual_data)
                    else:
                        self._render_text(actual_data)

        except Exception as e:
            self._logger.error(f"Error rendering data: {e}", self.__class__.__name__)
            self._render_text(data)

    def _render_dataframe(self, df, schema_info=None):
        """Render a pandas DataFrame with interactive controls."""
        with dpg.group(tag=f"{self._root}_data_container", parent=f"{self._root}_display"):
            all_columns = list(df.columns)

            with dpg.collapsing_header(label="Row Selection", default_open=False):
                with dpg.group(horizontal=True):
                    dpg.add_text("From:", color=(180, 180, 180))
                    dpg.add_input_int(
                        tag=f"{self._root}_start_row",
                        default_value=self._start_row,
                        width=80,
                        callback=self._on_row_range_changed,
                        min_value=0,
                        min_clamped=True
                    )
                    dpg.add_text("to", color=(180, 180, 180))
                    dpg.add_input_int(
                        tag=f"{self._root}_end_row",
                        default_value=self._end_row,
                        width=80,
                        callback=self._on_row_range_changed,
                        min_value=1,
                        min_clamped=True
                    )
                    dpg.add_button(label="Apply", callback=self._force_refresh, small=True)

            with dpg.collapsing_header(label="Column Visibility", default_open=False):
                with dpg.group(horizontal=True):
                    visible_count = len(all_columns) if self._visible_columns is None else len(self._visible_columns)
                    dpg.add_text(f"({visible_count}/{len(all_columns)} visible)", color=(150, 150, 150))
                    dpg.add_button(
                        label="Show All",
                        callback=lambda: self._select_columns(all_columns),
                        small=True
                    )
                    dpg.add_button(
                        label="Hide All",
                        callback=lambda: self._select_columns([]),
                        small=True
                    )

                dpg.add_spacer(height=3)

                with dpg.child_window(height=150, border=False):
                    num_cols_per_row = 3
                    for i in range(0, len(all_columns), num_cols_per_row):
                        with dpg.group(horizontal=True):
                            for col in all_columns[i:i + num_cols_per_row]:
                                selected = self._visible_columns is None or col in self._visible_columns
                                col_label = str(col)
                                if len(col_label) > 20:
                                    col_label = col_label[:17] + "..."

                                dpg.add_checkbox(
                                    label=col_label,
                                    default_value=selected,
                                    callback=lambda s, a, u: self._toggle_column(u),
                                    user_data=col
                                )

            dpg.add_spacer(height=5)

            display_df = df.iloc[self._start_row:self._end_row]
            if self._visible_columns:
                available_cols = [c for c in self._visible_columns if c in display_df.columns]
                if available_cols:
                    display_df = display_df[available_cols]

            if len(display_df) == 0:
                dpg.add_text("No data to display in selected range", color=(180, 180, 120))
                return

            if schema_info:
                dpg.add_text(f"Shape: {schema_info.get('shape', 'N/A')}", color=(150, 150, 150))
            else:
                rows, cols = df.shape
                dpg.add_text(f"{rows:,} rows × {cols} columns | Displaying rows {self._start_row}-{min(self._end_row, rows)}", color=(150, 150, 150))

            dpg.add_spacer(height=3)

            with dpg.table(
                header_row=True,
                borders_innerH=True,
                borders_outerH=True,
                borders_innerV=True,
                borders_outerV=True,
                scrollY=True,
                scrollX=True,
                policy=dpg.mvTable_SizingFixedFit,
                row_background=True,
                pad_outerX=True,
                height=-1
            ):
                dpg.add_table_column(label="Index", width_fixed=True, init_width_or_weight=80)

                for col in display_df.columns:
                    col_header = str(col)
                    if len(col_header) > 40:
                        col_header = col_header[:37] + "..."
                    dpg.add_table_column(label=col_header, width_fixed=True, init_width_or_weight=150)

                for idx, row in display_df.iterrows():
                    with dpg.table_row():
                        dpg.add_text(str(idx), color=(150, 200, 150))
                        for val in row:
                            val_str = str(val)
                            if len(val_str) > 80:
                                val_str = val_str[:77] + "..."
                            dpg.add_text(val_str)

    def _select_columns(self, columns):
        """Select specific columns to display."""
        self._visible_columns = columns if columns else None
        self._force_refresh()

    def _toggle_column(self, column):
        """Toggle a column's visibility."""
        from research_analytics_suite.data_engine.core.DataContext import DataContext
        import pandas as pd

        data = self._slot.raw_data
        if isinstance(data, DataContext):
            data = data.data

        if self._visible_columns is None and isinstance(data, pd.DataFrame):
            self._visible_columns = list(data.columns)

        if column in self._visible_columns:
            self._visible_columns.remove(column)
        else:
            if isinstance(data, pd.DataFrame):
                all_columns = list(data.columns)
                original_idx = all_columns.index(column)

                insert_idx = 0
                for i, visible_col in enumerate(self._visible_columns):
                    if visible_col in all_columns and all_columns.index(visible_col) < original_idx:
                        insert_idx = i + 1

                self._visible_columns.insert(insert_idx, column)
            else:
                self._visible_columns.append(column)

        self._force_refresh()

    def _render_series(self, series):
        """Render a pandas Series."""
        with dpg.group(tag=f"{self._root}_data_container", parent=f"{self._root}_display"):
            dpg.add_text(f"Series: {series.name or 'unnamed'}")
            dpg.add_text(f"Length: {len(series)}")

            display_series = series.iloc[self._start_row:self._end_row]

            with dpg.table(
                header_row=True,
                borders_innerH=True,
                borders_outerH=True,
                borders_innerV=True,
                borders_outerV=True,
                scrollY=True,
                policy=dpg.mvTable_SizingStretchProp
            ):
                dpg.add_table_column(label="Index")
                dpg.add_table_column(label="Value")

                for idx, val in display_series.items():
                    with dpg.table_row():
                        dpg.add_text(str(idx))
                        val_str = str(val)
                        if len(val_str) > 100:
                            val_str = val_str[:100] + "..."
                        dpg.add_text(val_str)

    def _render_array(self, arr):
        """Render a numpy array."""
        with dpg.group(tag=f"{self._root}_data_container", parent=f"{self._root}_display"):
            dpg.add_text(f"NumPy Array - Shape: {arr.shape}, Dtype: {arr.dtype}")

            if arr.ndim == 1:
                display_arr = arr[self._start_row:self._end_row]

                with dpg.table(
                    header_row=True,
                    borders_innerH=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_outerV=True,
                    scrollY=True,
                    policy=dpg.mvTable_SizingStretchProp
                ):
                    dpg.add_table_column(label="Index")
                    dpg.add_table_column(label="Value")

                    for idx, val in enumerate(display_arr, start=self._start_row):
                        with dpg.table_row():
                            dpg.add_text(str(idx))
                            dpg.add_text(str(val))

            elif arr.ndim == 2:
                display_arr = arr[self._start_row:self._end_row, :]

                with dpg.table(
                    header_row=True,
                    borders_innerH=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_outerV=True,
                    scrollY=True,
                    scrollX=True,
                    policy=dpg.mvTable_SizingStretchProp
                ):
                    dpg.add_table_column(label="Row")
                    for col_idx in range(min(arr.shape[1], self._max_cols_to_display)):
                        dpg.add_table_column(label=f"Col {col_idx}")

                    for row_idx, row in enumerate(display_arr, start=self._start_row):
                        with dpg.table_row():
                            dpg.add_text(str(row_idx))
                            for col_idx in range(min(arr.shape[1], self._max_cols_to_display)):
                                dpg.add_text(str(row[col_idx]))

            else:
                dpg.add_text(f"Array with {arr.ndim} dimensions")
                dpg.add_text(str(arr))

    def _render_tensor(self, np_data, tensor):
        """Render a PyTorch tensor."""
        with dpg.group(tag=f"{self._root}_data_container", parent=f"{self._root}_display"):
            dpg.add_text(f"PyTorch Tensor")
            dpg.add_text(f"Shape: {tensor.shape}, Dtype: {tensor.dtype}, Device: {tensor.device}")
            dpg.add_separator()

        # Render as array
        self._render_array(np_data)

    def _render_dict(self, d):
        """Render a dictionary."""
        with dpg.group(tag=f"{self._root}_data_container", parent=f"{self._root}_display"):
            dpg.add_text(f"Dictionary with {len(d)} keys")

            items = list(d.items())[self._start_row:self._end_row]

            with dpg.table(
                header_row=True,
                borders_innerH=True,
                borders_outerH=True,
                borders_innerV=True,
                borders_outerV=True,
                scrollY=True,
                policy=dpg.mvTable_SizingStretchProp
            ):
                dpg.add_table_column(label="Key")
                dpg.add_table_column(label="Value")

                for key, value in items:
                    with dpg.table_row():
                        dpg.add_text(str(key))
                        val_str = str(value)
                        if len(val_str) > 100:
                            val_str = val_str[:100] + "..."
                        dpg.add_text(val_str)

    def _render_list(self, lst):
        """Render a list or tuple."""
        with dpg.group(tag=f"{self._root}_data_container", parent=f"{self._root}_display"):
            type_name = "List" if isinstance(lst, list) else "Tuple"
            dpg.add_text(f"{type_name} with {len(lst)} items")

            items = lst[self._start_row:self._end_row]

            with dpg.table(
                header_row=True,
                borders_innerH=True,
                borders_outerH=True,
                borders_innerV=True,
                borders_outerV=True,
                scrollY=True,
                policy=dpg.mvTable_SizingStretchProp
            ):
                dpg.add_table_column(label="Index")
                dpg.add_table_column(label="Value")

                for idx, item in enumerate(items, start=self._start_row):
                    with dpg.table_row():
                        dpg.add_text(str(idx))
                        item_str = str(item)
                        if len(item_str) > 100:
                            item_str = item_str[:100] + "..."
                        dpg.add_text(item_str)

    def _render_text(self, data):
        """Fallback text display."""
        with dpg.group(tag=f"{self._root}_data_container", parent=f"{self._root}_display"):
            txt = str(data)
            if len(txt) > 4000:
                txt = txt[:4000] + " …"
            dpg.add_text(txt, wrap=0)

    async def _update_async(self) -> None:
        """Update the data view when slot data changes."""
        while not self._update_operation.is_running:
            await asyncio.sleep(0.1)

        while True:
            await asyncio.sleep(0.5)  # Less frequent updates since we have manual refresh

            # Check if data has been modified
            current_modified_at = getattr(self._slot, '_modified_at', None)

            if current_modified_at is not None and current_modified_at != self._last_updated_modified_at:
                self._last_updated_modified_at = current_modified_at

                # Data changed, force refresh
                if dpg.does_item_exist(f"{self._root}_data_container"):
                    dpg.delete_item(f"{self._root}_data_container")
                    self._render_data()

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        """Resize the GUI."""
        self.width = new_width
        self.height = new_height

        if dpg.does_item_exist(f"{self._root}_display"):
            dpg.configure_item(f"{self._root}_display", height=new_height)

    def set_slot(self, slot: MemorySlot):
        """Update the slot being viewed."""
        self._slot = slot
        self._last_updated_modified_at = None
        self._force_refresh()

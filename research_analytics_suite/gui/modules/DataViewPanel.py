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
    Supports optional editing of data when editable=True.
    """

    def __init__(self, width: int, height: int, parent, slot: MemorySlot, editable: bool = False):
        super().__init__(width, height, parent)
        self._slot = slot
        self._root = f"data_view_{slot.memory_id}"
        self._last_updated_modified_at = None
        self._editable = editable

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
                    elif self._editable and isinstance(actual_data, (str, int, float, bool)):
                        self._render_editable_scalar(actual_data)
                    else:
                        self._render_text(actual_data)

        except Exception as e:
            self._logger.error(f"Error rendering data: {e}", self.__class__.__name__)
            self._render_text(data)

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
                        callback=lambda s, a, u: self._select_columns(all_columns),
                        small=True
                    )
                    dpg.add_button(
                        label="Hide All",
                        callback=lambda s, a, u: self._select_columns([]),
                        small=True
                    )

                dpg.add_spacer(height=3)

                with dpg.child_window(height=150, border=False):
                    num_cols_per_row = 2
                    for i in range(0, len(all_columns), num_cols_per_row):
                        with dpg.group(horizontal=True):
                            for col in all_columns[i:i + num_cols_per_row]:
                                selected = self._visible_columns is None or col in self._visible_columns
                                col_label = self._format_column_name(col, max_length=35)
                                full_name = self._format_column_name(col, max_length=None)

                                checkbox = dpg.add_checkbox(
                                    label=col_label,
                                    default_value=selected,
                                    callback=lambda s, a, u: self._toggle_column(u),
                                    user_data=col
                                )

                                if len(full_name) > 35:
                                    with dpg.tooltip(checkbox):
                                        dpg.add_text(full_name)

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

            if self._editable:
                dpg.add_text("Click a cell to edit it", color=(150, 150, 150))

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
                    col_header = self._format_column_name(col, max_length=50)
                    full_col_name = self._format_column_name(col, max_length=None)

                    table_col = dpg.add_table_column(label=col_header, width_fixed=True, init_width_or_weight=200)

                    if len(full_col_name) > 50:
                        with dpg.tooltip(table_col):
                            dpg.add_text(full_col_name, wrap=400)

                for idx, row in display_df.iterrows():
                    with dpg.table_row():
                        dpg.add_text(str(idx), color=(150, 200, 150))
                        for col_idx, val in enumerate(row):
                            val_str = str(val)
                            if len(val_str) > 80:
                                val_str = val_str[:77] + "..."

                            if self._editable:
                                col_name = display_df.columns[col_idx]
                                dpg.add_selectable(
                                    label=val_str,
                                    callback=lambda s, a, u: self._open_cell_edit_modal(*u),
                                    user_data=(idx, col_name, val)
                                )
                            else:
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
        """Render a numpy array with optional editing."""
        with dpg.group(tag=f"{self._root}_data_container", parent=f"{self._root}_display"):
            dpg.add_text(f"NumPy Array - Shape: {arr.shape}, Dtype: {arr.dtype}")

            if self._editable and arr.ndim <= 2:
                dpg.add_text("Click a cell to edit it", color=(150, 150, 150))

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
                            if self._editable:
                                dpg.add_selectable(
                                    label=str(val),
                                    callback=lambda s, a, u: self._open_array_edit_modal(u[0], u[1], u[2]),
                                    user_data=(idx, None, val)
                                )
                            else:
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
                                val = row[col_idx]
                                if self._editable:
                                    dpg.add_selectable(
                                        label=str(val),
                                        callback=lambda s, a, u: self._open_array_edit_modal(u[0], u[1], u[2]),
                                        user_data=(row_idx, col_idx, val)
                                    )
                                else:
                                    dpg.add_text(str(val))

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
        """Render a dictionary with optional editing."""
        with dpg.group(tag=f"{self._root}_data_container", parent=f"{self._root}_display"):
            dpg.add_text(f"Dictionary with {len(d)} keys")

            if self._editable:
                dpg.add_text("Click a value to edit it", color=(150, 150, 150))

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
                if self._editable:
                    dpg.add_table_column(label="", width_fixed=True, init_width_or_weight=30)

                for key, value in items:
                    with dpg.table_row():
                        dpg.add_text(str(key))
                        val_str = str(value)
                        if len(val_str) > 100:
                            val_str = val_str[:100] + "..."

                        if self._editable:
                            dpg.add_selectable(
                                label=val_str,
                                callback=lambda s, a, u: self._open_dict_edit_modal(u[0], u[1]),
                                user_data=(key, value)
                            )
                            dpg.add_button(
                                label="X",
                                small=True,
                                callback=lambda s, a, u: asyncio.create_task(self._delete_dict_key(u)),
                                user_data=key
                            )
                        else:
                            dpg.add_text(val_str)

            if self._editable:
                dpg.add_spacer(height=10)
                dpg.add_button(label="+ Add Entry", callback=self._open_add_dict_entry_modal)

    def _render_list(self, lst):
        """Render a list or tuple with optional editing."""
        is_tuple = isinstance(lst, tuple)
        with dpg.group(tag=f"{self._root}_data_container", parent=f"{self._root}_display"):
            type_name = "List" if not is_tuple else "Tuple"
            dpg.add_text(f"{type_name} with {len(lst)} items")

            if self._editable:
                if is_tuple:
                    dpg.add_text("Note: Editing will convert tuple to list", color=(255, 200, 100))
                dpg.add_text("Click a value to edit it", color=(150, 150, 150))

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
                if self._editable:
                    dpg.add_table_column(label="", width_fixed=True, init_width_or_weight=30)

                for idx, item in enumerate(items, start=self._start_row):
                    with dpg.table_row():
                        dpg.add_text(str(idx))
                        item_str = str(item)
                        if len(item_str) > 100:
                            item_str = item_str[:100] + "..."

                        if self._editable:
                            dpg.add_selectable(
                                label=item_str,
                                callback=lambda s, a, u: self._open_list_edit_modal(u[0], u[1]),
                                user_data=(idx, item)
                            )
                            dpg.add_button(
                                label="X",
                                small=True,
                                callback=lambda s, a, u: asyncio.create_task(self._delete_list_item(u)),
                                user_data=idx
                            )
                        else:
                            dpg.add_text(item_str)

            if self._editable:
                dpg.add_spacer(height=10)
                dpg.add_button(label="+ Add Item", callback=self._open_add_list_item_modal)

    def _render_editable_scalar(self, data):
        """Render an editable scalar value (str, int, float, bool)."""
        with dpg.group(tag=f"{self._root}_data_container", parent=f"{self._root}_display"):
            dpg.add_text(f"Type: {type(data).__name__}", color=(150, 150, 150))
            dpg.add_spacer(height=5)

            if isinstance(data, bool):
                dpg.add_checkbox(
                    label="Value",
                    default_value=data,
                    callback=lambda s, v: asyncio.create_task(self._save_scalar_value(v)),
                    tag=f"{self._root}_scalar_edit"
                )
            elif isinstance(data, int):
                with dpg.group(horizontal=True):
                    dpg.add_input_int(
                        default_value=data,
                        tag=f"{self._root}_scalar_edit",
                        width=200
                    )
                    dpg.add_button(label="Save",
                                   callback=lambda s, a, u: asyncio.create_task(self._save_scalar_from_input(int)))
            elif isinstance(data, float):
                with dpg.group(horizontal=True):
                    dpg.add_input_float(
                        default_value=data,
                        tag=f"{self._root}_scalar_edit",
                        width=200
                    )
                    dpg.add_button(label="Save",
                                   callback=lambda s, a, u: asyncio.create_task(self._save_scalar_from_input(float)))
            else:  # string
                with dpg.group(horizontal=True):
                    dpg.add_input_text(
                        default_value=str(data),
                        tag=f"{self._root}_scalar_edit",
                        width=300
                    )
                    dpg.add_button(label="Save",
                                   callback=lambda s, a, u: asyncio.create_task(self._save_scalar_from_input(str)))

    async def _save_scalar_value(self, value):
        """Save a scalar value directly (for checkboxes)."""
        try:
            self._slot.data = value
            self._force_refresh()
        except Exception as e:
            self._logger.error(f"Failed to save scalar: {e}", self.__class__.__name__)

    async def _save_scalar_from_input(self, data_type):
        """Save scalar value from input field."""
        try:
            raw_value = dpg.get_value(f"{self._root}_scalar_edit")
            value = data_type(raw_value)
            await self._save_scalar_value(value)
        except Exception as e:
            self._logger.error(f"Failed to convert/save scalar: {e}", self.__class__.__name__)

    def _open_dict_edit_modal(self, key, current_value):
        """Open modal to edit a dictionary value."""
        modal_tag = f"{self._root}_dict_edit_modal"
        if dpg.does_item_exist(modal_tag):
            dpg.delete_item(modal_tag)

        display_value = self._to_native_value(current_value)

        with dpg.window(tag=modal_tag, label=f"Edit '{key}'", modal=True,
                        width=400, height=220, show=True):
            dpg.add_text(f"Key: {key}")
            dpg.add_input_text(
                label="Value",
                default_value=repr(display_value),
                tag=f"{self._root}_dict_value_input",
                width=300,
                multiline=True,
                height=80
            )
            dpg.add_text("Use Python literal syntax: 42, 'text', [1,2], {'a':1}",
                         color=(150, 150, 150))
            dpg.add_spacer(height=5)
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Save",
                    callback=lambda s, a, u: asyncio.create_task(self._save_dict_edit(key, modal_tag))
                )
                dpg.add_button(label="Cancel", callback=lambda s, a, u: dpg.delete_item(modal_tag))

    async def _save_dict_edit(self, key, modal_tag):
        """Save edited dictionary value."""
        import ast
        try:
            value_text = dpg.get_value(f"{self._root}_dict_value_input")
            new_value = ast.literal_eval(value_text)

            # Get current dict, update it, save back
            current_data = dict(self._slot.raw_data)
            current_data[key] = new_value

            self._slot.data = current_data

            dpg.delete_item(modal_tag)
            self._force_refresh()
        except Exception as e:
            self._logger.error(f"Failed to save dict edit: {e}", self.__class__.__name__)

    async def _delete_dict_key(self, key):
        """Delete a key from the dictionary."""
        try:
            current_data = dict(self._slot.raw_data)
            del current_data[key]

            self._slot.data = current_data
            self._force_refresh()
        except Exception as e:
            self._logger.error(f"Failed to delete dict key: {e}", self.__class__.__name__)

    def _open_add_dict_entry_modal(self):
        """Open modal to add a new dictionary entry."""
        modal_tag = f"{self._root}_dict_add_modal"
        if dpg.does_item_exist(modal_tag):
            dpg.delete_item(modal_tag)

        with dpg.window(tag=modal_tag, label="Add Entry", modal=True,
                        width=400, height=220, show=True):
            dpg.add_input_text(
                label="Key",
                tag=f"{self._root}_dict_new_key",
                width=300
            )
            dpg.add_input_text(
                label="Value",
                default_value="",
                tag=f"{self._root}_dict_new_value",
                width=300,
                multiline=True,
                height=60
            )
            dpg.add_text("Use Python literal syntax for value",
                         color=(150, 150, 150))
            dpg.add_spacer(height=5)
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Add",
                    callback=lambda s, a, u: asyncio.create_task(self._add_dict_entry(modal_tag))
                )
                dpg.add_button(label="Cancel", callback=lambda s, a, u: dpg.delete_item(modal_tag))

    async def _add_dict_entry(self, modal_tag):
        """Add a new entry to the dictionary."""
        import ast
        try:
            key = dpg.get_value(f"{self._root}_dict_new_key")
            value_text = dpg.get_value(f"{self._root}_dict_new_value")

            if not key:
                self._logger.warning("Key cannot be empty")
                return

            try:
                new_value = ast.literal_eval(value_text)
            except:
                new_value = value_text  # Treat as string if not valid Python literal

            current_data = dict(self._slot.raw_data)
            current_data[key] = new_value

            self._slot.data = current_data

            dpg.delete_item(modal_tag)
            self._force_refresh()
        except Exception as e:
            self._logger.error(f"Failed to add dict entry: {e}", self.__class__.__name__)

    def _open_list_edit_modal(self, index, current_value):
        """Open modal to edit a list item."""
        modal_tag = f"{self._root}_list_edit_modal"
        if dpg.does_item_exist(modal_tag):
            dpg.delete_item(modal_tag)

        display_value = self._to_native_value(current_value)

        with dpg.window(tag=modal_tag, label=f"Edit Item [{index}]", modal=True,
                        width=400, height=200, show=True):
            dpg.add_text(f"Index: {index}")
            dpg.add_input_text(
                label="Value",
                default_value=repr(display_value),
                tag=f"{self._root}_list_value_input",
                width=300,
                multiline=True,
                height=60
            )
            dpg.add_text("Use Python literal syntax: 42, 'text', [1,2], {'a':1}",
                         color=(150, 150, 150))
            dpg.add_spacer(height=5)
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Save",
                    callback=lambda s, a, u: asyncio.create_task(self._save_list_edit(index, modal_tag))
                )
                dpg.add_button(label="Cancel", callback=lambda s, a, u: dpg.delete_item(modal_tag))

    async def _save_list_edit(self, index, modal_tag):
        """Save edited list item."""
        import ast
        try:
            value_text = dpg.get_value(f"{self._root}_list_value_input")
            new_value = ast.literal_eval(value_text)

            # Get current list, update it, save back
            current_data = list(self._slot.raw_data)
            current_data[index] = new_value

            # Use direct data setter instead of async update_slot to avoid lock issues
            await self._slot.set_data(current_data)

            dpg.delete_item(modal_tag)
            self._force_refresh()
        except Exception as e:
            self._logger.error(f"Failed to save list edit: {e}", self.__class__.__name__)

    async def _delete_list_item(self, index):
        """Delete an item from the list."""
        try:
            current_data = list(self._slot.raw_data)
            del current_data[index]

            self._slot.data = current_data
            self._force_refresh()
        except Exception as e:
            self._logger.error(f"Failed to delete list item: {e}", self.__class__.__name__)

    def _open_add_list_item_modal(self):
        """Open modal to add a new list item."""
        modal_tag = f"{self._root}_list_add_modal"
        if dpg.does_item_exist(modal_tag):
            dpg.delete_item(modal_tag)

        with dpg.window(tag=modal_tag, label="Add Item", modal=True,
                        width=400, height=180, show=True):
            dpg.add_input_text(
                label="Value",
                default_value="",
                tag=f"{self._root}_list_new_value",
                width=300,
                multiline=True,
                height=60
            )
            dpg.add_text("Use Python literal syntax for value",
                         color=(150, 150, 150))
            dpg.add_spacer(height=5)
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Add",
                    callback=lambda s, a, u: asyncio.create_task(self._add_list_item(modal_tag))
                )
                dpg.add_button(label="Cancel", callback=lambda s, a, u: dpg.delete_item(modal_tag))

    async def _add_list_item(self, modal_tag):
        """Add a new item to the list."""
        import ast
        try:
            value_text = dpg.get_value(f"{self._root}_list_new_value")

            try:
                new_value = ast.literal_eval(value_text)
            except:
                new_value = value_text  # Treat as string if not valid Python literal

            current_data = list(self._slot.raw_data)
            current_data.append(new_value)

            self._slot.data = current_data

            dpg.delete_item(modal_tag)
            self._force_refresh()
        except Exception as e:
            self._logger.error(f"Failed to add list item: {e}", self.__class__.__name__)

    def _open_cell_edit_modal(self, row_idx, col_name, current_value):
        """Open modal to edit a DataFrame cell."""
        modal_tag = f"{self._root}_cell_edit_modal"
        if dpg.does_item_exist(modal_tag):
            dpg.delete_item(modal_tag)

        col_display = self._format_column_name(col_name, max_length=30)
        display_value = self._to_native_value(current_value)

        with dpg.window(tag=modal_tag, label=f"Edit Cell [{row_idx}, {col_display}]",
                        modal=True, width=350, height=180, show=True):
            dpg.add_text(f"Row: {row_idx}")
            dpg.add_text(f"Column: {self._format_column_name(col_name)}")
            dpg.add_input_text(
                label="Value",
                default_value=str(display_value),
                tag=f"{self._root}_cell_value_input",
                width=250
            )
            dpg.add_spacer(height=5)
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Save",
                    callback=lambda s, a, u: asyncio.create_task(
                        self._save_cell_edit(row_idx, col_name, modal_tag)
                    )
                )
                dpg.add_button(label="Cancel", callback=lambda s, a, u: dpg.delete_item(modal_tag))

    async def _save_cell_edit(self, row_idx, col_name, modal_tag):
        """Save edited DataFrame cell."""
        import pandas as pd
        try:
            value_text = dpg.get_value(f"{self._root}_cell_value_input")

            # Get current DataFrame
            df = self._slot.raw_data.copy()

            # Try to preserve type
            original_dtype = df[col_name].dtype
            try:
                if pd.api.types.is_integer_dtype(original_dtype):
                    new_value = int(value_text)
                elif pd.api.types.is_float_dtype(original_dtype):
                    new_value = float(value_text)
                elif pd.api.types.is_bool_dtype(original_dtype):
                    new_value = value_text.lower() in ('true', '1', 'yes')
                else:
                    new_value = value_text
            except:
                new_value = value_text

            df.at[row_idx, col_name] = new_value

            self._slot.data = df

            dpg.delete_item(modal_tag)
            self._force_refresh()
        except Exception as e:
            self._logger.error(f"Failed to save cell edit: {e}", self.__class__.__name__)

    def _to_native_value(self, value):
        """Convert numpy/pandas scalar types to native Python types for display."""
        import numpy as np
        if hasattr(value, 'item'):
            return value.item()
        return value

    def _open_array_edit_modal(self, row_idx, col_idx, current_value):
        """Open modal to edit a numpy array cell."""
        modal_tag = f"{self._root}_array_edit_modal"
        if dpg.does_item_exist(modal_tag):
            dpg.delete_item(modal_tag)

        if col_idx is None:
            label = f"Edit Array [{row_idx}]"
            location = f"Index: {row_idx}"
        else:
            label = f"Edit Array [{row_idx}, {col_idx}]"
            location = f"Row: {row_idx}, Column: {col_idx}"

        display_value = self._to_native_value(current_value)

        with dpg.window(tag=modal_tag, label=label,
                        modal=True, width=350, height=160, show=True):
            dpg.add_text(location)
            dpg.add_input_text(
                label="Value",
                default_value=str(display_value),
                tag=f"{self._root}_array_value_input",
                width=250
            )
            dpg.add_spacer(height=5)
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Save",
                    callback=lambda s, a, u: asyncio.create_task(
                        self._save_array_edit(row_idx, col_idx, modal_tag)
                    )
                )
                dpg.add_button(label="Cancel", callback=lambda s, a, u: dpg.delete_item(modal_tag))

    async def _save_array_edit(self, row_idx, col_idx, modal_tag):
        """Save edited numpy array cell."""
        import numpy as np
        try:
            value_text = dpg.get_value(f"{self._root}_array_value_input")

            # Get current array
            arr = self._slot.raw_data.copy()

            # Try to preserve dtype
            try:
                if np.issubdtype(arr.dtype, np.integer):
                    new_value = int(value_text)
                elif np.issubdtype(arr.dtype, np.floating):
                    new_value = float(value_text)
                elif np.issubdtype(arr.dtype, np.bool_):
                    new_value = value_text.lower() in ('true', '1', 'yes')
                else:
                    new_value = value_text
            except:
                new_value = value_text

            if col_idx is None:
                arr[row_idx] = new_value
            else:
                arr[row_idx, col_idx] = new_value

            self._slot.data = arr

            dpg.delete_item(modal_tag)
            self._force_refresh()
        except Exception as e:
            self._logger.error(f"Failed to save array edit: {e}", self.__class__.__name__)

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

"""
VisualizationWorkspace Module

Central visualization workspace with multi-tab interface for automatic data visualization.
Detects data types and renders appropriate visualizations with export capabilities.

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
from typing import Optional, Dict, Any, List
import dearpygui.dearpygui as dpg
from matplotlib.figure import Figure

from research_analytics_suite.gui.GUIBase import GUIBase
from research_analytics_suite.gui.modules.NotificationBus import notification_bus
from research_analytics_suite.gui.modules.VisualizationDetector import VisualizationDetector
from research_analytics_suite.gui.modules.VisualizationRenderer import VisualizationRenderer
from research_analytics_suite.operation_manager.operations.system.UpdateMonitor import UpdateMonitor


class VisualizationTab:
    """Represents a single visualization tab."""

    def __init__(self, tab_id: str, title: str, data: Any = None):
        self.tab_id = tab_id
        self.title = title
        self.data = data
        self.is_pinned = False
        self.viz_type = "auto"
        self.viz_config: Optional[Dict[str, Any]] = None
        self.rendered_image: Optional[str] = None
        self.figure: Optional[Figure] = None
        self.texture_id: Optional[str] = None
        self.selected_columns: Optional[list] = None  # For column selection in DataFrames
        self.numeric_columns: Optional[list] = None  # Available numeric columns
        self.all_columns: Optional[list] = None  # All columns in DataFrame

        # User customization options
        self.custom_options: Dict[str, Any] = {
            'title': None,  # Custom chart title (None = auto)
            'x_label': None,  # X-axis label (None = auto)
            'y_label': None,  # Y-axis label (None = auto)
            'show_grid': True,
            'show_legend': True,
            'color_map': 'viridis',  # For heatmaps
            'marker_size': 20,  # For scatter plots
            'line_style': '-',  # solid, dashed, dotted
            'alpha': 0.7,  # Transparency
            'bins': 30,  # For histograms
            'aggregation': 'mean',  # For bar charts: mean, sum, count, median
            'x_column': None,  # Manual X column selection
            'y_columns': None,  # Manual Y columns selection
            'category_column': None,  # Manual category selection
            'value_columns': None,  # Manual value columns selection
            'filter_column': None,  # Column to filter by
            'filter_values': None,  # Values to include in filter
            'chart_width': None,  # Custom chart width (None = auto)
            'chart_height': None,  # Custom chart height (None = auto)
        }


class VisualizationWorkspace(GUIBase):
    """
    Main visualization workspace with tabbed interface for displaying operation results.
    """

    # All supported chart types
    CHART_TYPES = [
        ('line', 'Line Chart'),
        ('scatter', 'Scatter Plot'),
        ('bar', 'Bar Chart'),
        ('histogram', 'Histogram'),
        ('box', 'Box Plot'),
        ('heatmap', 'Heatmap'),
        ('correlation_heatmap', 'Correlation Heatmap'),
        ('pie', 'Pie Chart'),
        ('area', 'Area Chart'),
        ('text', 'Text/Raw Data'),
    ]

    # Color map options for heatmaps
    COLOR_MAPS = ['viridis', 'plasma', 'inferno', 'magma', 'cividis',
                  'RdBu_r', 'coolwarm', 'seismic', 'Blues', 'Greens', 'Reds']

    # Line styles
    LINE_STYLES = [('-', 'Solid'), ('--', 'Dashed'), (':', 'Dotted'), ('-.', 'Dash-Dot')]

    # Aggregation methods for bar charts
    AGGREGATIONS = ['mean', 'sum', 'count', 'median', 'min', 'max', 'std']

    def __init__(self, width: int, height: int, parent: str):
        super().__init__(width, height, parent)
        self._workspace_id = f"viz_workspace_{self._runtime_id}"
        self._tab_bar_id = f"viz_tabs_{self._runtime_id}"
        self._toolbar_id = f"viz_toolbar_{self._runtime_id}"
        self._texture_registry_id = f"viz_tex_registry_{self._runtime_id}"

        self._tabs: List[VisualizationTab] = []
        self._active_tab: Optional[VisualizationTab] = None
        self._update_operation: Optional[UpdateMonitor] = None
        self._last_tab_count: int = 0  # Track when tabs change
        self._needs_redraw: bool = False  # Flag for when redraw is needed
        self._options_popup_tab: Optional[VisualizationTab] = None  # Track which tab has popup open

        # Create persistent texture registry
        if not dpg.does_item_exist(self._texture_registry_id):
            dpg.add_texture_registry(tag=self._texture_registry_id)

    async def initialize_gui(self) -> None:
        """Initialize visualization workspace and subscribe to events."""
        self._logger.debug("Initializing VisualizationWorkspace")

        notification_bus.subscribe("operation_complete", self._on_operation_complete)
        notification_bus.subscribe("create_visualization", self._on_create_visualization)
        notification_bus.subscribe("operation_selected", self._on_operation_selected)
        notification_bus.subscribe("memory_slot_selected", self._on_memory_slot_selected)

        self._update_operation = await self._operation_control.operation_manager.create_operation(
            operation_type=UpdateMonitor,
            name=f"viz_workspace_update_{self._runtime_id}",
            action=self._update_async
        )
        self._update_operation.is_ready = True

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        """Resize the visualization workspace."""
        self.width = new_width
        self.height = new_height

        if dpg.does_item_exist(self._workspace_id):
            dpg.set_item_width(self._workspace_id, new_width)
            dpg.set_item_height(self._workspace_id, new_height)

    def draw(self) -> None:
        """Draw the visualization workspace interface."""
        with dpg.child_window(tag=self._workspace_id, parent=self._parent,
                             width=self.width, height=self.height, border=False):
            self._draw_tab_area()

    def _draw_tab_area(self) -> None:
        """Draw the tabbed visualization area."""
        # Save currently active tab before redrawing
        current_active_tab_id = None
        if dpg.does_item_exist(self._tab_bar_id):
            try:
                current_active_tab_id = dpg.get_value(self._tab_bar_id)
            except:
                pass
            # Delete all individual tab items first to avoid alias conflicts
            for tab in self._tabs:
                if dpg.does_item_exist(tab.tab_id):
                    dpg.delete_item(tab.tab_id)
            dpg.delete_item(self._tab_bar_id)

        empty_state_id = f"{self._workspace_id}_empty_state"

        if not self._tabs:
            self._draw_empty_state()
            return

        # Clean up empty state if it exists (tabs are now present)
        if dpg.does_item_exist(empty_state_id):
            dpg.delete_item(empty_state_id)

        with dpg.tab_bar(tag=self._tab_bar_id, parent=self._workspace_id,
                         reorderable=True):
            for tab in self._tabs:
                self._draw_tab(tab)

        # Restore previously active tab or use current active_tab
        if current_active_tab_id and dpg.does_item_exist(current_active_tab_id):
            dpg.set_value(self._tab_bar_id, current_active_tab_id)
        elif self._active_tab and dpg.does_item_exist(self._active_tab.tab_id):
            dpg.set_value(self._tab_bar_id, self._active_tab.tab_id)

    def _draw_empty_state(self) -> None:
        """Draw empty state when no visualizations exist."""
        if not dpg.does_item_exist(self._workspace_id):
            return

        # Use unique tag and clean up before redrawing to prevent spam
        empty_state_id = f"{self._workspace_id}_empty_state"
        if dpg.does_item_exist(empty_state_id):
            return  # Already drawn, don't redraw

        with dpg.group(tag=empty_state_id, parent=self._workspace_id):
            dpg.add_spacer(height=100)
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=50)
                with dpg.group():
                    dpg.add_text("No visualizations yet", color=(128, 128, 128))
                    dpg.add_text("Visualizations will appear here when operations complete or when selected from memory slots (below).",
                               color=(128, 128, 128))

    def _draw_tab(self, tab: VisualizationTab) -> None:
        """Draw a single visualization tab."""
        tab_label = f"{'[PIN] ' if tab.is_pinned else ''}{tab.title}"

        with dpg.tab(label=tab_label, tag=tab.tab_id, closable=True, order_mode=dpg.mvTabOrder_Leading):
            self._draw_tab_content(tab)

    def _draw_tab_content(self, tab: VisualizationTab) -> None:
        """Draw the content of a visualization tab."""
        if tab.data is None:
            dpg.add_text("No data available", color=(128, 128, 128))
            return

        # Check if data is DataFrame and extract numeric columns
        import pandas as pd
        import numpy as np

        if isinstance(tab.data, pd.DataFrame):
            self._logger.debug(f"DataFrame with columns: {tab.data.columns.tolist()}")
            if tab.numeric_columns is None:
                tab.numeric_columns = tab.data.select_dtypes(include=[np.number]).columns.tolist()

            # Default to all numeric columns if nothing selected
            if tab.selected_columns is None and tab.numeric_columns:
                tab.selected_columns = tab.numeric_columns

        # Get data to visualize (filtered by selected columns if applicable)
        viz_data = tab.data
        if isinstance(tab.data, pd.DataFrame) and tab.selected_columns:
            # Build list of columns to include: Y columns + X column (if specified)
            columns_to_include = list(tab.selected_columns)

            # Always include the X column if it's a real column (not Index)
            x_column = tab.custom_options.get('x_column')
            if x_column and x_column in tab.data.columns and x_column not in columns_to_include:
                columns_to_include.append(x_column)

            # Also check viz_config for x_column (fallback)
            if tab.viz_config:
                config_x = tab.viz_config.get('x_column')
                if config_x and config_x in tab.data.columns and config_x not in columns_to_include:
                    columns_to_include.append(config_x)

            viz_data = tab.data[columns_to_include]
            self._logger.debug(f"Filtered to columns: {columns_to_include}")
            self._logger.debug(f"Filtered data dtypes: {viz_data.dtypes.to_dict()}")

        # Detect visualization type if not already done
        if not tab.viz_config:
            tab.viz_config = VisualizationDetector.detect_visualization_type(viz_data)
            tab.viz_type = tab.viz_config.get('primary_viz', 'auto')
            self._logger.debug(f"Detected viz type: {tab.viz_type} for data shape: {getattr(viz_data, 'shape', 'N/A')}")

        # Render visualization if not already rendered
        if not tab.rendered_image:
            try:
                # Use custom dimensions if set, otherwise use default workspace-based dimensions
                render_width = tab.custom_options.get('chart_width') or int(self.width - 250)
                render_height = tab.custom_options.get('chart_height') or int(self.height - 110)

                render_result = VisualizationRenderer.render(
                    viz_data,
                    tab.viz_config,
                    width=render_width,
                    height=render_height,
                    custom_options=tab.custom_options
                )
                tab.rendered_image = render_result['image_data']
                tab.figure = render_result['figure']

                # Create texture immediately after rendering
                if tab.rendered_image:
                    import base64
                    image_bytes = base64.b64decode(tab.rendered_image)
                    self._create_texture_from_bytes(tab, image_bytes)

            except Exception as e:
                self._logger.error(f"Visualization rendering failed for {tab.title}: {e}", self.__class__.__name__)
                dpg.add_text(f"Visualization failed: {str(e)}", color=(255, 100, 100), wrap=self.width - 40)
                return

        # Wrap everything in a child_window for proper containment
        with dpg.child_window(width=-1, height=-1, border=False, horizontal_scrollbar=True):
            # Store all columns for the tab if DataFrame
            if isinstance(tab.data, pd.DataFrame) and tab.all_columns is None:
                tab.all_columns = tab.data.columns.tolist()

            # Visualization controls - single row with type display and options button
            with dpg.group(horizontal=True):
                # Show current chart type
                chart_type_display = tab.viz_type.replace('_', ' ').title()
                dpg.add_text(f"Chart: {chart_type_display}", color=(150, 150, 150))

                dpg.add_spacer(width=20)

                # Visualization Options button
                dpg.add_button(
                    label="Visualization Options",
                    callback=lambda s, a, u: self._show_viz_options_popup(u),
                    user_data=tab
                )
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Configure chart type, axis labels, columns, and filters")

                dpg.add_spacer(width=10)

                # Export PNG button
                dpg.add_button(
                    label="Export PNG",
                    callback=lambda s, a, u: self._export_png_for_tab(u),
                    user_data=tab
                )
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Export visualization as PNG to project exports folder")

            dpg.add_spacer(height=10)

            # Display the visualization image
            if tab.texture_id and dpg.does_item_exist(tab.texture_id):
                img_width = getattr(tab, 'image_width', 600)
                img_height = getattr(tab, 'image_height', 400)
                dpg.add_image(tab.texture_id, width=img_width, height=img_height)
            elif tab.rendered_image:
                dpg.add_text("Loading visualization...", color=(200, 200, 100))
            else:
                dpg.add_text("Rendering visualization...", color=(200, 200, 100))

    def _export_png(self) -> None:
        """Export current visualization as PNG."""
        if self._active_tab is not None:
            self._export_png_for_tab(self._active_tab)
        else:
            self._logger.warning("No visualization to export")

    def _export_png_for_tab(self, tab: VisualizationTab) -> None:
        """Export a specific tab's visualization as PNG to the project exports folder."""
        if tab is None or tab.figure is None:
            self._logger.warning("No visualization to export")
            notification_bus.publish("data_ready", {
                "operation_name": "Export Visualization",
                "message": "No visualization available to export",
                "status": "warning"
            })
            return

        try:
            from research_analytics_suite.utils import Config
            import os
            from datetime import datetime

            config = Config()
            export_dir = config.repr_path(config.EXPORT_DIR)
            os.makedirs(export_dir, exist_ok=True)

            # Clean the title for use as filename
            clean_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in tab.title)
            clean_title = clean_title.replace(' ', '_')

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{clean_title}_{timestamp}.png"
            filepath = os.path.join(export_dir, filename)

            VisualizationRenderer.export_figure(tab.figure, filepath, format='png', dpi=300)

            self._logger.info(f"Exported visualization to {filepath}")

            notification_bus.publish("data_ready", {
                "operation_name": "Export Visualization",
                "message": f"Exported to {filename}",
                "file_path": filepath
            })

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)
            notification_bus.publish("data_ready", {
                "operation_name": "Export Visualization",
                "message": f"Export failed: {str(e)}",
                "status": "error"
            })

    def _on_operation_complete(self, data: Dict[str, Any]) -> None:
        """Handle operation completion by creating new visualization tab."""
        operation_name = data.get('operation_name', 'Unknown')
        tab_id = f"viz_tab_{data.get('operation_id', id(data))}"

        # Check if tab already exists to avoid duplicates
        existing_tab = next((tab for tab in self._tabs if tab.tab_id == tab_id), None)
        if existing_tab:
            self._active_tab = existing_tab
            self._logger.debug(f"Switched to existing visualization for {operation_name}")
            return

        new_tab = VisualizationTab(
            tab_id=tab_id,
            title=f"{operation_name} Results",
            data=data.get('result')
        )

        self._tabs.append(new_tab)
        self._active_tab = new_tab

        self._logger.debug(f"Created visualization tab for {operation_name}")

    def _on_create_visualization(self, data: Dict[str, Any]) -> None:
        """Handle explicit visualization request from notification action."""
        operation_name = data.get('operation_name', 'Unknown')
        tab_id = f"viz_tab_{data.get('operation_id', id(data))}"

        existing_tab = next((tab for tab in self._tabs if tab.tab_id == tab_id), None)
        if existing_tab:
            self._active_tab = existing_tab
            self._logger.debug(f"Switched to existing visualization for {operation_name}")
        else:
            new_tab = VisualizationTab(
                tab_id=tab_id,
                title=f"{operation_name} Results",
                data=data.get('result')
            )
            self._tabs.append(new_tab)
            self._active_tab = new_tab
            self._logger.debug(f"Created visualization tab from notification for {operation_name}")

    def _on_operation_selected(self, operation_id: str) -> None:
        """Handle operation selection by creating visualization tab for its inputs/outputs."""
        try:
            from research_analytics_suite.operation_manager.control import OperationControl
            from research_analytics_suite.data_engine.memory.MemoryManager import MemoryManager

            op_control = OperationControl()
            operation = op_control.operation_manager.get_operation(operation_id)

            if not operation or not hasattr(operation, 'attributes'):
                return

            attrs = operation.attributes
            memory_manager = MemoryManager()

            # Collect data from input/output slots
            viz_data = {}

            # Get input data
            if attrs.input_ids:
                for input_name, slot_id in attrs.input_ids.items():
                    slot = memory_manager.get_slot(slot_id)
                    if slot and slot.raw_data is not None:
                        viz_data[f"Input: {input_name}"] = slot.raw_data

            # Get output data
            if attrs.output_ids:
                for output_name, slot_id in attrs.output_ids.items():
                    slot = memory_manager.get_slot(slot_id)
                    if slot and slot.raw_data is not None:
                        viz_data[f"Output: {output_name}"] = slot.raw_data

            # Only create tab if there's data to visualize
            if not viz_data:
                self._logger.debug(f"No input/output data to visualize for operation {operation.name}")
                return

            # Create or switch to tab for this operation
            tab_id = f"viz_tab_op_{operation_id}"
            existing_tab = next((tab for tab in self._tabs if tab.tab_id == tab_id), None)

            if existing_tab:
                self._active_tab = existing_tab
                self._logger.debug(f"Switched to existing tab for operation {operation.name}")
            else:
                # If only one data item, use it directly; otherwise use dict
                data_to_viz = list(viz_data.values())[0] if len(viz_data) == 1 else viz_data

                new_tab = VisualizationTab(
                    tab_id=tab_id,
                    title=f"{operation.name} Data",
                    data=data_to_viz
                )
                self._tabs.append(new_tab)
                self._active_tab = new_tab
                self._logger.debug(f"Created visualization tab for operation {operation.name}")

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    def _on_memory_slot_selected(self, slot_id: str) -> None:
        """Handle memory slot selection by creating visualization tab for its data."""
        try:
            from research_analytics_suite.data_engine.memory.MemoryManager import MemoryManager

            memory_manager = MemoryManager()
            slot = memory_manager.get_slot(slot_id)

            if not slot or slot.raw_data is None:
                self._logger.debug(f"No data to visualize for slot {slot_id}")
                return

            # Create or switch to tab for this memory slot
            tab_id = f"viz_tab_slot_{slot_id}"
            existing_tab = next((tab for tab in self._tabs if tab.tab_id == tab_id), None)

            if existing_tab:
                self._active_tab = existing_tab
                self._logger.debug(f"Switched to existing tab for slot {slot.name}")
            else:
                new_tab = VisualizationTab(
                    tab_id=tab_id,
                    title=f"Slot: {slot.name}",
                    data=slot.raw_data
                )
                self._tabs.append(new_tab)
                self._active_tab = new_tab
                self._logger.info(f"Created visualization tab for memory slot {slot.name}")

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    def _create_texture_from_bytes(self, tab: VisualizationTab, image_bytes: bytes) -> None:
        """Create DearPyGui texture from PNG bytes using static texture (simpler method)."""
        try:
            import tempfile
            import os

            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            temp_file.write(image_bytes)
            temp_file.close()

            texture_id = f"{tab.tab_id}_texture"

            if dpg.does_item_exist(texture_id):
                dpg.delete_item(texture_id)

            # Load as static texture (much simpler!)
            width, height, channels, data = dpg.load_image(temp_file.name)

            self._logger.debug(f"Loaded image: {width}x{height}x{channels} channels")

            dpg.add_static_texture(
                width=width,
                height=height,
                default_value=data,
                tag=texture_id,
                parent=self._texture_registry_id
            )

            tab.texture_id = texture_id
            tab.image_width = width
            tab.image_height = height

            # Clean up temp file
            os.unlink(temp_file.name)

            self._logger.debug(f"Static texture created: {texture_id} ({width}x{height})")

        except Exception as e:
            self._logger.error(f"Texture creation error: {e}", self.__class__.__name__)

    def _close_figure(self, tab: VisualizationTab) -> None:
        """Safely close matplotlib figure to prevent memory leaks."""
        if tab.figure is not None:
            try:
                import matplotlib.pyplot as plt
                plt.close(tab.figure)
            except Exception:
                pass  # Ignore errors when closing figures
            tab.figure = None

    def _toggle_column(self, tab: VisualizationTab, column: str, checked: bool) -> None:
        """Toggle column selection for DataFrame visualization."""
        if tab.selected_columns is None:
            tab.selected_columns = []

        if checked and column not in tab.selected_columns:
            tab.selected_columns.append(column)
        elif not checked and column in tab.selected_columns:
            tab.selected_columns.remove(column)

        # Clear rendered image and viz_config to force re-detection and re-render with new columns
        tab.rendered_image = None
        self._close_figure(tab)  # Properly close matplotlib figure to prevent memory leak
        tab.viz_config = None  # Clear config so column references are re-detected
        if tab.texture_id and dpg.does_item_exist(tab.texture_id):
            dpg.delete_item(tab.texture_id)
            tab.texture_id = None

        self._needs_redraw = True
        self._logger.debug(f"Column {column} {'selected' if checked else 'deselected'} for {tab.title}")

    def _switch_viz_type(self, tab: VisualizationTab, new_viz_type: str) -> None:
        """Switch visualization type for a tab."""
        if not tab.viz_config:
            return

        # Update alternatives list: add old primary, remove new primary
        old_primary = tab.viz_config.get('primary_viz')
        alternatives = tab.viz_config.get('alternatives', [])

        if old_primary and old_primary not in alternatives:
            alternatives.append(old_primary)

        if new_viz_type in alternatives:
            alternatives.remove(new_viz_type)

        tab.viz_config['alternatives'] = alternatives
        tab.viz_config['primary_viz'] = new_viz_type
        tab.viz_type = new_viz_type
        tab.rendered_image = None
        self._close_figure(tab)  # Properly close matplotlib figure to prevent memory leak

        if tab.texture_id and dpg.does_item_exist(tab.texture_id):
            dpg.delete_item(tab.texture_id)
            tab.texture_id = None

        self._needs_redraw = True  # Request redraw for new viz type
        self._logger.debug(f"Switched {tab.title} to {new_viz_type}")

    def _show_viz_options_popup(self, tab: VisualizationTab) -> None:
        """Show visualization options popup window for a tab."""
        popup_id = f"viz_options_popup_{tab.tab_id}"

        # Close existing popup if open
        if dpg.does_item_exist(popup_id):
            dpg.delete_item(popup_id)

        self._options_popup_tab = tab

        # Create popup window
        with dpg.window(
            tag=popup_id,
            label=f"VIZ: {tab.title} Options",
            modal=True,
            width=450,
            height=500,
            no_resize=False,
            pos=[100, 100],
            on_close=lambda: self._close_viz_options_popup(popup_id)
        ):
            # Chart Type Section
            dpg.add_text("Chart Type", color=(200, 200, 255))
            dpg.add_spacer(height=5)

            # Get current chart type index
            current_type = tab.viz_type
            chart_type_labels = [ct[1] for ct in self.CHART_TYPES]
            chart_type_values = [ct[0] for ct in self.CHART_TYPES]
            current_index = chart_type_values.index(current_type) if current_type in chart_type_values else 0

            chart_type_combo_id = f"{popup_id}_chart_type"
            dpg.add_combo(
                items=chart_type_labels,
                default_value=chart_type_labels[current_index],
                tag=chart_type_combo_id,
                callback=lambda s, v, u: self._on_chart_type_changed(u['popup_id'], u['tab'], v),
                user_data={'popup_id': popup_id, 'tab': tab},
                width=300
            )

            dpg.add_spacer(height=15)
            dpg.add_separator()
            dpg.add_spacer(height=10)

            # Dynamic options container (changes based on chart type)
            options_container_id = f"{popup_id}_options_container"
            with dpg.group(tag=options_container_id):
                self._draw_chart_options(options_container_id, tab, current_type)

            dpg.add_spacer(height=20)
            dpg.add_separator()
            dpg.add_spacer(height=10)

            # Action buttons
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Apply",
                    callback=lambda s, a, u: self._apply_viz_options(u['popup_id'], u['tab']),
                    user_data={'popup_id': popup_id, 'tab': tab},
                    width=100
                )
                dpg.add_spacer(width=10)
                dpg.add_button(
                    label="Apply & Close",
                    callback=lambda s, a, u: self._apply_and_close_viz_options(u['popup_id'], u['tab']),
                    user_data={'popup_id': popup_id, 'tab': tab},
                    width=120
                )
                dpg.add_spacer(width=10)
                dpg.add_button(
                    label="Cancel",
                    callback=lambda s, a, u: self._close_viz_options_popup(u),
                    user_data=popup_id,
                    width=80
                )

    def _on_chart_type_changed(self, popup_id: str, tab: VisualizationTab, selected_label: str) -> None:
        """Handle chart type selection change - redraw options section."""
        # Map label back to chart type value
        chart_type_map = {ct[1]: ct[0] for ct in self.CHART_TYPES}
        new_chart_type = chart_type_map.get(selected_label, 'line')

        # Redraw the options container
        options_container_id = f"{popup_id}_options_container"
        if dpg.does_item_exist(options_container_id):
            dpg.delete_item(options_container_id, children_only=True)
            self._draw_chart_options(options_container_id, tab, new_chart_type)

    def _draw_chart_options(self, container_id: str, tab: VisualizationTab, chart_type: str) -> None:
        """Draw chart-specific options in the container."""
        import pandas as pd

        opts = tab.custom_options

        with dpg.group(parent=container_id):
            # Common options for all chart types
            dpg.add_text("Labels & Title", color=(200, 200, 255))
            dpg.add_spacer(height=5)

            # Custom title
            dpg.add_input_text(
                label="Chart Title",
                tag=f"{container_id}_title",
                default_value=opts.get('title') or '',
                hint="Leave empty for auto-generated title",
                width=300
            )

            # X and Y axis labels (for applicable charts)
            if chart_type not in ['pie', 'text']:
                dpg.add_input_text(
                    label="X-Axis Label",
                    tag=f"{container_id}_x_label",
                    default_value=opts.get('x_label') or '',
                    hint="Leave empty for auto",
                    width=300
                )
                dpg.add_input_text(
                    label="Y-Axis Label",
                    tag=f"{container_id}_y_label",
                    default_value=opts.get('y_label') or '',
                    hint="Leave empty for auto",
                    width=300
                )

            dpg.add_spacer(height=15)

            # Chart-type specific options
            if chart_type in ['line', 'scatter', 'area']:
                self._draw_line_scatter_options(container_id, tab, chart_type)
            elif chart_type == 'bar':
                self._draw_bar_options(container_id, tab)
            elif chart_type == 'histogram':
                self._draw_histogram_options(container_id, tab)
            elif chart_type == 'box':
                self._draw_box_options(container_id, tab)
            elif chart_type in ['heatmap', 'correlation_heatmap']:
                self._draw_heatmap_options(container_id, tab)
            elif chart_type == 'pie':
                self._draw_pie_options(container_id, tab)

            dpg.add_spacer(height=15)

            # Display options (grid, legend)
            dpg.add_text("Display Options", color=(200, 200, 255))
            dpg.add_spacer(height=5)

            dpg.add_checkbox(
                label="Show Grid",
                tag=f"{container_id}_show_grid",
                default_value=opts.get('show_grid', True)
            )

            if chart_type in ['line', 'scatter', 'area', 'bar']:
                dpg.add_checkbox(
                    label="Show Legend",
                    tag=f"{container_id}_show_legend",
                    default_value=opts.get('show_legend', True)
                )

            # Transparency slider
            dpg.add_slider_float(
                label="Opacity",
                tag=f"{container_id}_alpha",
                default_value=opts.get('alpha', 0.7),
                min_value=0.1,
                max_value=1.0,
                width=200
            )

            dpg.add_spacer(height=10)

            # Chart size options
            dpg.add_text("Chart Size", color=(200, 200, 255))
            dpg.add_spacer(height=5)

            # Get current dimensions from custom_options, tab attributes, or calculate defaults
            default_width = opts.get('chart_width') or getattr(tab, 'image_width', None) or int(self.width - 250)
            default_height = opts.get('chart_height') or getattr(tab, 'image_height', None) or int(self.height - 110)

            dpg.add_input_int(
                label="Plot Width",
                tag=f"{container_id}_chart_width",
                default_value=default_width,
                min_value=200,
                max_value=2000,
                step=50,
                width=100
            )
            dpg.add_spacer(width=20)
            dpg.add_input_int(
                label="Plot Height",
                tag=f"{container_id}_chart_height",
                default_value=default_height,
                min_value=150,
                max_value=1500,
                step=50,
                width=100
            )

    def _draw_line_scatter_options(self, container_id: str, tab: VisualizationTab, chart_type: str) -> None:
        """Draw options specific to line, scatter, and area charts."""
        import pandas as pd

        opts = tab.custom_options
        dpg.add_text("Data Selection", color=(200, 200, 255))
        dpg.add_spacer(height=5)

        # Column selection for DataFrames
        if isinstance(tab.data, pd.DataFrame) and tab.all_columns:
            all_cols = tab.all_columns
            numeric_cols = tab.numeric_columns or []

            # X Column selection
            x_options = ['(Index)'] + all_cols
            current_x = opts.get('x_column') or tab.viz_config.get('x_column') or '(Index)'
            y_columns_container_id = f"{container_id}_y_columns_container"

            dpg.add_combo(
                items=x_options,
                label="X Column",
                tag=f"{container_id}_x_column",
                default_value=current_x if current_x in x_options else '(Index)',
                width=200,
                callback=lambda s, v, u: self._on_x_column_changed(u['container_id'], u['tab'], v),
                user_data={'container_id': container_id, 'tab': tab}
            )

            # Y Columns selection (multi-select via checkboxes)
            dpg.add_spacer(height=5)
            dpg.add_text("Y Columns:", color=(150, 150, 150))

            current_y_cols = opts.get('y_columns') or tab.selected_columns or numeric_cols
            # Remove X column from Y columns if present
            if current_x and current_x != '(Index)' and current_x in current_y_cols:
                current_y_cols = [c for c in current_y_cols if c != current_x]

            with dpg.group(tag=y_columns_container_id):
                self._draw_y_column_checkboxes(container_id, tab, all_cols, numeric_cols, current_y_cols, current_x)

        dpg.add_spacer(height=10)

        # Style options
        dpg.add_text("Style", color=(200, 200, 255))
        dpg.add_spacer(height=5)

        if chart_type == 'scatter':
            dpg.add_slider_int(
                label="Marker Size",
                tag=f"{container_id}_marker_size",
                default_value=opts.get('marker_size', 20),
                min_value=5,
                max_value=100,
                width=200
            )
        elif chart_type in ['line', 'area']:
            line_style_labels = [ls[1] for ls in self.LINE_STYLES]
            current_style = opts.get('line_style', '-')
            style_index = next((i for i, ls in enumerate(self.LINE_STYLES) if ls[0] == current_style), 0)

            dpg.add_combo(
                items=line_style_labels,
                label="Line Style",
                tag=f"{container_id}_line_style",
                default_value=line_style_labels[style_index],
                width=150
            )

    def _draw_y_column_checkboxes(self, container_id: str, tab: VisualizationTab,
                                   all_cols: list, numeric_cols: list,
                                   current_y_cols: list, current_x: str) -> None:
        """Draw Y column checkboxes, disabling the one that matches X column."""
        for col in all_cols:
            is_numeric = col in numeric_cols
            is_selected = col in current_y_cols
            is_x_column = (col == current_x)
            checkbox_tag = f"{container_id}_ycol_{col}"

            with dpg.group(horizontal=True):
                # Disable checkbox if this column is the X column
                dpg.add_checkbox(
                    label=col,
                    tag=checkbox_tag,
                    default_value=is_selected and not is_x_column,
                    enabled=not is_x_column
                )
                if is_x_column:
                    dpg.add_text("(X axis)", color=(150, 150, 150))
                elif is_numeric:
                    dpg.add_text("(numeric)", color=(100, 200, 100))
                else:
                    dpg.add_text("(non-numeric)", color=(200, 100, 100))

    def _on_x_column_changed(self, container_id: str, tab: VisualizationTab, new_x_value: str) -> None:
        """Handle X column selection change - update Y columns to disable the selected X."""
        y_columns_container_id = f"{container_id}_y_columns_container"

        if not dpg.does_item_exist(y_columns_container_id):
            return

        all_cols = tab.all_columns or []
        numeric_cols = tab.numeric_columns or []

        # Get currently selected Y columns before redraw
        current_y_cols = []
        for col in all_cols:
            checkbox_tag = f"{container_id}_ycol_{col}"
            if dpg.does_item_exist(checkbox_tag):
                if dpg.get_value(checkbox_tag):
                    current_y_cols.append(col)

        # Remove the new X column from Y columns if it was selected
        if new_x_value and new_x_value != '(Index)' and new_x_value in current_y_cols:
            current_y_cols.remove(new_x_value)

        # Redraw the Y columns container - use push/pop to set correct parent context
        dpg.delete_item(y_columns_container_id, children_only=True)
        dpg.push_container_stack(y_columns_container_id)
        try:
            self._draw_y_column_checkboxes(container_id, tab, all_cols, numeric_cols, current_y_cols, new_x_value)
        finally:
            dpg.pop_container_stack()

    def _draw_bar_options(self, container_id: str, tab: VisualizationTab) -> None:
        """Draw options specific to bar charts."""
        import pandas as pd

        opts = tab.custom_options
        dpg.add_text("Data Selection", color=(200, 200, 255))
        dpg.add_spacer(height=5)

        if isinstance(tab.data, pd.DataFrame) and tab.all_columns:
            all_cols = tab.all_columns
            numeric_cols = tab.numeric_columns or []

            # Category column selection
            current_cat = opts.get('category_column') or tab.viz_config.get('category_column')
            dpg.add_combo(
                items=all_cols,
                label="Category Column",
                tag=f"{container_id}_category_column",
                default_value=current_cat if current_cat in all_cols else (all_cols[0] if all_cols else ''),
                width=200
            )

            # Value column selection
            current_val = opts.get('value_columns') or tab.viz_config.get('value_columns', [])
            if isinstance(current_val, list) and current_val:
                current_val = current_val[0]
            dpg.add_combo(
                items=numeric_cols,
                label="Value Column",
                tag=f"{container_id}_value_column",
                default_value=current_val if current_val in numeric_cols else (numeric_cols[0] if numeric_cols else ''),
                width=200
            )

            dpg.add_spacer(height=10)

            # Aggregation method
            dpg.add_text("Aggregation", color=(200, 200, 255))
            dpg.add_spacer(height=5)
            current_agg = opts.get('aggregation', 'mean')
            dpg.add_combo(
                items=self.AGGREGATIONS,
                label="Method",
                tag=f"{container_id}_aggregation",
                default_value=current_agg,
                width=150
            )

    def _draw_histogram_options(self, container_id: str, tab: VisualizationTab) -> None:
        """Draw options specific to histograms."""
        import pandas as pd

        opts = tab.custom_options
        dpg.add_text("Data Selection", color=(200, 200, 255))
        dpg.add_spacer(height=5)

        if isinstance(tab.data, pd.DataFrame):
            numeric_cols = tab.numeric_columns or []
            current_col = opts.get('column') or tab.viz_config.get('column')

            dpg.add_combo(
                items=numeric_cols,
                label="Column",
                tag=f"{container_id}_column",
                default_value=current_col if current_col in numeric_cols else (numeric_cols[0] if numeric_cols else ''),
                width=200
            )

        dpg.add_spacer(height=10)
        dpg.add_text("Histogram Settings", color=(200, 200, 255))
        dpg.add_spacer(height=5)

        dpg.add_slider_int(
            label="Number of Bins",
            tag=f"{container_id}_bins",
            default_value=opts.get('bins', 30),
            min_value=5,
            max_value=100,
            width=200
        )

    def _draw_box_options(self, container_id: str, tab: VisualizationTab) -> None:
        """Draw options specific to box plots."""
        import pandas as pd

        opts = tab.custom_options
        dpg.add_text("Data Selection", color=(200, 200, 255))
        dpg.add_spacer(height=5)

        if isinstance(tab.data, pd.DataFrame):
            numeric_cols = tab.numeric_columns or []
            current_col = opts.get('column') or tab.viz_config.get('column')

            dpg.add_combo(
                items=numeric_cols,
                label="Column",
                tag=f"{container_id}_column",
                default_value=current_col if current_col in numeric_cols else (numeric_cols[0] if numeric_cols else ''),
                width=200
            )

    def _draw_heatmap_options(self, container_id: str, tab: VisualizationTab) -> None:
        """Draw options specific to heatmaps."""
        opts = tab.custom_options
        dpg.add_text("Color Settings", color=(200, 200, 255))
        dpg.add_spacer(height=5)

        current_cmap = opts.get('color_map', 'viridis')
        dpg.add_combo(
            items=self.COLOR_MAPS,
            label="Color Map",
            tag=f"{container_id}_color_map",
            default_value=current_cmap,
            width=200
        )

    def _draw_pie_options(self, container_id: str, tab: VisualizationTab) -> None:
        """Draw options specific to pie charts."""
        # Pie charts have minimal customization in this implementation
        dpg.add_text("Pie charts use dictionary keys as labels", color=(150, 150, 150))
        dpg.add_text("and values as proportions.", color=(150, 150, 150))

    def _apply_viz_options(self, popup_id: str, tab: VisualizationTab) -> None:
        """Apply visualization options without closing the popup."""
        self._collect_and_apply_options(popup_id, tab)

    def _apply_and_close_viz_options(self, popup_id: str, tab: VisualizationTab) -> None:
        """Apply visualization options and close the popup."""
        self._collect_and_apply_options(popup_id, tab)
        self._close_viz_options_popup(popup_id)

    def _collect_and_apply_options(self, popup_id: str, tab: VisualizationTab) -> None:
        """Collect options from popup and apply them to the tab."""
        opts = tab.custom_options
        container_id = f"{popup_id}_options_container"

        # Get chart type
        chart_type_combo = f"{popup_id}_chart_type"
        if dpg.does_item_exist(chart_type_combo):
            selected_label = dpg.get_value(chart_type_combo)
            chart_type_map = {ct[1]: ct[0] for ct in self.CHART_TYPES}
            new_chart_type = chart_type_map.get(selected_label, tab.viz_type)
        else:
            new_chart_type = tab.viz_type

        # Common options
        title_tag = f"{container_id}_title"
        if dpg.does_item_exist(title_tag):
            title = dpg.get_value(title_tag)
            opts['title'] = title if title.strip() else None

        x_label_tag = f"{container_id}_x_label"
        if dpg.does_item_exist(x_label_tag):
            x_label = dpg.get_value(x_label_tag)
            opts['x_label'] = x_label if x_label.strip() else None

        y_label_tag = f"{container_id}_y_label"
        if dpg.does_item_exist(y_label_tag):
            y_label = dpg.get_value(y_label_tag)
            opts['y_label'] = y_label if y_label.strip() else None

        # Display options
        grid_tag = f"{container_id}_show_grid"
        if dpg.does_item_exist(grid_tag):
            opts['show_grid'] = dpg.get_value(grid_tag)

        legend_tag = f"{container_id}_show_legend"
        if dpg.does_item_exist(legend_tag):
            opts['show_legend'] = dpg.get_value(legend_tag)

        alpha_tag = f"{container_id}_alpha"
        if dpg.does_item_exist(alpha_tag):
            opts['alpha'] = dpg.get_value(alpha_tag)

        # Chart size options
        width_tag = f"{container_id}_chart_width"
        if dpg.does_item_exist(width_tag):
            opts['chart_width'] = dpg.get_value(width_tag)

        height_tag = f"{container_id}_chart_height"
        if dpg.does_item_exist(height_tag):
            opts['chart_height'] = dpg.get_value(height_tag)

        # Chart-specific options
        if new_chart_type in ['line', 'scatter', 'area']:
            # X column
            x_col_tag = f"{container_id}_x_column"
            x_col = None
            if dpg.does_item_exist(x_col_tag):
                x_col = dpg.get_value(x_col_tag)
                opts['x_column'] = None if x_col == '(Index)' else x_col

            # Y columns (collect from checkboxes, excluding X column)
            if tab.all_columns:
                y_cols = []
                for col in tab.all_columns:
                    # Skip the X column - it shouldn't be in Y columns
                    if x_col and x_col != '(Index)' and col == x_col:
                        continue
                    checkbox_tag = f"{container_id}_ycol_{col}"
                    if dpg.does_item_exist(checkbox_tag) and dpg.get_value(checkbox_tag):
                        y_cols.append(col)
                opts['y_columns'] = y_cols if y_cols else None
                tab.selected_columns = y_cols if y_cols else [c for c in tab.numeric_columns if c != x_col]

            # Style
            marker_tag = f"{container_id}_marker_size"
            if dpg.does_item_exist(marker_tag):
                opts['marker_size'] = dpg.get_value(marker_tag)

            line_style_tag = f"{container_id}_line_style"
            if dpg.does_item_exist(line_style_tag):
                style_label = dpg.get_value(line_style_tag)
                style_map = {ls[1]: ls[0] for ls in self.LINE_STYLES}
                opts['line_style'] = style_map.get(style_label, '-')

        elif new_chart_type == 'bar':
            cat_tag = f"{container_id}_category_column"
            if dpg.does_item_exist(cat_tag):
                opts['category_column'] = dpg.get_value(cat_tag)

            val_tag = f"{container_id}_value_column"
            if dpg.does_item_exist(val_tag):
                val = dpg.get_value(val_tag)
                opts['value_columns'] = [val] if val else None

            agg_tag = f"{container_id}_aggregation"
            if dpg.does_item_exist(agg_tag):
                opts['aggregation'] = dpg.get_value(agg_tag)

        elif new_chart_type == 'histogram':
            col_tag = f"{container_id}_column"
            if dpg.does_item_exist(col_tag):
                opts['column'] = dpg.get_value(col_tag)

            bins_tag = f"{container_id}_bins"
            if dpg.does_item_exist(bins_tag):
                opts['bins'] = dpg.get_value(bins_tag)

        elif new_chart_type == 'box':
            col_tag = f"{container_id}_column"
            if dpg.does_item_exist(col_tag):
                opts['column'] = dpg.get_value(col_tag)

        elif new_chart_type in ['heatmap', 'correlation_heatmap']:
            cmap_tag = f"{container_id}_color_map"
            if dpg.does_item_exist(cmap_tag):
                opts['color_map'] = dpg.get_value(cmap_tag)

        # Apply chart type change if different
        if new_chart_type != tab.viz_type:
            self._switch_viz_type(tab, new_chart_type)
        else:
            # Just re-render with new options
            tab.rendered_image = None
            self._close_figure(tab)  # Properly close matplotlib figure to prevent memory leak
            if tab.texture_id and dpg.does_item_exist(tab.texture_id):
                dpg.delete_item(tab.texture_id)
                tab.texture_id = None
            self._needs_redraw = True

        self._logger.debug(f"Applied viz options for {tab.title}: type={new_chart_type}")

    def _close_viz_options_popup(self, popup_id: str) -> None:
        """Close the visualization options popup."""
        if dpg.does_item_exist(popup_id):
            dpg.delete_item(popup_id)
        self._options_popup_tab = None

    async def _update_async(self) -> None:
        """Async update loop - only redraw when tabs change."""
        while self._update_operation and self._update_operation.is_ready:
            if dpg.does_item_exist(self._workspace_id):
                # Only redraw if tab count changed or explicit redraw requested
                current_tab_count = len(self._tabs)
                if current_tab_count != self._last_tab_count or self._needs_redraw:
                    self._draw_tab_area()
                    self._last_tab_count = current_tab_count
                    self._needs_redraw = False
            await asyncio.sleep(1.0)

    async def cleanup(self) -> None:
        """Cleanup resources when workspace is destroyed."""
        if self._update_operation:
            await self._update_operation.stop()

        self._logger.debug("VisualizationWorkspace cleanup completed")

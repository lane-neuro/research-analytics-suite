"""
OperationDetailPanel Module

This module provides a comprehensive detail panel for viewing and editing operation attributes
with a clean tabbed interface.

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
from copy import copy
from typing import Optional

import dearpygui.dearpygui as dpg

from research_analytics_suite.commands.utils.text_utils import get_function_body
from research_analytics_suite.data_engine import MemoryManager
from research_analytics_suite.gui.GUIBase import GUIBase
from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation
from research_analytics_suite.operation_manager.operations.core.OperationAttributes import OperationAttributes
from research_analytics_suite.operation_manager.operations.system.UpdateMonitor import UpdateMonitor


class OperationDetailPanel(GUIBase):
    """
    Detailed operation viewer and editor panel.

    Provides comprehensive interface for viewing and modifying operation attributes,
    managing inputs/outputs, and controlling execution.
    """

    def __init__(self, width: int, height: int, parent: str):
        """
        Initialize the OperationDetailPanel.

        Args:
            width (int): Width of the detail panel
            height (int): Height of the detail panel
            parent (str): Parent container ID
        """
        super().__init__(width, height, parent)
        self._panel_id = f"detail_panel_{self._runtime_id}"
        self._tab_bar_id = f"detail_tabs_{self._runtime_id}"

        self._current_operation: Optional[BaseOperation] = None
        self._original_attributes: Optional[OperationAttributes] = None
        self._last_rendered_operation: Optional[BaseOperation] = None

        self._update_operation: Optional[BaseOperation] = None

        self.VIEW_MODE_SIMPLIFIED = 0
        self.VIEW_MODE_ADVANCED = 1
        self._view_mode: int = self.VIEW_MODE_SIMPLIFIED

        self._last_input_ids: Optional[dict] = None
        self._last_output_ids: Optional[dict] = None

    async def initialize_gui(self) -> None:
        """Initialize GUI components and update monitoring."""
        self._logger.debug("Initializing OperationDetailPanel")

        # Create update monitor
        self._update_operation = await self._operation_control.operation_manager.create_operation(
            operation_type=UpdateMonitor,
            name=f"detail_update_{self._runtime_id}",
            action=self._update_async
        )
        self._update_operation.is_ready = True

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        """Resize the detail panel and re-render content."""
        self.width = new_width
        self.height = new_height
        if dpg.does_item_exist(self._panel_id):
            dpg.set_item_width(self._panel_id, new_width)
            dpg.set_item_height(self._panel_id, new_height)
            if self._current_operation:
                self._render_operation_details(self._current_operation)

    def draw(self) -> None:
        """Draw the detail panel interface."""
        with dpg.child_window(tag=self._panel_id,
                             parent=self._parent,
                             width=self.width,
                             height=self.height,
                             border=False):
            self._draw_panel_content()

    def _draw_panel_content(self) -> None:
        """Draw the panel content (separated to avoid container issues)."""
        if not self._current_operation:
            self._draw_empty_state()
            return

        self._draw_operation_header()

        dpg.add_separator()

        if self._view_mode == self.VIEW_MODE_SIMPLIFIED:
            self._draw_simplified_view()
        else:
            tab_bar_tag = f"{self._tab_bar_id}_{id(self._current_operation)}"
            with dpg.tab_bar(tag=tab_bar_tag):
                with dpg.tab(label="Overview"):
                    self._draw_overview_tab()

                with dpg.tab(label="Inputs/Outputs"):
                    self._draw_io_tab()

                with dpg.tab(label="Code & Execution"):
                    self._draw_execution_tab()

                with dpg.tab(label="Settings"):
                    self._draw_settings_tab()

    def _draw_empty_state(self) -> None:
        """Draw empty state when no operation is selected."""
        dpg.add_spacer(height=100)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=50)
            dpg.add_text("Select an operation from the tree to view details",
                        color=(128, 128, 128))

    def _draw_simplified_view(self) -> None:
        """Draw simplified single-screen view with all essential information."""
        if not self._current_operation:
            return

        attrs = self._current_operation.attributes if hasattr(self._current_operation, 'attributes') else None
        if not attrs:
            dpg.add_text("No attributes available")
            return

        dpg.add_text("Description:", color=(200, 200, 200))
        dpg.add_text(attrs.description, wrap=self.width - 60)

        dpg.add_spacer(height=10)

        with dpg.group(horizontal=True):
            panel_width = max(200, int((self.width - 80) / 2))

            with dpg.child_window(width=panel_width, height=150, border=True):
                dpg.add_text("Required Inputs", color=(100, 200, 255))
                dpg.add_separator()

                input_ids = attrs.input_ids
                if input_ids:
                    for name, slot_id in input_ids.items():
                        with dpg.group(horizontal=True):
                            dpg.add_text(f"{name}:")
                            dpg.add_text(str(slot_id), color=(180, 180, 180))

                        dpg.add_button(
                            label=f"View {name}",
                            width=-1,
                            callback=(lambda captured_slot_id: lambda: self._view_memory_slot(captured_slot_id))(slot_id)
                        )
                        dpg.add_spacer(height=5)
                else:
                    dpg.add_text("No inputs defined", color=(128, 128, 128))

            dpg.add_spacer(width=10)

            with dpg.child_window(width=panel_width, height=150, border=True):
                dpg.add_text("Outputs", color=(255, 200, 100))
                dpg.add_separator()

                output_ids = attrs.output_ids
                if output_ids:
                    for name, slot_id in output_ids.items():
                        with dpg.group(horizontal=True):
                            dpg.add_text(f"{name}:")
                            dpg.add_text(str(slot_id), color=(180, 180, 180))

                        dpg.add_button(
                            label=f"View {name}",
                            width=-1,
                            callback=(lambda captured_slot_id: lambda: self._view_memory_slot(captured_slot_id))(slot_id)
                        )
                        dpg.add_spacer(height=5)
                else:
                    dpg.add_text("No outputs defined", color=(128, 128, 128))

        dpg.add_spacer(height=10)

        dpg.add_text("Settings:", color=(200, 200, 200))
        dpg.add_separator()

        with dpg.group(horizontal=True, horizontal_spacing=20):
            op_id = id(self._current_operation)
            dpg.add_checkbox(
                label="Manages own loop",
                default_value=attrs.is_loop,
                callback=lambda s, v: self._update_setting('is_loop', v),
                tag=f"loop_setting_{self._runtime_id}_{op_id}_simple"
            )
            with dpg.tooltip(f"loop_setting_{self._runtime_id}_{op_id}_simple"):
                dpg.add_text("Enable if this operation implements its own internal loop")
                dpg.add_text("(e.g., while self.is_loop: ...)")
                dpg.add_text("The operation will remain in 'running' state until stopped")

            dpg.add_checkbox(
                label="Run in parallel",
                default_value=attrs.parallel,
                callback=lambda s, v: self._update_setting('parallel', v),
                tag=f"parallel_setting_{self._runtime_id}_{op_id}_simple"
            )

        dpg.add_spacer(height=10)

        with dpg.group(horizontal=True, horizontal_spacing=10):
            dpg.add_button(
                label="Save Settings",
                callback=lambda: self._save_operation_settings()
            )

            dpg.add_button(
                label="View Results",
                callback=lambda: asyncio.create_task(self._view_results())
            )

    def _draw_operation_header(self) -> None:
        """Draw operation header with name, status, and quick actions."""
        if not self._current_operation:
            return

        attrs = self._current_operation.attributes if hasattr(self._current_operation, 'attributes') else None

        with dpg.group(horizontal=True, horizontal_spacing=20):
            with dpg.group():
                name = attrs.name if attrs else self._current_operation.name
                version = f" v{attrs.version}" if attrs and hasattr(attrs, 'version') else ""
                dpg.add_text(f"{name}{version}", color=(255, 255, 255))

                if self._view_mode == self.VIEW_MODE_ADVANCED:
                    author = attrs.author if attrs else "Unknown"
                    runtime_id = self._current_operation.runtime_id[-8:]
                    dpg.add_text(f"by {author} | ID: {runtime_id}", color=(180, 180, 180))

            dpg.add_spacer(width=20)

            with dpg.group():
                status = self._current_operation.status
                status_color = self._get_status_color(status)
                dpg.add_text(f"Status: {status}", color=status_color)

                with dpg.group(horizontal=True, horizontal_spacing=10):
                    if status in ["ready", "waiting", "idle", "started"]:
                        dpg.add_button(
                            label="Execute",
                            callback=lambda: asyncio.create_task(self._execute_operation())
                        )
                    elif status == "running":
                        dpg.add_button(
                            label="Stop",
                            callback=lambda: asyncio.create_task(self._stop_operation())
                        )

                    dpg.add_button(
                        label="Reset",
                        callback=lambda: asyncio.create_task(self._reset_operation())
                    )

            dpg.add_spacer(width=10)

            with dpg.group():
                dpg.add_text("View:", color=(180, 180, 180))
                dpg.add_radio_button(
                    items=["Simplified", "Advanced"],
                    default_value="Advanced" if self._view_mode == self.VIEW_MODE_ADVANCED else "Simplified",
                    horizontal=True,
                    callback=self._on_view_mode_changed,
                    tag=f"view_mode_toggle_{self._runtime_id}_{id(self._current_operation)}"
                )

    def _draw_overview_tab(self) -> None:
        """Draw overview tab with basic information."""
        if not self._current_operation:
            return

        attrs = self._current_operation.attributes if hasattr(self._current_operation, 'attributes') else None
        if not attrs:
            dpg.add_text("No attributes available")
            return

        with dpg.group():
            dpg.add_text("Description:", color=(200, 200, 200))
            dpg.add_text(attrs.description, wrap=self.width - 40)

            dpg.add_spacer(height=15)

            with dpg.group(horizontal=True):
                with dpg.group():
                    dpg.add_text("Category ID:", color=(200, 200, 200))
                    dpg.add_text(str(attrs.category_id))

                    dpg.add_spacer(height=10)

                    dpg.add_text("Email:", color=(200, 200, 200))
                    dpg.add_text(attrs.email)

                dpg.add_spacer(width=50)

                with dpg.group():
                    dpg.add_text("GitHub:", color=(200, 200, 200))
                    dpg.add_text(attrs.github)

                    dpg.add_spacer(height=10)

                    dpg.add_text("Active:", color=(200, 200, 200))
                    dpg.add_text("Yes" if attrs.active else "No")

            dpg.add_spacer(height=15)

            if attrs.inheritance:
                dpg.add_text("Inherited Operations:", color=(200, 200, 200))
                with dpg.group(indent=20):
                    for inherited in attrs.inheritance:
                        dpg.add_text(f"• {inherited}")

    def _draw_io_tab(self) -> None:
        """Draw inputs/outputs tab."""
        if not self._current_operation:
            return

        attrs = self._current_operation.attributes if hasattr(self._current_operation, 'attributes') else None
        if not attrs:
            dpg.add_text("No attributes available")
            return

        with dpg.child_window(border=False, width=-1, height=-1, horizontal_scrollbar=True):
            with dpg.group(horizontal=True):
                _width = dpg.get_item_width(self._panel_id)
                with dpg.child_window(width=150, height=-1, border=True):
                    dpg.add_text("Required Inputs", color=(100, 200, 255))
                    dpg.add_separator()

                    input_ids = attrs.input_ids
                    if input_ids:
                        for name, slot_id in input_ids.items():
                            with dpg.group(horizontal=True):
                                dpg.add_text(f"{name}:")
                                dpg.add_text(str(slot_id), color=(180, 180, 180))

                            dpg.add_button(
                                label=f"View {name}",
                                width=-1,
                                callback=(lambda captured_slot_id: lambda: self._view_memory_slot(captured_slot_id))(slot_id)
                            )
                            dpg.add_spacer(height=5)
                    else:
                        dpg.add_text("No inputs defined", color=(128, 128, 128))

                with dpg.child_window(width=150, height=-1, border=True):
                    dpg.add_text("Outputs", color=(255, 200, 100))
                    dpg.add_separator()

                    output_ids = attrs.output_ids
                    if output_ids:
                        for name, slot_id in output_ids.items():
                            with dpg.group(horizontal=True):
                                dpg.add_text(f"{name}:")
                                dpg.add_text(str(slot_id), color=(180, 180, 180))

                            dpg.add_button(
                                label=f"View {name}",
                                width=-1,
                                callback=(lambda captured_slot_id: lambda: self._view_memory_slot(captured_slot_id))(slot_id)
                            )
                            dpg.add_spacer(height=5)
                    else:
                        dpg.add_text("No outputs defined", color=(128, 128, 128))

    def _draw_execution_tab(self) -> None:
        """Draw code and execution tab."""
        if not self._current_operation:
            return

        attrs = self._current_operation.attributes if hasattr(self._current_operation, 'attributes') else None
        if not attrs:
            dpg.add_text("No attributes available")
            return

        dpg.add_text("Action Code:", color=(200, 200, 200))

        action_code = ""
        if attrs.action:
            action_code = get_function_body(attrs.action)

        action_code_tag = f"action_code_{self._runtime_id}_{id(self._current_operation)}"
        dpg.add_input_text(
            default_value=action_code,
            multiline=True,
            tab_input=True,
            height=150,
            width=-1,
            readonly=True,
            tag=action_code_tag
        )

        dpg.add_spacer(height=15)

        dpg.add_text("Execution Results:", color=(200, 200, 200))
        dpg.add_button(
            label="View Results",
            callback=lambda: asyncio.create_task(self._view_results())
        )

        if hasattr(self._current_operation, 'log_entries'):
            dpg.add_spacer(height=15)
            dpg.add_text("Recent Log Entries:", color=(200, 200, 200))

            with dpg.child_window(height=150, border=True):
                for entry in self._current_operation.log_entries[-10:]:
                    dpg.add_text(entry, wrap=self.width - 60)

    def _draw_settings_tab(self) -> None:
        """Draw settings and configuration tab."""
        if not self._current_operation:
            return

        attrs = self._current_operation.attributes if hasattr(self._current_operation, 'attributes') else None
        if not attrs:
            dpg.add_text("No attributes available")
            return

        dpg.add_text("Execution Settings:", color=(200, 200, 200))
        dpg.add_separator()

        op_id = id(self._current_operation)

        dpg.add_checkbox(
            label="Manages Own Loop",
            default_value=attrs.is_loop,
            callback=lambda s, v: self._update_setting('is_loop', v),
            tag=f"loop_setting_{self._runtime_id}_{op_id}"
        )
        with dpg.tooltip(f"loop_setting_{self._runtime_id}_{op_id}"):
            dpg.add_text("Enable if this operation implements its own internal loop")
            dpg.add_text("(e.g., while self.is_loop: ...)")
            dpg.add_text("The operation will remain in 'running' state until stopped")

        dpg.add_checkbox(
            label="GPU Bound",
            default_value=attrs.is_gpu_bound,
            callback=lambda s, v: self._update_setting('is_gpu_bound', v),
            tag=f"gpu_setting_{self._runtime_id}_{op_id}"
        )

        dpg.add_checkbox(
            label="CPU Bound",
            default_value=attrs.is_cpu_bound,
            callback=lambda s, v: self._update_setting('is_cpu_bound', v),
            tag=f"cpu_setting_{self._runtime_id}_{op_id}"
        )

        dpg.add_checkbox(
            label="Parallel Execution",
            default_value=attrs.parallel,
            callback=lambda s, v: self._update_setting('parallel', v),
            tag=f"parallel_setting_{self._runtime_id}_{op_id}"
        )

        dpg.add_spacer(height=20)

        with dpg.group(horizontal=True, horizontal_spacing=10):
            dpg.add_button(
                label="Save Settings",
                callback=lambda: self._save_operation_settings()
            )

            dpg.add_button(
                label="Reset to Original",
                callback=lambda: self._reset_to_original_attributes()
            )

    async def _update_async(self) -> None:
        """Asynchronous update loop for refreshing display."""
        while self._update_operation.is_ready:
            if self._current_operation and dpg.does_item_exist(self._panel_id):
                await self._refresh_dynamic_content()
            await asyncio.sleep(0.5)

    async def _refresh_dynamic_content(self) -> None:
        """Refresh dynamic content like status indicators and I/O slots."""
        if not self._current_operation or not hasattr(self._current_operation, 'attributes'):
            return

        attrs = self._current_operation.attributes
        current_input_ids = dict(attrs.input_ids) if attrs.input_ids else {}
        current_output_ids = dict(attrs.output_ids) if attrs.output_ids else {}

        inputs_changed = current_input_ids != self._last_input_ids
        outputs_changed = current_output_ids != self._last_output_ids

        if inputs_changed or outputs_changed:
            self._logger.debug(f"I/O slots changed - inputs: {inputs_changed}, outputs: {outputs_changed}")
            self._last_input_ids = current_input_ids
            self._last_output_ids = current_output_ids
            self._render_operation_details(self._current_operation)

    def set_operation(self, operation: BaseOperation) -> None:
        """Set the operation to display in the detail panel."""
        if self._current_operation == operation:
            return

        self._current_operation = operation
        if operation and hasattr(operation, 'attributes'):
            self._original_attributes = copy(operation.attributes)
            attrs = operation.attributes
            self._last_input_ids = dict(attrs.input_ids) if attrs.input_ids else {}
            self._last_output_ids = dict(attrs.output_ids) if attrs.output_ids else {}
        else:
            self._last_input_ids = None
            self._last_output_ids = None

        self._render_operation_details(operation)

    def _render_operation_details(self, operation: BaseOperation) -> None:
        """Safely recreate panel content to avoid container stack issues."""
        # Delete existing panel and recreate it
        if dpg.does_item_exist(self._panel_id):
            dpg.delete_item(self._panel_id)

        # Recreate the panel with fresh content
        with dpg.child_window(tag=self._panel_id,
                             parent=self._parent,
                             width=self.width,
                             height=self.height,
                             border=False):
            self._draw_panel_content()

    def _get_status_color(self, status: str) -> tuple:
        """Get color for operation status."""
        status_colors = {
            "ready": (100, 255, 100),
            "running": (100, 150, 255),
            "waiting": (255, 255, 100),
            "completed": (150, 150, 150),
            "error": (255, 100, 100),
            "paused": (255, 150, 100),
        }
        return status_colors.get(status.lower(), (200, 200, 200))

    def _on_view_mode_changed(self, sender, app_data) -> None:
        """Handle view mode toggle changes."""
        new_mode = self.VIEW_MODE_SIMPLIFIED if app_data == "Simplified" else self.VIEW_MODE_ADVANCED
        if self._view_mode != new_mode:
            self._view_mode = new_mode
            mode_name = "simplified" if new_mode == self.VIEW_MODE_SIMPLIFIED else "advanced"
            self._logger.debug(f"View mode changed to: {mode_name}")
            if self._current_operation:
                self._render_operation_details(self._current_operation)

    def _update_setting(self, setting_name: str, value: bool) -> None:
        """Update an operation setting."""
        if self._current_operation and hasattr(self._current_operation, 'attributes'):
            setattr(self._current_operation.attributes, setting_name, value)
            self._logger.debug(f"Updated {setting_name} to {value} for operation {self._current_operation.name}")

    def _save_operation_settings(self) -> None:
        """Save operation settings to workspace."""
        if self._current_operation:
            try:
                self._current_operation.save_in_workspace()
                self._logger.info(f"Saved settings for operation: {self._current_operation.name}")
            except Exception as e:
                self._logger.error(f"Error saving operation settings: {e}")

    def _reset_to_original_attributes(self) -> None:
        """Reset operation to original attributes."""
        if self._current_operation and self._original_attributes:
            self._current_operation.attributes = copy(self._original_attributes)
            self.set_operation(self._current_operation)
            self._logger.info(f"Reset operation to original attributes: {self._current_operation.name}")

    def _view_memory_slot(self, slot_id: str) -> None:
        """View details of a memory slot."""
        if dpg.does_item_exist(f"popup_view_slot_{slot_id}"):
            dpg.delete_item(f"popup_view_slot_{slot_id}")

        pos = dpg.get_mouse_pos()
        with dpg.window(label=f"Slot Details - {slot_id}", width=250, height=200, pos=pos,
                        show=True, tag=f"popup_view_slot_{slot_id}", no_resize=False):
            asyncio.create_task(self.render_popup(slot_id))

    async def render_popup(self, slot_id: str) -> None:
        """Renders the popup for viewing slot details."""
        _memory_manager = MemoryManager()
        slot = _memory_manager.get_slot(slot_id)
        if slot is None:
            self._logger.error(f"Slot with runtime ID {slot_id} not found.")
            return

        from research_analytics_suite.gui.modules.AdvancedSlotView import AdvancedSlotView
        adv_slot_view = AdvancedSlotView(slot=slot, temp_view=True, width=240, height=160,
                                         parent=f"popup_view_slot_{slot_id}")
        await adv_slot_view.initialize_gui()
        adv_slot_view.draw()

    async def _execute_operation(self) -> None:
        """Execute the current operation."""
        if self._current_operation:
            try:
                self._current_operation.is_ready = True
                self._logger.info(f"Executing operation: {self._current_operation.name}")
            except Exception as e:
                self._logger.error(f"Error executing operation: {e}")

    async def _stop_operation(self) -> None:
        """Stop the current operation."""
        if self._current_operation:
            try:
                await self._current_operation.stop()
                self._logger.info(f"Stopped operation: {self._current_operation.name}")
            except Exception as e:
                self._logger.error(f"Error stopping operation: {e}")

    async def _reset_operation(self) -> None:
        """Reset the current operation."""
        if self._current_operation:
            try:
                await self._current_operation.reset()
                self._logger.info(f"Reset operation: {self._current_operation.name}")
            except Exception as e:
                self._logger.error(f"Error resetting operation: {e}")

    async def _view_results(self) -> None:
        """View operation results."""
        if self._current_operation:
            try:
                results = await self._current_operation.get_results()
                self._logger.debug(f"Operation results: {results}")

                # Create popup for results
                popup_id = f"results_popup_{self._runtime_id}"
                if dpg.does_item_exist(popup_id):
                    dpg.delete_item(popup_id)

                with dpg.window(label="Operation Results",
                               tag=popup_id,
                               width=400,
                               height=300,
                               modal=True,
                               show=True):
                    dpg.add_text(str(results), wrap=380)
                    dpg.add_button(label="Close", callback=lambda: dpg.delete_item(popup_id))

            except Exception as e:
                self._logger.error(f"Error viewing results: {e}")

    def clear_operation(self) -> None:
        """Clear the current operation and show empty state."""
        self._current_operation = None
        self._original_attributes = None
        self._last_rendered_operation = None
        self._last_input_ids = None
        self._last_output_ids = None
        self._render_operation_details(None)

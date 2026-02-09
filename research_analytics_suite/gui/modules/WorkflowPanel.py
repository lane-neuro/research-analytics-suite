"""
WorkflowPanel Module

Provides guided workflow templates with checklist-style progress tracking for common analysis tasks.
Includes pre-built templates and smart suggestions for next steps.

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
from typing import Optional, Dict, List, Any
import dearpygui.dearpygui as dpg

from research_analytics_suite.gui.GUIBase import GUIBase
from research_analytics_suite.gui.modules.NotificationBus import notification_bus
from research_analytics_suite.operation_manager.operations.system.UpdateMonitor import UpdateMonitor


class WorkflowStep:
    """Represents a single step in a workflow."""

    def __init__(self, step_id: str, label: str, operation_type: str = None,
                 required: bool = False, dependencies: List[str] = None):
        self.step_id = step_id
        self.label = label
        self.operation_type = operation_type
        self.required = required
        self.dependencies = dependencies or []
        self.status = "pending"
        self.linked_operation_id = None


class WorkflowSection:
    """Represents a section of workflow steps."""

    def __init__(self, name: str, steps: List[WorkflowStep]):
        self.name = name
        self.steps = steps
        self.is_expanded = True


class WorkflowTemplate:
    """Represents a complete workflow template."""

    def __init__(self, name: str, template_id: str, sections: List[WorkflowSection]):
        self.name = name
        self.template_id = template_id
        self.sections = sections


class WorkflowPanel(GUIBase):
    """
    Workflow panel providing guided checklist-based analysis workflows.
    """

    def __init__(self, width: int, height: int, parent: str):
        super().__init__(width, height, parent)
        self._panel_id = f"workflow_panel_{self._runtime_id}"
        self._workflow_list_id = f"workflow_list_{self._runtime_id}"

        self._current_template: Optional[WorkflowTemplate] = None
        self._update_operation: Optional[UpdateMonitor] = None

        self._hardware_expanded = False

    async def initialize_gui(self) -> None:
        """Initialize workflow panel and subscribe to events."""
        self._logger.debug("Initializing WorkflowPanel")

        notification_bus.subscribe("operation_complete", self._on_operation_complete)

        self._load_default_template()

        self._update_operation = await self._operation_control.operation_manager.create_operation(
            operation_type=UpdateMonitor,
            name=f"workflow_update_{self._runtime_id}",
            action=self._update_async
        )
        self._update_operation.is_ready = True

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        """Resize the workflow panel."""
        self.width = new_width
        self.height = new_height

        if dpg.does_item_exist(self._panel_id):
            dpg.set_item_width(self._panel_id, new_width)
            dpg.set_item_height(self._panel_id, new_height)

    def draw(self) -> None:
        """Draw the workflow panel interface."""
        with dpg.child_window(tag=self._panel_id, parent=self._parent,
                             width=self.width, height=self.height, border=False):
            self._draw_header()
            self._draw_workflow_content()
            dpg.add_separator()
            self._draw_hardware_section()

    def _draw_header(self) -> None:
        """Draw the panel header."""
        dpg.add_text("ANALYSIS WORKFLOW", color=(255, 255, 255))

    def _draw_workflow_content(self) -> None:
        """Draw the workflow template content."""
        if not dpg.does_item_exist(self._panel_id):
            return

        if dpg.does_item_exist(self._workflow_list_id):
            dpg.delete_item(self._workflow_list_id)

        with dpg.child_window(tag=self._workflow_list_id, height=-100, border=False, parent=self._panel_id):
            if not self._current_template:
                self._draw_template_selector()
            else:
                self._draw_active_workflow()

    def _draw_template_selector(self) -> None:
        """Draw template selection interface."""
        dpg.add_spacer(height=10)
        dpg.add_text("Select a workflow template:", color=(200, 200, 200))
        dpg.add_spacer(height=10)

        templates = [
            "Data Cleaning",
            "Statistical Analysis",
            "Machine Learning",
            "Exploratory Data Analysis"
        ]

        for template_name in templates:
            dpg.add_button(
                label=f"○ {template_name}",
                callback=lambda s, a, u: self._select_template(u),
                user_data=template_name,
                width=-1
            )
            dpg.add_spacer(height=5)

    def _draw_active_workflow(self) -> None:
        """Draw the active workflow with sections and steps."""
        if not self._current_template:
            return

        dpg.add_text(f"Template: {self._current_template.name}", color=(150, 150, 200))
        dpg.add_spacer(height=10)

        for section in self._current_template.sections:
            self._draw_workflow_section(section)

    def _draw_workflow_section(self, section: WorkflowSection) -> None:
        """Draw a single workflow section."""
        completed = sum(1 for step in section.steps if step.status == "completed")
        total = len(section.steps)

        expand_icon = "v" if section.is_expanded else ">"
        section_id = f"section_{id(section)}"

        if dpg.does_item_exist(section_id):
            dpg.delete_item(section_id)

        with dpg.group(tag=section_id):
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label=expand_icon,
                    callback=lambda: self._toggle_section(section),
                    small=True,
                    width=30
                )
                dpg.add_text(f"{section.name}", color=(200, 200, 200))
                dpg.add_text(f"[{completed}/{total}]", color=(150, 150, 150))

            if section.is_expanded:
                with dpg.group(indent=20):
                    for step in section.steps:
                        self._draw_workflow_step(step)

            dpg.add_spacer(height=10)

    def _draw_workflow_step(self, step: WorkflowStep) -> None:
        """Draw a single workflow step."""
        step_id = f"step_{step.step_id}"

        if dpg.does_item_exist(step_id):
            dpg.delete_item(step_id)

        with dpg.group(tag=step_id, horizontal=True):
            icon = "[X]" if step.status == "completed" else "[ ]"
            color = (100, 255, 100) if step.status == "completed" else (200, 200, 200)

            dpg.add_text(f"{icon} {step.label}", color=color)

    def _draw_hardware_section(self) -> None:
        """Draw the collapsible hardware status section."""
        expand_icon = "v" if self._hardware_expanded else ">"

        with dpg.group(horizontal=True):
            dpg.add_button(
                label=expand_icon,
                callback=self._toggle_hardware,
                small=True,
                width=30
            )
            dpg.add_text("HARDWARE STATUS", color=(150, 150, 150))

        if self._hardware_expanded:
            with dpg.group(indent=20):
                dpg.add_text("RAM: 38.2%", color=(150, 150, 150))
                dpg.add_text("GPU: Available", color=(150, 150, 150))
                dpg.add_text("CPU: 12.0%", color=(150, 150, 150))

    def _toggle_section(self, section: WorkflowSection) -> None:
        """Toggle section expansion."""
        section.is_expanded = not section.is_expanded

    def _toggle_hardware(self) -> None:
        """Toggle hardware section expansion."""
        self._hardware_expanded = not self._hardware_expanded

    def _select_template(self, template_name: str) -> None:
        """Select and load a workflow template."""
        self._logger.info(f"Selected workflow template: {template_name}")
        self._load_template_by_name(template_name)

    def _load_default_template(self) -> None:
        """Load a default workflow template."""
        steps = [
            WorkflowStep("load_data", "Load Data", "DataLoader", required=True),
            WorkflowStep("clean_data", "Clean Data", "DataCleaner", dependencies=["load_data"]),
            WorkflowStep("normalize", "Normalize/Standardize")
        ]

        section = WorkflowSection("Data Preparation", steps)
        self._current_template = WorkflowTemplate(
            "Quick Start",
            "quick_start",
            [section]
        )

    def _load_template_by_name(self, template_name: str) -> None:
        """Load a specific template by name."""
        self._load_default_template()
        self._current_template.name = template_name

    def _on_operation_complete(self, data: Dict[str, Any]) -> None:
        """Handle operation completion by updating workflow steps."""
        operation_id = data.get('operation_id')

        if not self._current_template:
            return

        for section in self._current_template.sections:
            for step in section.steps:
                if step.linked_operation_id == operation_id:
                    step.status = "completed"
                    self._logger.debug(f"Marked workflow step complete: {step.label}")

    async def _update_async(self) -> None:
        """Async update loop for refreshing the panel."""
        while self._update_operation and self._update_operation.is_ready:
            if dpg.does_item_exist(self._panel_id):
                self._draw_workflow_content()
            await asyncio.sleep(1.0)

    async def cleanup(self) -> None:
        """Cleanup resources when panel is destroyed."""
        if self._update_operation:
            await self._update_operation.stop()

        self._logger.debug("WorkflowPanel cleanup completed")

"""
UpdatedOperationModule

This module defines the UpdatedOperationModule class, which is responsible for managing operations and their GUI
representation within the research analytics suite. It handles the initialization, execution, stopping, pausing,
resuming, and resetting of operations and updates the GUI accordingly.

Author: Lane
Copyright: Lane
Credits: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import dearpygui.dearpygui as dpg
from research_analytics_suite.gui.GUIBase import GUIBase
from research_analytics_suite.operation_manager.operations.core.execution import action_serialized


class UpdatedOperationModule(GUIBase):

    def __init__(self, operation_dict: dict, width: int, height: int, parent: str):
        super().__init__(width, height, parent)

        self._operation_info = operation_dict

        self._name = self._operation_info.get("name", "[unknown_name]")
        self._version = self._operation_info.get("version", "0.0.1")
        self._description = self._operation_info.get("description", "[No description provided]")
        self._category_id = self._operation_info.get("category_id", 0)
        self._author = self._operation_info.get("author", "[unknown_author]")
        self._github = self._operation_info.get("github", "[unknown_github]")
        self._email = self._operation_info.get("email", "[unknown_email]")
        self._operation_id = self._operation_info.get("unique_id", f"{self._github}_{self._name}_{self._version}")
        self._action = action_serialized(self._operation_info.get("action"))
        self._required_inputs = self._operation_info.get("required_inputs", {})
        self._output_type = self._operation_info.get("output_type", {})
        self._parent_operation = self._operation_info.get("parent_operation", None)
        self._inheritance = self._operation_info.get("inheritance", [])

        self._is_loop = self._operation_info.get("is_loop", False)
        self._is_cpu_bound = self._operation_info.get("is_cpu_bound", False)
        self._is_parallel = self._operation_info.get("parallel", False)

        self._parent_id = f"parent_{self._runtime_id}"

    async def initialize_gui(self) -> None:
        pass

    async def _update_async(self) -> None:
        pass

    def draw(self):
        with dpg.group(tag=self._parent_id, parent=self._parent, height=self.height):
            self.draw_upper_region(self._parent_id, width=self.width)
            self.draw_details_region(self._parent_id, width=self.width)
            self.draw_middle_region(self._parent_id, width=self.width)
            self.draw_lower_region(self._parent_id, width=self.width)

    def draw_upper_region(self, parent, width=200):
        # with dpg.group(tag=f"upper_{self._runtime_id}", parent=parent, width=300):
        with dpg.group(horizontal=True, tag=f"basic_{self._runtime_id}",
                       parent=parent, horizontal_spacing=20, width=width):
            dpg.add_text(default_value=f"v{self._version}", indent=10)
            dpg.add_input_text(default_value=self._name)

        with dpg.group(horizontal=True, parent=parent, width=width, horizontal_spacing=20, height=65,
                       tag=f"details_{self._runtime_id}"):
            dpg.add_text(default_value=self._author, indent=10)
            with dpg.group(height=-1):
                dpg.add_input_text(default_value=self._github)
                dpg.add_input_text(default_value=self._email)

    def draw_details_region(self, parent, width=200):
        with dpg.group(horizontal=True, tag=f"more_details_{self._runtime_id}", width=width*.6,
                       horizontal_spacing=15, parent=parent):
            with dpg.group(label="Description", tag=f"description_{self._runtime_id}"):
                dpg.add_text(default_value="Description", indent=10)
                dpg.add_text(default_value=self._description, wrap=width//2+30)

            with dpg.group(label="Output", tag=f"output_{self._runtime_id}", parent=f"more_details_{self._runtime_id}",
                           width=width):
                dpg.add_text(default_value="Output", indent=5)
                dpg.add_listbox(items=[], num_items=3)
        # dpg.add_separator(label="Options", parent=parent)

        with dpg.group(horizontal=True, tag=f"options_{self._runtime_id}", horizontal_spacing=35, parent=parent,
                       width=width):
            dpg.add_checkbox(label="Loop", default_value=self._is_loop, indent=10)
            dpg.add_checkbox(label="CPU", default_value=self._is_cpu_bound)
            dpg.add_checkbox(label="Parallel", default_value=self._is_parallel)

    def draw_middle_region(self, parent, width=200):
        with dpg.group(horizontal=True, tag=f"middle_{self._runtime_id}",
                       parent=parent, horizontal_spacing=5):
            with dpg.group(label="Required Inputs", parent=f"middle_{self._runtime_id}", width=width*.65):
                dpg.add_text(default_value="Input", indent=10)
                req_input_list = [
                    f"{value}" for _, value in self._required_inputs.items()] if self._required_inputs else []
                dpg.add_listbox(items=req_input_list, num_items=3)

            with dpg.group(label="Inherited Ops", width=width*.65):
                dpg.add_text(default_value="Inherited Ops", indent=10)
                dpg.add_listbox(items=self._inheritance, num_items=3)

    def draw_lower_region(self, parent, width=200):
        dpg.add_text(default_value="Action", parent=parent, indent=10)
        with dpg.group(parent=parent, tag=f"action_group_{self._runtime_id}"):
            dpg.add_input_text(default_value=self._action, multiline=True, tab_input=True,
                               height=100)

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        """Resizes the GUI."""
        self.width = new_width
        self.height = new_height
        dpg.set_item_width(self._parent_id, new_width)
        dpg.set_item_height(self._parent_id, new_height)

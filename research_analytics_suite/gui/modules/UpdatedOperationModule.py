"""
OperationModule

This module defines the OperationModule class, which is responsible for managing operations and their GUI representation
within the research analytics suite. It handles the initialization, execution, stopping, pausing, resuming, and
resetting of operations and updates the GUI accordingly.

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


class UpdatedOperationModule(GUIBase):

    def __init__(self, operation_dict: dict, width: int, height: int, parent: str):
        """
        Initializes the OperationModule with the specified operation, width, height, and parent.

        Args:
            operation_dict (dict): The dictionary containing the operation information.
            width (int): The width of the operation module.
            height (int): The height of the operation module.
            parent (str): The parent GUI element ID.
        """
        super().__init__(width, height, parent)

        self._operation_info = operation_dict

        self._version = self._operation_info.get("version", "1")
        self._name = self._operation_info.get("name", "[unknown_name]")
        self._author = self._operation_info.get("author", "[unknown_author]")
        self._github = self._operation_info.get("github", "[unknown_github]")
        self._email = self._operation_info.get("email", "[unknown_email]")
        self._operation_id = self._operation_info.get("unique_id", f"{self._github}_{self._name}_{self._version}")
        self._description = self._operation_info.get("description", "[No description provided]")
        self._action = self._operation_info.get("action", "")
        self._output_type = self._operation_info.get("output_type", None)
        self._is_loop = self._operation_info.get("persistent", False)
        self._is_cpu_bound = self._operation_info.get("is_cpu_bound", False)
        self._is_parallel = self._operation_info.get("concurrent", False)
        self._dependencies = self._operation_info.get("dependencies", [])

        self._child_ops_parent = None
        self._values_required_parent = None

        self._concurrent_id = f"concurrent_{self._runtime_id}"
        self._persistent_id = f"persistent_{self._runtime_id}"
        self._cpu_bound_id = f"cpu_bound_{self._runtime_id}"
        self._parent_id = f"parent_{self._runtime_id}"
        self._left_panel_id = f"left_panel_{self._runtime_id}"

    async def initialize_gui(self) -> None:
        """Initializes resources and adds the update operation."""
        pass

    async def _update_async(self) -> None:
        pass

    def draw(self):
        with dpg.group(tag=self._parent_id, parent=self._parent):
            # Upper Region
            with dpg.group(tag=f"upper_{self._runtime_id}", parent=self._parent_id):
                with dpg.group(horizontal=True, tag=f"basic_{self._runtime_id}", parent=f"upper_{self._runtime_id}"):
                    with dpg.group():
                        dpg.add_text(default_value=self._version, parent=f"basic_{self._runtime_id}")
                    with dpg.group():
                        dpg.add_input_text(default_value=self._name, parent=f"basic_{self._runtime_id}")

                with dpg.group(label="Details", horizontal=True, tag=f"details_{self._runtime_id}",
                               parent=f"upper_{self._runtime_id}"):
                    with dpg.group(parent=f"details_{self._runtime_id}"):
                        dpg.add_text(default_value=self._author)
                    with dpg.group(parent=f"details_{self._runtime_id}"):
                        dpg.add_input_text(default_value=self._github)
                        dpg.add_input_text(default_value=self._email)

                with dpg.group(horizontal=True, tag=f"more_details_{self._runtime_id}",
                               parent=f"upper_{self._runtime_id}"):
                    with dpg.group(label="Description", tag=f"description_{self._runtime_id}"):
                        dpg.add_input_text(default_value=self._description, multiline=True)
                    with dpg.group(label="Output Type", tag=f"output_{self._runtime_id}"):
                        dpg.add_listbox(items=["Type1", "Type2", "Type3"])

                with dpg.group(horizontal=True, tag=f"options_{self._runtime_id}",
                               parent=f"upper_{self._runtime_id}"):
                    with dpg.group():
                        dpg.add_checkbox(label="Loop", default_value=False)
                    with dpg.group():
                        dpg.add_checkbox(label="CPU", default_value=False)
                    with dpg.group():
                        dpg.add_checkbox(label="Parallel", default_value=False)

            # Middle Region
            with dpg.group(horizontal=True, tag=f"middle_{self._runtime_id}",
                           parent=self._parent_id):
                with dpg.group(label="Dependencies"):
                    dpg.add_listbox(label="Values Required List", items=['test', 'test2', 'test3'], num_items=6)
                    # dpg.add_button(label="Add Value", callback=self.add_value)

                with dpg.group(label="Child Operations"):
                    dpg.add_listbox(items=[], num_items=6)
                    # dpg.add_button("Add Operation", callback=self.add_child_operation)

            # Lower Region
            with dpg.group(tag=f"action_{self._runtime_id}", parent=self._parent_id):
                dpg.add_text("Action")
                dpg.add_input_text(default_value="##Code Block", multiline=True)

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        """Resizes the GUI."""
        self.width = new_width
        self.height = new_height
        dpg.set_item_width(self._parent_id, new_width)
        dpg.set_item_height(self._parent_id, new_height)

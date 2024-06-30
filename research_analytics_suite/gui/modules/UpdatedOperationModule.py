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
        self._child_ops_parent = None
        self._values_required_parent = None

        self._concurrent_id = f"concurrent_{self._unique_id}"
        self._persistent_id = f"persistent_{self._unique_id}"
        self._cpu_bound_id = f"cpu_bound_{self._unique_id}"
        self._parent_id = f"parent_{self._unique_id}"
        self._left_panel_id = f"left_panel_{self._unique_id}"

    async def initialize_gui(self) -> None:
        """Initializes resources and adds the update operation."""
        pass

    async def _update_async(self) -> None:
        pass

    def draw(self):
        with dpg.group(tag=self._parent_id, parent=self._parent):
            # Upper Region
            with dpg.group(tag=f"upper_{self._unique_id}", height=300, parent=self._parent_id):
                dpg.add_group(horizontal=True, tag=f"basic_{self._unique_id}",
                              width=-1)
                _width = int(dpg.get_item_width(f"basic_{self._unique_id}") * 0.3)
                print(_width)
                dpg.add_input_text(default_value="0.0.1", width=_width)
                dpg.add_input_text(default_value="Name")

                with dpg.group(label="Details", horizontal=True, width=-1, tag=f"details_{self._unique_id}"):
                    _width = int(dpg.get_item_width(f"details_{self._unique_id}") * 0.3)
                    dpg.add_input_text(default_value="Author", width=_width, height=-1)
                    with dpg.group(width=_width):
                        dpg.add_input_text(default_value="GitHub", width=-1)
                        dpg.add_input_text(default_value="##Email", width=-1)
                    dpg.add_input_text(default_value="##Unique ID", height=-1)

                with dpg.group(horizontal=True, width=-1, tag=f"more_details_{self._unique_id}"):
                    with dpg.group(label="Description", tag=f"description_{self._unique_id}",
                                   width=int(dpg.get_item_width(f"more_details_{self._unique_id}") * 0.8)):
                        dpg.add_input_text(default_value="Description", multiline=True, width=-1, height=-1)
                    with dpg.group(label="Output Type", width=-1, height=-1, tag=f"output_{self._unique_id}"):
                        dpg.add_listbox(items=["Type1", "Type2", "Type3"], width=-1)

                with dpg.group(horizontal=True, width=-1, height=30,
                               tag=f"options_{self._unique_id}", parent=self._parent_id):
                    _width = int(dpg.get_item_width(f"options_{self._unique_id}") * 0.3)
                    with dpg.group(width=_width):
                        dpg.add_checkbox(label="Loop", default_value=False)
                    with dpg.group(width=_width):
                        dpg.add_checkbox(label="CPU", default_value=False)
                    with dpg.group(width=-1):
                        dpg.add_checkbox(label="Parallel", default_value=False)

            # Middle Region
            with dpg.group(horizontal=True, width=-1, height=300, tag=f"middle_{self._unique_id}",
                           parent=self._parent_id):
                _width = int(dpg.get_item_width(f"middle_{self._unique_id}") * 0.3)
                with dpg.group(label="Dependencies", width=_width):
                    dpg.add_listbox(label="Values Required List", items=['test', 'test2', 'test3'], num_items=6)
                    # dpg.add_button(label="Add Value", callback=self.add_value)

                with dpg.group(label="Child Operations", width=-1):
                    dpg.add_listbox(items=[], num_items=6)
                    # dpg.add_button("Add Operation", callback=self.add_child_operation)

            # Lower Region
            with dpg.group(height=-1, width=-1, tag=f"action_{self._unique_id}", parent=self._parent_id):
                dpg.add_text("Action")
                dpg.add_input_text(default_value="##Code Block", multiline=True)

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        """Resizes the GUI."""
        self.width = new_width
        self.height = new_height
        dpg.set_item_width(self._parent_id, new_width)
        dpg.set_item_height(self._parent_id, new_height)

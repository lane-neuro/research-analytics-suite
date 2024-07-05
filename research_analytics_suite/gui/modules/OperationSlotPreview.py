"""
OperationSlotPreview Module

This module defines the OperationSlotPreview class, which is responsible for managing the GUI representation of
individual operation slots.

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


class OperationSlotPreview(GUIBase):

    def __init__(self, operation_dict: dict, width: int, height: int, parent: str):
        """
        Initializes the OperationSlotPreview with the specified operation, width, height, and parent.

        Args:
            operation_dict (dict): The dictionary containing the operation information.
            width (int): The width of the operation module.
            height (int): The height of the operation module.
            parent (str): The parent GUI element ID.
        """
        super().__init__(width, height, parent)

        from research_analytics_suite.gui.NodeEditorManager import NodeEditorManager
        self._node_manager = NodeEditorManager()

        self._operation_info = operation_dict

        self._name = self._operation_info["name"]
        self._version = self._operation_info["version"]
        self._description = self._operation_info["description"]
        self._author = self._operation_info["author"]
        self._github = self._operation_info["github"]
        self._action = self._operation_info["action"]
        self._output_type = None  # self._operation_info["output_type"]
        self._required_inputs = self._operation_info["required_inputs"]
        if self._required_inputs is None:
            self._required_inputs = []
        self._parent_id = f"parent_{self._runtime_id}"

    async def initialize_gui(self) -> None:
        """Initializes resources and adds the update operation."""
        pass

    async def _update_async(self) -> None:
        pass

    def draw(self):
        with dpg.child_window(tag=self._parent_id, parent=self._parent, width=self.width, height=self.height,
                              no_scrollbar=True, no_scroll_with_mouse=True, border=False):
            with dpg.tooltip(parent=self._parent_id, tag=f"tooltip_{self.runtime_id}"):
                from research_analytics_suite.gui.modules.UpdatedOperationModule import UpdatedOperationModule
                operation_view = UpdatedOperationModule(operation_dict=self._operation_info, width=200,
                                                        height=100, parent=f"tooltip_{self.runtime_id}")
                operation_view.draw()

            with dpg.group(tag=f"slot_preview_{self.runtime_id}", parent=self._parent_id,
                           horizontal=True, horizontal_spacing=10):
                dpg.add_button(label="+", width=25, height=25, parent=f"slot_preview_{self.runtime_id}",
                               callback=lambda: self._node_manager.editors["planning_editor"].add_node(
                                   self._operation_info), indent=5)
                dpg.add_text(default_value=f"{self._name}", parent=f"slot_preview_{self.runtime_id}")

                # with dpg.child_window(height=30, width=55, no_scrollbar=True, pos=(self.width - 115, 5)):
                #     deps = self._operation_info['dependencies'] if 'dependencies' in self._operation_info else []
                #     if deps is []:
                #         dpg.add_text("-")
                #     elif iter(deps):
                #         for item in deps:
                #             dpg.add_text(item)
                #     else:
                #         dpg.add_text("-")
                #
                # with dpg.child_window(height=30, width=55, no_scrollbar=True, pos=(self.width - 61, 5)):
                #     outs = self._operation_info['output_type'] if 'output_type' in self._operation_info else []
                #     if outs is []:
                #         dpg.add_text("-")
                #     elif iter(outs):
                #         for item in outs:
                #             dpg.add_text(item)
                #     else:
                #         dpg.add_text("-")

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        """Resizes the GUI."""
        self.width = new_width
        self.height = new_height
        dpg.set_item_width(self._parent_id, new_width)
        dpg.set_item_height(self._parent_id, new_height)

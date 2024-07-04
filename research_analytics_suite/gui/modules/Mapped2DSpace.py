"""
Mapped2DSpace Module

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
import dearpygui.dearpygui as dpg
from research_analytics_suite.gui.GUIBase import GUIBase


class Mapped2DSpace(GUIBase):
    """
    Mapped2DSpace class is used to create a 2D space to utilize DearPyGui node editor.

    Attributes:
        _lock (asyncio.Lock): The lock to ensure thread safety.
    """
    _lock = asyncio.Lock()

    def __init__(self, width: int, height: int, parent):
        """
        Initialize the Mapped2DSpace class.

        Args:
            width (int): The width of the 2D space.
            height (int): The height of the 2D space.
            parent (Any): The parent object.
        """
        super().__init__(width, height, parent)
        self._node_editor_id = dpg.generate_uuid()
        self._nodes = []
        self._links = []

    async def initialize_gui(self) -> None:
        ...

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        # Placeholder for resizing logic
        pass

    async def _update_async(self) -> None:
        # Placeholder for asynchronous update logic
        pass

    def add_node(self, label, pos=(0, 0)):
        """
        Adds a node to the node editor.

        Args:
            label (str): The label of the node.
            pos (tuple): The position of the node.
        """
        node_id = dpg.generate_uuid()
        with dpg.node(tag=node_id, parent=self._node_editor_id, label=label, pos=pos):
            input_id = dpg.generate_uuid()
            output_id = dpg.generate_uuid()
            dpg.add_node_attribute(tag=input_id, attribute_type=dpg.mvNode_Attr_Input)
            dpg.add_node_attribute(tag=output_id, attribute_type=dpg.mvNode_Attr_Output)
        self._nodes.append((node_id, input_id, output_id))

    def link_nodes(self, output_attr, input_attr):
        """
        Links two nodes together.

        Args:
            output_attr (int): The UUID of the output attribute.
            input_attr (int): The UUID of the input attribute.
        """
        link_id = dpg.generate_uuid()
        dpg.add_node_link(output_attr, input_attr, parent=self._node_editor_id, id=link_id)
        self._links.append(link_id)

    def draw(self) -> None:
        """
        Draws the node editor and its nodes.
        """
        with dpg.node_editor(tag=self._node_editor_id, parent=self._parent):
            pass
        dpg.show_item(self._node_editor_id)
        for node in self._nodes:
            dpg.show_item(node[0])
        for link in self._links:
            dpg.show_item(link)

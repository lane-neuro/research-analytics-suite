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
from copy import copy

import dearpygui.dearpygui as dpg
from research_analytics_suite.gui.GUIBase import GUIBase
from research_analytics_suite.operation_manager.operations.core.OperationAttributes import OperationAttributes


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
        self._active_operation_modules = []
        self._nodes = []
        self._links = []

    async def initialize_gui(self) -> None:
        """
        Initializes the GUI resources and sets up the node editor.
        """
        self._logger.debug("Initializing the node editor.")

        from research_analytics_suite.operation_manager.operations.system.UpdateMonitor import UpdateMonitor
        self._update_operation = await self._operation_control.operation_manager.create_operation(
            operation_type=UpdateMonitor, name=f"gui_{self._runtime_id}", action=self._update_async)
        self._update_operation.is_ready = True

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        # Placeholder for resizing logic
        pass

    async def _update_async(self) -> None:
        """Asynchronously updates the node editor and initializes node elements."""
        while not self._update_operation.is_running:
            await asyncio.sleep(0.1)

        while self._update_operation.is_running:
            for op_module in self._active_operation_modules:
                if not op_module.initialized:
                    await op_module.initialize_gui()

            await asyncio.sleep(0.0001)

    def add_node(self, operation_attributes: OperationAttributes, pos=(0, 0)) -> tuple:
        """
        Adds a node to the node editor.

        Args:
            operation_attributes (OperationAttributes): The dictionary containing the operation information.
            pos (tuple): The position of the node.

        Returns:
            tuple: The UUIDs of the node, input attribute, and output attribute.
        """
        _operation = None
        node_id = dpg.generate_uuid()
        operation_attributes = copy(operation_attributes)
        operation_attributes.active = True
        _operation_module = None
        with dpg.node(tag=node_id, parent=self._node_editor_id, label=operation_attributes.name, pos=pos):
            input_id = dpg.generate_uuid()
            output_id = dpg.generate_uuid()

            from research_analytics_suite.gui.modules.UpdatedOperationModule import UpdatedOperationModule

            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static, tag=f"{node_id}_name"):
                with dpg.group(tag=f"{node_id}_name_group"):
                    _operation_module = UpdatedOperationModule(operation_attributes, 200, 500,
                                                               node_id)
                    # Use operation attributes directly since operation isn't created yet
                    dpg.configure_item(node_id, label=f"{operation_attributes.name} [rID: {operation_attributes.unique_id[-6:]}]")
                    _operation_module.draw_upper_region(parent=f"{node_id}_name_group", width=200)

            with dpg.node_attribute(tag=f"{node_id}_details", attribute_type=dpg.mvNode_Attr_Static):
                with dpg.group(tag=f"{node_id}_details_group"):
                    _operation_module.draw_details_region(parent=f"{node_id}_details_group", width=200)

            with dpg.node_attribute(tag=f"{node_id}_middle", attribute_type=dpg.mvNode_Attr_Static):
                with dpg.group(tag=f"{node_id}_middle_group"):
                    _operation_module.draw_middle_region(parent=f"{node_id}_middle_group", width=200)

            with dpg.node_attribute(tag=f"{node_id}_lower", attribute_type=dpg.mvNode_Attr_Static):
                with dpg.group(tag=f"{node_id}_lower_group", width=260):
                    _operation_module.draw_lower_region(parent=f"{node_id}_lower_group", width=200)

        self._nodes.append((node_id, input_id, output_id))
        self._active_operation_modules.append(_operation_module)
        return node_id, input_id, output_id

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

    def clear_elements(self):
        """
        Clears all elements from the node editor.
        """
        # TODO: fix reset state for gui elements when switching workspaces. currently works but for some reason the middle group's listbox is empty when I try to create a new operation
        for node in self._nodes:
            dpg.delete_item(node[0])
        self._nodes = []

        for link in self._links:
            dpg.delete_item(link)
        self._links = []

        for op_module in self._active_operation_modules:
            dpg.delete_item(op_module.gui_id)

        self._active_operation_modules = []

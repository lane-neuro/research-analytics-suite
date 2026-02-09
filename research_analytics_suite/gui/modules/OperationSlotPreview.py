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
from research_analytics_suite.operation_manager.operations.core.OperationAttributes import OperationAttributes
from research_analytics_suite.operation_manager.operations.core.execution import action_serialized


class OperationSlotPreview(GUIBase):

    def __init__(self, operation_attributes: OperationAttributes, width: int, height: int, parent: str):
        """
        Initializes the OperationSlotPreview with the specified operation, width, height, and parent.

        Args:
            operation_attributes (OperationAttributes): The dictionary containing the operation information.
            width (int): The width of the operation module.
            height (int): The height of the operation module.
            parent (str): The parent GUI element ID.
        """
        super().__init__(width, height, parent)

        from research_analytics_suite.gui.NodeEditorManager import NodeEditorManager
        self._node_manager = NodeEditorManager()

        self._attributes = operation_attributes

        self._name = self._attributes.name
        self._version = self._attributes.version
        self._description = self._attributes.description
        self._author = self._attributes.author
        self._github = self._attributes.github
        self._action = action_serialized(self._attributes.action)
        self._output_type = None  # self._attributes["output_type"]
        self._parent_id = f"parent_{self._runtime_id}"

    async def initialize_gui(self) -> None:  # pragma: no cover
        """Initializes resources and adds the update operation."""
        pass

    async def _update_async(self) -> None:  # pragma: no cover
        pass

    def add_to_workspace(self, operation_attributes: OperationAttributes) -> None:
        """
        Add operation to workspace with given attributes.

        Args:
            operation_attributes (OperationAttributes): The attributes of the operation to add.
        """
        import asyncio
        asyncio.create_task(self._create_and_add_operation(operation_attributes))

    async def _create_and_add_operation(self, operation_attributes: OperationAttributes) -> None:
        """Create and register a new operation from attributes."""
        try:
            # Set attributes as active for proper initialization
            operation_attributes.active = True

            from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation
            operation = BaseOperation(operation_attributes)

            # Initialize the operation
            await operation.initialize_operation()

            # Add to operation manager (this handles sequencer registration)
            operation = await self._operation_control.operation_manager.add_initialized_operation(operation)

            self._logger.info(f"Operation added to workspace: {operation.name}")

        except Exception as e:
            self._logger.error(f"Failed to add operation: {e}", self.__class__.__name__)

    def draw(self):
        with dpg.child_window(tag=self._parent_id, parent=self._parent, width=self.width, height=self.height,
                              no_scrollbar=True, no_scroll_with_mouse=True, border=False):
            with dpg.tooltip(parent=self._parent_id, tag=f"tooltip_{self.runtime_id}"):
                from research_analytics_suite.gui.modules.UpdatedOperationModule import UpdatedOperationModule
                operation_view = UpdatedOperationModule(operation_attributes=self._attributes, width=200,
                                                        height=100, parent=f"tooltip_{self.runtime_id}")
                operation_view.draw()

            with dpg.group(tag=f"slot_preview_{self.runtime_id}", parent=self._parent_id,
                           horizontal=True, horizontal_spacing=10):
                dpg.add_button(label="+", width=25, height=25, parent=f"slot_preview_{self.runtime_id}",
                               callback=lambda: self.add_to_workspace(OperationAttributes(**self._attributes.export_attributes())), indent=5)
                dpg.add_text(default_value=f"{self._name}", parent=f"slot_preview_{self.runtime_id}")

                # with dpg.child_window(height=30, width=55, no_scrollbar=True, pos=(self.width - 115, 5)):
                #     deps = self._attributes['dependencies'] if 'dependencies' in self._attributes else []
                #     if deps is []:
                #         dpg.add_text("-")
                #     elif iter(deps):
                #         for item in deps:
                #             dpg.add_text(item)
                #     else:
                #         dpg.add_text("-")
                #
                # with dpg.child_window(height=30, width=55, no_scrollbar=True, pos=(self.width - 61, 5)):
                #     outs = self._attributes['output_type'] if 'output_type' in self._attributes else []
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

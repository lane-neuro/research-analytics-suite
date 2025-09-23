"""
NodeEditorManager Module

The NodeEditorManager class module is used to manage the node editor and its components.

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


class NodeEditorManager:
    """
    NodeEditorManager class is used to manage the node editor and its components.

    Attributes:
        editors (dict): A dictionary of the editors.
        cross_editor_links (list): A list of cross-editor links.

    Methods:
        add_editor: Adds an editor to the manager.
        add_cross_editor_link: Adds a cross-editor link.
        draw_cross_editor_links: Draws the cross-editor links.
        update_cross_editor_links: Updates the cross-editor links.
    """
    _lock = asyncio.Lock()
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._editors = {}
            self._cross_editor_links = []

            self._initialized = False

    async def initialize(self):
        if not self._initialized:
            async with NodeEditorManager._lock:
                if not self._initialized:

                    self._initialized = True

    @property
    def editors(self) -> dict:
        return self._editors

    @property
    def cross_editor_links(self):
        return self._cross_editor_links

    async def add_editor(self, editor_id, width, height, parent):
        from research_analytics_suite.gui.modules.Mapped2DSpace import Mapped2DSpace
        editor = Mapped2DSpace(width, height, parent)
        await editor.initialize_gui()

        self._editors[editor_id] = editor
        editor.draw()

    def get_editor(self, editor_id):
        if editor_id not in self._editors or self._editors.get(editor_id) is None:
            return None
        return self._editors.get(editor_id)

    def add_cross_editor_link(self, output_attr, input_attr, editor_id_from, editor_id_to):
        self._cross_editor_links.append((output_attr, input_attr, editor_id_from, editor_id_to))

    def draw_cross_editor_links(self):
        for input_attr, output_attr, editor_id_from, editor_id_to in self._cross_editor_links:
            start_pos = dpg.get_item_pos(input_attr)
            end_pos = dpg.get_item_pos(output_attr)
            start_size = dpg.get_item_rect_size(input_attr)
            end_size = dpg.get_item_rect_size(output_attr)

            start_pos = (start_pos[0] + start_size[0] / 2, start_pos[1] + start_size[1] / 2)
            end_pos = (end_pos[0] + end_size[0] / 2, end_pos[1] + end_size[1] / 2)

            with dpg.drawlist(parent="cross_editor_drawlist"):
                dpg.draw_line(start_pos, end_pos, color=(255, 0, 0, 255), thickness=2.0)

    def update_cross_editor_links(self):
        dpg.delete_item("cross_editor_drawlist", children_only=True)
        self.draw_cross_editor_links()

    async def reset_for_workspace(self, config=None):
        """
        Reset NodeEditorManager for workspace loading.

        Args:
            config: Optional new configuration (unused by NodeEditorManager)
        """
        async with NodeEditorManager._lock:
            for _editor in self._editors.values():
                _editor.clear_elements()

            # Reset state
            self._editors.clear()
            self._cross_editor_links.clear()

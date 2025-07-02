"""
This module contains a function to add a new left-aligned combobox to the GUI.

Author: Lane
Credits: DearPyGui
License: BSD 3-Clause License
"""
from __future__ import annotations

from typing import Any

import dearpygui.dearpygui as dpg


def left_aligned_combo(label: str, tag: str, parent, height: int = -1, width: int = -1,
                       items: list[str] | tuple[str, ...] = (), label_indent: int = -1,
                       bullet: bool = False, user_data: Any = None, callback = None) -> None:
    """
    Adds a new left-aligned combobox to the GUI.

    Args:
        label (str): The label for the checkbox.
        tag (str): The tag for the checkbox.
        parent: The parent of the checkbox.
        height (int): The height of the checkbox. Default is -1 (parent).
        width (int): The width of the checkbox. Default is -1 (parent).
        items (list[str] | tuple[str, ...]): The items to display in the combobox. Default is an empty list.
        label_indent (int): The indent of the label. Default is 0.
        bullet (bool): Whether to display a bullet point. Default is False.
        user_data (Any): User data to pass to the callback function. Default is None.
        callback (function): The callback function for the combobox. Default is None.
    """
    if height == -1:
        height = dpg.get_item_height(parent)
    if width == -1:
        width = dpg.get_item_width(parent)

    with dpg.group(horizontal=True, parent=parent, width=width, height=height):
        with dpg.group(horizontal=False, width=int(width * 0.9), height=height):
            dpg.add_text(default_value=label, bullet=bullet, indent=label_indent)
        with dpg.group(horizontal=True, height=height):
            dpg.add_combo(tag=tag, items=items, callback=callback, user_data=user_data)

"""
This module contains a function to add a new left-aligned checkbox to the GUI.

Author: Lane
Credits: DearPyGui
License: BSD 3-Clause License
"""
import dearpygui.dearpygui as dpg


def left_aligned_checkbox(label: str, tag: str, parent: int | str, value: bool, height: int = -1, width: int = -1,
                          bullet: bool = False, readonly: bool = False, label_indent: int = -1) -> None:
    """
    Adds a new left-aligned checkbox to the GUI.

    Args:
        label (str): The label for the checkbox.
        tag (str): The tag for the checkbox.
        parent (int | str): The parent of the checkbox.
        value (bool): The default value for the checkbox.
        height (int): The height of the checkbox. Default is -1 (parent).
        width (int): The width of the checkbox. Default is -1 (parent).
        bullet (bool): Whether to display a bullet point. Default is False.
        readonly (bool): Whether the checkbox is read-only. Default is False.
        label_indent (int): The indent of the label. Default is 0.
    """
    if height == -1:
        height = dpg.get_item_height(parent)
    if width == -1:
        width = dpg.get_item_width(parent)

    with dpg.group(horizontal=True, parent=parent, width=width, height=height):
        with dpg.group(horizontal=False, width=int(width * 0.4), height=height):
            dpg.add_text(default_value=label, bullet=bullet, indent=label_indent)
        with dpg.group(horizontal=True, width=-1, height=height):
            dpg.add_checkbox(tag=tag, default_value=value, enabled=not readonly)

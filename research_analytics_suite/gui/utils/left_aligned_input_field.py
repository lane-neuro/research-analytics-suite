"""
This module contains a utility function for adding a left-aligned input field to the GUI.

Author: Lane
Credits: DearPyGui
License: BSD 3-Clause License
"""
import dearpygui.dearpygui as dpg


def left_aligned_input_field(label: str, tag: str, parent, value: str, height: int = -1,
                             width: int = -1,
                             bullet: bool = False, multiline: bool = False, readonly: bool = False,
                             callback=None) -> None:
    """
    Adds a new left-aligned input field to the GUI.

    Args:
        label (str): The label for the input field.
        tag (str): The tag for the input field.
        parent: The parent of the input field.
        value (str): The default value for the input field.
        height (int): The height of the input field. Default is -1 (parent).
        width (int): The width of the input field. Default is -1 (parent).
        bullet (bool): Whether to display a bullet point. Default is False.
        multiline (bool): Whether to allow multiple lines of text. Default is False.
        readonly (bool): Whether the prompt is read-only. Default is False.
        callback (function): The callback function for the input field. Default is None
    """
    if height == -1:
        height = dpg.get_item_height(parent)
    if width == -1:
        width = dpg.get_item_width(parent)

    with dpg.group(horizontal=True, parent=parent, width=width, height=height):
        dpg.add_text(label, bullet=bullet)
        dpg.add_input_text(tag=tag, default_value=value, indent=int(width * 0.4), width=-1, multiline=multiline,
                           height=-1, readonly=readonly, enabled=not readonly, callback=callback)

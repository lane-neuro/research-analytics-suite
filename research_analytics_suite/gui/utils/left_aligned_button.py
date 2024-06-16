"""
This module contains a utility function for adding a left-aligned button to the GUI.

Author: Lane
Credits: DearPyGui
License: BSD 3-Clause License
"""
import dearpygui.dearpygui as dpg


def left_aligned_button(label: str, text: str, tag: str, parent: int | str, callback, height: int = -1,
                        width: int = -1, bullet: bool = False, enabled: bool = False) -> None:
    """
    Adds a new left-aligned button to the GUI.

    Args:
        label (str): The label for the button.
        text (str): The text for the button.
        tag (str): The tag for the button.
        parent (int | str): The parent of the button.
        callback: The callback function for the button.
        height (int): The height of the input field. Default is -1 (parent).
        width (int): The width of the input field. Default is -1 (parent).
        bullet (bool): Whether to display a bullet point. Default is False.
        enabled (bool): Whether the prompt is enabled. Default is True.
    """
    if height == -1:
        height = dpg.get_item_height(parent)
    if width == -1:
        width = dpg.get_item_width(parent)

    with dpg.group(horizontal=True, parent=parent, width=width, height=height):
        dpg.add_text(default_value=label, bullet=bullet)
        dpg.add_button(label=text, tag=tag, callback=callback, indent=int(width * 0.4), enabled=enabled)

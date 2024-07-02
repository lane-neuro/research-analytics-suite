"""
center_in_container

This function centers an item within a container. It calculates the offset needed to center the item within the
container and sets the item's position accordingly.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import dearpygui.dearpygui as dpg


def center_in_container(container, item):
    container_width = dpg.get_item_width(container)
    container_height = dpg.get_item_height(container)

    item_width = dpg.get_item_width(item)
    item_height = dpg.get_item_height(item)

    offset_x = container_width / 2 - item_width
    offset_y = (container_height - item_height) / 2

    dpg.set_item_pos(item, [offset_x, 0])

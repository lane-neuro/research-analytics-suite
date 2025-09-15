"""
DocumentationDialog Module

This module defines the DocumentationDialog class, which provides a simple dialog directing users
to the GitHub documentation for the Research Analytics Suite.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import webbrowser
import dearpygui.dearpygui as dpg

from research_analytics_suite.gui.GUIBase import GUIBase


class DocumentationDialog(GUIBase):
    """A class to create and manage the documentation dialog."""

    def __init__(self, width: int = 400, height: int = 250, parent=None):
        """
        Initializes the DocumentationDialog instance.
        """
        super().__init__(width, height, parent)
        self._dialog_tag = "documentation_dialog"

    async def initialize_gui(self) -> None:
        """Initialize the documentation dialog GUI components."""
        if dpg.does_item_exist(self._dialog_tag):
            dpg.delete_item(self._dialog_tag)

    async def _update_async(self) -> None:
        """Async update method (not used for this dialog)."""
        pass

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        """Resize the dialog GUI."""
        if dpg.does_item_exist(self._dialog_tag):
            dpg.configure_item(self._dialog_tag, width=new_width, height=new_height)

    def draw(self):
        """Creates and shows the documentation dialog."""
        if dpg.does_item_exist(self._dialog_tag):
            dpg.delete_item(self._dialog_tag)

        with dpg.window(
            label="Documentation",
            modal=True,
            tag=self._dialog_tag,
            width=self._width,
            height=self._height,
            no_resize=True
        ):
            dpg.add_text("Research Analytics Suite Documentation", color=(255, 255, 0))
            dpg.add_separator()

            dpg.add_text("For comprehensive documentation, please visit:")
            dpg.add_spacer(height=10)

            dpg.add_button(
                label="Open GitHub Documentation",
                callback=self._open_github_docs,
                width=250
            )

            dpg.add_spacer(height=3)
            dpg.add_text("The documentation includes:")
            dpg.add_text("- Installation instructions")
            dpg.add_text("- Getting started guide")
            dpg.add_text("- Feature overview")

            dpg.add_spacer(height=3)
            dpg.add_separator()

            with dpg.group(horizontal=True):
                dpg.add_button(label="Close", callback=self._close_dialog)

    def _open_github_docs(self):
        """Opens the GitHub repository in the default web browser."""
        try:
            webbrowser.open("https://github.com/lane-neuro/research-analytics-suite")
            self._logger.info("Opened GitHub documentation in browser")
        except Exception as e:
            self._logger.error(e, "Failed to open GitHub documentation")

    def _close_dialog(self):
        """Closes the documentation dialog."""
        if dpg.does_item_exist(self._dialog_tag):
            dpg.delete_item(self._dialog_tag)

    def show(self):
        """Shows the documentation dialog."""
        self.draw()
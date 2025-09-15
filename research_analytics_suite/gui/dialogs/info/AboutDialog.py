"""
AboutDialog Module

This module defines the AboutDialog class, which provides information about the Research Analytics Suite
including version, author, license, and contact information.

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
import platform
import dearpygui.dearpygui as dpg

from research_analytics_suite.gui.GUIBase import GUIBase


class AboutDialog(GUIBase):
    """A class to create and manage the about dialog."""

    def __init__(self, width: int = 450, height: int = 400, parent=None):
        """
        Initializes the AboutDialog instance.
        """
        super().__init__(width, height, parent)
        self._dialog_tag = "about_dialog"

    async def initialize_gui(self) -> None:
        """Initialize the about dialog GUI components."""
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
        """Creates and shows the about dialog."""
        if dpg.does_item_exist(self._dialog_tag):
            dpg.delete_item(self._dialog_tag)

        with dpg.window(
            label="About Research Analytics Suite",
            modal=True,
            tag=self._dialog_tag,
            width=self._width,
            height=self._height,
            no_resize=True
        ):
            # Header
            dpg.add_text("Research Analytics Suite", color=(255, 255, 0))
            dpg.add_text("Version 0.0.0.1", color=(200, 200, 200))
            dpg.add_separator()

            # Description
            dpg.add_text("A free, open-source platform for managing and analyzing scientific data.")
            dpg.add_text("RAS removes financial and technical barriers by providing a user-friendly")
            dpg.add_text("desktop application for researchers, educators, and professionals.")
            dpg.add_spacer(height=10)

            # Author Information
            dpg.add_text("Author Information:", color=(255, 255, 0))
            dpg.add_text("Author: Lane")
            dpg.add_text("Email: justlane@uw.edu")
            dpg.add_spacer(height=10)

            # License Information
            dpg.add_text("License:", color=(255, 255, 0))
            dpg.add_text("BSD 3-Clause License")
            dpg.add_spacer(height=10)

            # Links
            dpg.add_text("Links:", color=(255, 255, 0))
            dpg.add_button(
                label="GitHub Repository",
                callback=self._open_github,
                width=200
            )
            dpg.add_spacer(height=10)

            # System Information
            dpg.add_text("System Information:", color=(255, 255, 0))
            dpg.add_text(f"Platform: {platform.system()} {platform.release()}")
            dpg.add_text(f"Python: {platform.python_version()}")
            dpg.add_spacer(height=10)

            # Close button
            dpg.add_separator()
            with dpg.group(horizontal=True):
                dpg.add_button(label="Close", callback=self._close_dialog)

    def _open_github(self):
        """Opens the GitHub repository in the default web browser."""
        try:
            webbrowser.open("https://github.com/lane-neuro/research-analytics-suite")
            self._logger.info("Opened GitHub repository in browser")
        except Exception as e:
            self._logger.error(e, "Failed to open GitHub repository")

    def _close_dialog(self):
        """Closes the about dialog."""
        if dpg.does_item_exist(self._dialog_tag):
            dpg.delete_item(self._dialog_tag)

    def show(self):
        """Shows the about dialog."""
        self.draw()
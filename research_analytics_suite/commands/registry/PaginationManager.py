"""
PaginationManager Module

This module defines the PaginationManager class, which manages the pagination of displayed commands within the Research Analytics Suite.
It provides methods to navigate through pages of commands.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

class PaginationManager:
    """Class that manages the pagination of displayed commands."""

    def __init__(self, display_manager):
        """Initialize the PaginationManager with the display manager.

        Args:
            display_manager: The DisplayManager instance.
        """
        self._display_manager = display_manager
        self._current_page = 1
        self._page_size = 10

    def next_page(self):
        """Navigate to the next page of commands."""
        self._current_page += 1
        self._display_manager.display_commands(self._display_manager.current_category, self._display_manager.search,
                                               self._current_page)

    def previous_page(self):
        """Navigate to the previous page of commands."""
        if self._current_page > 1:
            self._current_page -= 1
        self._display_manager.display_commands(self._display_manager.current_category, self._display_manager.search,
                                               self._current_page)

    @property
    def current_page(self):
        """Get the current page number."""
        return self._current_page

    @property
    def page_size(self):
        """Get the page size."""
        return self._page_size

    @page_size.setter
    def page_size(self, size):
        """Set the page size.

        Args:
            size: The new page size.
        """
        self._page_size = size
        self._display_manager.display_commands(self._display_manager.current_category, self._display_manager.search,
                                               self._current_page)

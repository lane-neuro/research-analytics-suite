"""
concrete_display_interface Module

This module contains a concrete implementation of DisplayInterface for testing purposes.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

from typing import List, Dict

from research_analytics_suite.hardware_manager.interface.display.DisplayInterface import DisplayInterface


class ConcreteDisplayInterface(DisplayInterface):
    def detect(self) -> List[Dict[str, str]]:
        """Detect display interfaces."""
        return []

    def _get_command(self, action: str) -> List[str]:
        """Get the command to perform an action based on OS."""
        return []

    def _parse_output(self, output: str) -> List[Dict[str, str]]:
        """Parse the raw output to extract display information."""
        return []

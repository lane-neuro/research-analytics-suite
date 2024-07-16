"""
This module contains the classes that are used to manage the commands that are available to the user.

Author: Lane
"""

from .CommandDecorators import temp_command_registry, link_class_commands, command
from .utils.text_utils import clean_description
from research_analytics_suite.commands.registry import CommandRegistry
from .DefaultCommands import _help, resources, tasks, registry, _exit

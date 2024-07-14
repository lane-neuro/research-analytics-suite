"""
Default commands for the Research Analytics Suite.

This module contains default commands that are available to the user when interacting with the Research Analytics Suite.
These commands are registered with the CommandRegistry and can be executed dynamically based on user input.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import sys

from research_analytics_suite.commands import CommandRegistry, command
from research_analytics_suite.utils import CustomLogger


@command
def _help() -> None:
    """Displays available commands and their descriptions."""
    CommandRegistry().display_commands()


@command
async def _exit() -> None:
    """Exits the Research Analytics Suite."""
    try:
        from research_analytics_suite.data_engine import Workspace
        await Workspace().save_current_workspace()
    except Exception as e:
        CustomLogger().error(Exception(f"Error saving workspace: {e}"), 'exit')
    finally:
        sys.exit(0)


@command
async def clear() -> None:
    """Clears the search and keyword variables."""
    CommandRegistry().clear_search()
    CommandRegistry().clear_category()


@command
def registry() -> dict:
    """Displays the command registry."""
    return CommandRegistry().registry


@command
async def resources() -> None:
    """Displays system resources."""
    from research_analytics_suite.operation_manager import OperationControl
    for operation_list in OperationControl().sequencer.sequencer:
        operation_node = OperationControl().sequencer.get_head_operation_from_chain(operation_list)
        from research_analytics_suite.operation_manager.operations.system import ResourceMonitorOperation
        if isinstance(operation_node, ResourceMonitorOperation):
            CustomLogger().info(operation_node.output_memory_usage())


@command
async def tasks() -> None:
    """Displays all tasks."""
    from research_analytics_suite.operation_manager import OperationControl
    for task in OperationControl().task_creator.tasks:
        operation = OperationControl().sequencer.find_operation_by_task(task)
        if operation:
            CustomLogger().info(f"Task: {task.get_name()} - {operation.status}")


@command
async def sequencer() -> None:
    """Displays all operations in the sequencer."""
    from research_analytics_suite.operation_manager import OperationControl
    for sequencer_chain in OperationControl().sequencer.sequencer:
        operation = sequencer_chain.head.operation
        CustomLogger().info(f"Operation: {operation.task.get_name()} - {operation.status}")


@command
async def get_memory() -> dict:
    """Displays local vars."""
    from research_analytics_suite.data_engine import MemoryManager
    return await MemoryManager().list_collections()

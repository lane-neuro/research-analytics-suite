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
from research_analytics_suite.commands import command, CommandRegistry
from research_analytics_suite.operation_manager import OperationControl
from research_analytics_suite.utils import CustomLogger


@command
def ras_help() -> str:
    """Displays available commands and their descriptions."""
    commands_info = ["Available commands:"]
    for cmd, meta in CommandRegistry().registry.items():
        args_info = ", ".join([f"{arg['name']}: {arg['type'].__name__}" for arg in meta['args']])
        return_info = meta['return_type'].__name__ if meta['return_type'] else "None"
        doc = meta['func'].__doc__ or "No description available."
        if args_info:
            commands_info.append(f"{cmd}({args_info}) -> {return_info}: {doc}")
        else:
            commands_info.append(f"{cmd} -> {return_info}: {doc}")
    return "\n".join(commands_info)


@command
async def stop():
    """Stops all operations."""
    await OperationControl().operation_manager.stop_all_operations()
    return "Stopping all operations..."


@command
async def pause():
    """Pauses all operations."""
    await OperationControl().operation_manager.pause_all_operations()
    return "Pausing all operations..."


@command
async def resume():
    """Resumes all operations."""
    await OperationControl().operation_manager.resume_all_operations()
    return "Resuming all operations..."


@command
async def resources():
    """Displays system resources."""
    for operation_list in OperationControl().sequencer.sequencer:
        operation_node = OperationControl().sequencer.get_head_operation_from_chain(operation_list)
        from research_analytics_suite.operation_manager.operations.system import ResourceMonitorOperation
        if isinstance(operation_node, ResourceMonitorOperation):
            CustomLogger().info(operation_node.output_memory_usage())
    return "Displaying system resources."


@command
async def tasks():
    """Displays all tasks."""
    for task in OperationControl().task_creator.tasks:
        operation = OperationControl().sequencer.find_operation_by_task(task)
        if operation:
            CustomLogger().info(f"Task: {task.get_name()} - {operation.status}")
    return "Displaying all tasks..."


@command
async def sequencer():
    """Displays all operations in the sequencer."""
    for sequencer_chain in OperationControl().sequencer.sequencer:
        operation = sequencer_chain.head.operation
        CustomLogger().info(f"Operation: {operation.task.get_name()} - {operation.status}")
    return "Displaying all operations in the sequencer..."


@command
async def get_memory():
    """Displays local vars."""
    return "Displaying local vars..."
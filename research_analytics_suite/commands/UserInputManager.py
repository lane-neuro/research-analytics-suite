"""
UserInputManager Module.

This module defines the UserInputManager class, which processes user input from the console within the research
analytics suite. It handles various commands by dynamically discovering and executing them.

Author: Lane
"""
import inspect

from research_analytics_suite.commands import CommandRegistry
from research_analytics_suite.commands.CommandRegistry import command
from research_analytics_suite.operation_manager import OperationControl
from research_analytics_suite.utils import CustomLogger


class UserInputManager:
    """
    A class to process user input from the console.

    This class processes user input and executes corresponding commands dynamically.
    """

    def __init__(self):
        """
        Initializes the UserInputManager with the necessary components.
        """
        self._operation_control = OperationControl()
        self._logger = CustomLogger()
        self._command_registry = CommandRegistry()

    async def process_user_input(self, user_input: str) -> str:
        """
        Processes user input from the console and executes corresponding commands.

        Args:
            user_input (str): The user input to process.

        Returns:
            str: The response to the user input.
        """
        command_name, args = self.parse_command(user_input)
        if command_name:
            return await self.execute_command(command_name, args)
        else:
            return f"Unknown command: {user_input}"

    def parse_command(self, input_str):
        """
        Parses the user input into a command name and arguments.

        Args:
            input_str (str): The user input to parse.

        Returns:
            tuple: A tuple containing the command name and a list of arguments.
        """
        parts = input_str.strip().split()
        if not parts:
            return None, []
        return parts[0], parts[1:]

    async def execute_command(self, command_name, args):
        """
        Executes the specified command with the given arguments.

        Args:
            command_name (str): The name of the command to execute.
            args (list): The arguments to pass to the command.

        Returns:
            str: The result of the command execution.
        """
        if command_name in self._command_registry.registry.keys():
            try:
                meta = self._command_registry.registry[command_name]
                func = meta['func']
                expected_args = meta['args']
                if len(expected_args) == len(args):
                    # Convert args to the expected types
                    converted_args = []
                    for arg, expected_arg in zip(args, expected_args):
                        arg_type = expected_arg['type']
                        converted_args.append(arg_type(arg))
                    if inspect.ismethod(func) or 'self' in inspect.signature(func).parameters:
                        result = func(self, *converted_args)  # Handle method
                    else:
                        result = func(*converted_args)  # Handle function
                    if inspect.isawaitable(result):
                        result = await result
                    return result
                else:
                    return f"Error: {command_name} expects {len(expected_args)} arguments but got {len(args)}."
            except Exception as e:
                self._logger.error(Exception(f"Error executing command '{command_name}': {e}"), self.__class__.__name__)
                return f"Error executing command '{command_name}': {e}"
        else:
            return f"Error: Unknown command '{command_name}'. Type 'help' to see available commands."

    @command
    def help(self) -> str:
        """Displays available commands and their descriptions."""
        commands_info = ["Available commands:"]
        for cmd, meta in self._command_registry.registry.items():
            args_info = ", ".join([f"{arg['name']}: {arg['type'].__name__}" for arg in meta['args']])
            return_info = meta['return_type'].__name__ if meta['return_type'] else "None"
            doc = meta['func'].__doc__ or "No description available."
            commands_info.append(f"{cmd}({args_info}) -> {return_info}: {doc}")
        return "\n".join(commands_info)


# Register default commands
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

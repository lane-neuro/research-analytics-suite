"""
UserInputManager Module

This module contains the UserInputManager class, which processes user input from the console and executes
corresponding commands dynamically.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import inspect

from research_analytics_suite.commands import CommandRegistry, command
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

    async def process_user_input(self, user_input: str, runtime_id: str = None) -> str:
        """
        Processes user input from the console and executes corresponding commands.

        Args:
            user_input (str): The user input to process.
            runtime_id (str): The runtime ID for instance-specific commands (optional).

        Returns:
            str: The response to the user input.
        """
        command_name, args = self.parse_command(user_input)
        if command_name:
            return await self.execute_command(command_name, args, runtime_id)
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

    async def execute_command(self, command_name, args, runtime_id=None):
        """
        Executes the specified command with the given arguments.

        Args:
            command_name (str): The name of the command to execute.
            args (list): The arguments to pass to the command.
            runtime_id (str): The runtime ID for instance-specific commands (optional).

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
                    result = self._command_registry.execute_command(command_name, runtime_id, *converted_args)
                    if inspect.isawaitable(result):
                        result = await result
                    return result
                else:
                    return f"Error: {command_name} expects {len(expected_args)} arguments but got {len(args)}."
            except Exception as e:
                self._logger.error(Exception(f"Error executing command '{command_name}': {e}"), self.__class__.__name__)
                return f"Error executing command '{command_name}': {e}"
        else:
            return f"Error: Unknown command '{command_name}'. Type 'ras_help' to see available commands."


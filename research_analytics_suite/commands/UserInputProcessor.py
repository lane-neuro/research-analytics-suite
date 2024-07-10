"""
UserInputProcessor

This module contains the UserInputProcessor class, which processes user input from the console and executes
corresponding commands.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from research_analytics_suite.commands import CommandRegistry
from research_analytics_suite.utils import CustomLogger


def parse_command(input_str):
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


async def process_user_input(user_input: str, runtime_id: str = None):
    """
    Processes user input from the console and executes corresponding commands.

    Args:
        user_input (str): The user input to process.
        runtime_id (str): The runtime ID for instance-specific commands (optional).

    Returns:
        str: The response to the user input.
    """
    command_name, args = parse_command(user_input)
    if command_name:
        return await CommandRegistry().execute_command(name=command_name, runtime_id=runtime_id, args=args)
    else:
        CustomLogger().error(Exception(f"Error: Unknown command '{user_input}'. Type 'ras_help' to see "
                                       f"available commands."), "UserInputProcessor")

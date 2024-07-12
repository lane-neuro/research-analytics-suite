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


async def process_user_input(user_input, runtime_id=None):
    from research_analytics_suite.utils import CustomLogger
    from research_analytics_suite.commands import CommandRegistry

    if not isinstance(user_input, str):
        raise AttributeError("user_input must be a string")

    original_input = user_input
    user_input = user_input.strip()
    if not user_input:
        CustomLogger().error(Exception(f"Error: Unknown command '{original_input}'. "
                                       f"Type '_help' to see available commands."), "UserInputProcessor")
        return None

    # Parse command and arguments
    parts = []
    current_part = []
    in_quotes = False
    quote_char = None

    for char in user_input:
        if char in ('"', "'"):
            if in_quotes:
                if char == quote_char:
                    in_quotes = False
                    parts.append(''.join(current_part))
                    current_part = []
                else:
                    current_part.append(char)
            else:
                in_quotes = True
                quote_char = char
        elif char.isspace():
            if in_quotes:
                current_part.append(char)
            else:
                if current_part:
                    parts.append(''.join(current_part))
                    current_part = []
        else:
            current_part.append(char)

    if current_part:
        parts.append(''.join(current_part))

    if not parts:
        CustomLogger().error(Exception(f"Error: Unknown command '{original_input}'. "
                                       f"Type '_help' to see available commands."), "UserInputProcessor")
        return None

    command_name = parts[0]
    args = parts[1:]

    try:
        return await CommandRegistry().execute_command(command_name, runtime_id, *args)
    except Exception as e:
        CustomLogger().error(e, "UserInputProcessor")
        raise e

"""
ConsoleMonitor Module

The ConsoleMonitor class is designed to handle user-input action from the console. It provides methods for
displaying a prompt for user input and processing the input action.

Author: Lane
Copyright: Lane
Credits: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import asyncio

import aioconsole
import sys
from research_analytics_suite.commands.UserInputProcessor import process_user_input
from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation


class ConsoleMonitor(BaseOperation):
    """
    A class used to represent a Console Operation in the Research Analytics Suite.

    This class provides methods for displaying a prompt for user input and processing the input data.
    """
    name = "sys_ConsoleMonitor"
    version = "0.0.1"
    description = "Handles user input from the console."
    category_id = -1
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {}
    parent_operation = None
    inheritance = []
    is_loop = True
    is_cpu_bound = False
    parallel = True

    def __init__(self, *args, **kwargs):
        """
        Initializes the ConsoleMonitor with a prompt for user input and the action to be processed.

        Args:
            prompt (str): A string that is displayed as a prompt for user input.
        """
        self._prompt = kwargs.pop("prompt", "\n\t>>\t")

        from research_analytics_suite.commands import CommandRegistry
        self._command_registry = CommandRegistry()

        super().__init__(*args, **kwargs)

    async def initialize_operation(self) -> None:
        """Initializes the operation."""
        await super().initialize_operation()
        self.is_ready = True

    async def execute(self) -> None:
        """Processes user input and sends it to the operation handler."""
        input_task = None  # Track the input task

        while self.is_loop:
            if input_task is None:
                if 'ipykernel' in sys.modules:
                    # Jupyter Notebook environment
                    print(self._prompt)
                    user_input = input()  # Use standard input in Jupyter Notebook
                    user_input = user_input.strip()  # Strip newline
                    if user_input:
                        self.add_log_entry(f"User input: {user_input}")
                        await process_user_input(user_input)
                else:
                    input_task = asyncio.create_task(aioconsole.ainput(self._prompt))  # Read user input asynchronously

            if input_task is not None and input_task.done():
                try:
                    user_input = input_task.result().strip()  # Get the result from the input task and strip newline

                    if user_input == "":  # Check for empty input
                        continue

                    self.add_log_entry(f"User input: {user_input}")

                    await process_user_input(user_input)

                except EOFError:
                    self.handle_error(Exception("EOFError: No input provided"))
                    break
                except UnicodeDecodeError as e:  # Catch specific exception
                    self.handle_error(e)
                except Exception as e:  # Catch all other exceptions
                    self.handle_error(e)
                    break
                finally:
                    input_task = None  # Reset input task

            await asyncio.sleep(0.01)  # Sleep for a short duration to avoid busy-waiting

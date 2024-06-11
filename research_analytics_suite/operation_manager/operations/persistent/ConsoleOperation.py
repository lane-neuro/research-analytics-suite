"""
A module that defines the ConsoleOperation class, which is a subclass of the CustomOperation class.

The ConsoleOperation class is designed to handle user-input _func from the console. It provides methods for
displaying a prompt for user input and processing the input _func.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import aioconsole

from research_analytics_suite.operation_manager.operations.ABCOperation import ABCOperation


class ConsoleOperation(ABCOperation):
    """
    A class used to represent a Console Operation in the Research Analytics Suite.

    This class provides methods for displaying a prompt for user input and processing the input data.
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the ConsoleOperation with a prompt for user input and the _func to be processed.

        Args:
            prompt (str): A string that is displayed as a prompt for user input.
            data (str): A formatted string to print out the _func that the operations will process.
        """
        self._prompt = kwargs.pop("prompt", "Enter a command: ")
        self._user_input_manager = kwargs.pop("user_input_manager")

        super().__init__(*args, **kwargs, name="sys_ConsoleOperation")

    async def execute(self) -> None:
        """Processes user input and sends it to the operation handler."""
        self._status = "running"
        self.add_log_entry(f"[RUN] {self._name}")

        while True:  # Loop until a specific user input is received
            try:
                user_input = await aioconsole.ainput(self._prompt)  # Read user input
                user_input = user_input.strip()  # strip newline

                if user_input == "":  # Check for empty input
                    continue

                self.add_log_entry(f"User input: {user_input}")

                if user_input == "exit":  # Exit condition
                    self._status = "stopped"
                    break

                await self._user_input_manager.process_user_input(user_input)
            except UnicodeDecodeError as e:  # Catch specific exception
                self._handle_error(e)
            except Exception as e:  # Catch all other exceptions
                self._handle_error(e)
                break

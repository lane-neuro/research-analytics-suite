"""
A module that defines the ConsoleOperation class, which is a subclass of the CustomOperation class.

The ConsoleOperation class is designed to handle user-input action from the console. It provides methods for
displaying a prompt for user input and processing the input action.

Author: Lane
"""
import aioconsole
import sys

from research_analytics_suite.commands.UserInputProcessor import process_user_input
from research_analytics_suite.operation_manager import BaseOperation


class ConsoleOperation(BaseOperation):
    """
    A class used to represent a Console Operation in the Research Analytics Suite.

    This class provides methods for displaying a prompt for user input and processing the input data.
    """
    def __init__(self, *args, **kwargs):
        """
        Initializes the ConsoleOperation with a prompt for user input and the action to be processed.

        Args:
            prompt (str): A string that is displayed as a prompt for user input.
            user_input_manager (UserInputManager): An instance of UserInputManager to process user input.
        """
        from research_analytics_suite.commands import CommandRegistry
        self._command_registry = CommandRegistry()

        self._prompt = "\n\t>>\t"
        kwargs["name"] = "sys_ConsoleOperation"

        super().__init__(*args, **kwargs)

    async def initialize_operation(self) -> None:
        """Initializes the operation."""
        await super().initialize_operation()
        self.is_ready = True

    async def execute(self) -> None:
        """Processes user input and sends it to the operation handler."""
        self._status = "running"
        self.add_log_entry(f"[RUN] {self._name}")

        while self.parallel and self.is_loop:  # Loop until a specific user input is received
            try:
                if 'ipykernel' in sys.modules:
                    # Jupyter Notebook environment
                    print(self._prompt)
                    user_input = input()  # Use standard input in Jupyter Notebook
                else:
                    # Standard terminal environment
                    user_input = await aioconsole.ainput(self._prompt)  # Read user input asynchronously

                user_input = user_input.strip()  # Strip newline

                if user_input == "":  # Check for empty input
                    continue

                self.add_log_entry(f"User input: {user_input}")

                if user_input == "exit":  # Exit condition
                    self._status = "stopped"
                    break

                result = await process_user_input(user_input)
                self._logger.info(result)

            except EOFError:
                self.handle_error("EOFError: No input provided")
                break
            except UnicodeDecodeError as e:  # Catch specific exception
                self.handle_error(e)
            except Exception as e:  # Catch all other exceptions
                self.handle_error(e)
                break

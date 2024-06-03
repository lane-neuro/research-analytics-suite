"""
A module that defines the CustomOperation class, a subclass of the ABCOperation class.

The CustomOperation class is designed to handle custom operations that require function processing. It provides methods
for setting the function to be processed and executing the operation.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import types
from typing import Tuple
from neurobehavioral_analytics_suite.operation_manager.operation.Operation import Operation
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler


class CustomOperation(Operation):
    """A class used to represent a Custom Operation in the NeuroBehavioral Analytics Suite.

    This class provides methods for setting the data to be processed and executing the operation.

    Attributes:
        func (callable): A function to be executed.
        error_handler (ErrorHandler): An instance of ErrorHandler to handle any exceptions that occur.
    """

    def __init__(self, error_handler: ErrorHandler, func, local_vars=None, name: str = "CustomOperation",
                 persistent: bool = False):
        """Initializes the CustomOperation with the function to be processed and an ErrorHandler instance.

        Args:
            error_handler (ErrorHandler): An instance of ErrorHandler to handle any exceptions that occur.
            func: A function to be executed.
            local_vars (dict): Local variables to be used in the function execution.
            name (str): The name of the operation.
        """
        super().__init__(name=name, error_handler=error_handler, func=func, persistent=persistent)
        if local_vars is None:
            local_vars = locals()
        if local_vars is None:
            local_vars = {}
        self.func = func
        self.error_handler = error_handler
        self.local_vars = local_vars
        self.task = None
        self.persistent = persistent
        self.name = name
        self._status = "idle"
        self.type = type(self)
        self.result_output = None

    def init_operation(self):
        """
        Initialize any resources or setup required for the operation before it starts.
        """
        super().init_operation()

    async def start(self):
        """Starts the operation and updates the status accordingly."""
        await super().start()

    async def execute(self):
        """Executes the operation and updates the status and result output accordingly.

        Returns:
            dict: The result output after function execution.
        """
        temp_vars = self.local_vars.copy()

        try:
            if isinstance(self.func, str):  # If self.func is a string of code
                code = self.func
                self.func = lambda: exec(code, {}, temp_vars)
            elif callable(self.func):  # If self.func is a callable function
                if isinstance(self.func, types.MethodType):  # If self.func is a bound method
                    self.func = self.func
                else:
                    func = self.func
                    self.func = lambda: func()
            else:
                raise TypeError("self.func must be a string of Python code, a callable function, or a bound method.")

            await super().execute()
        except Exception as e:
            self.error_handler.handle_error(e, self)
            self._status = "error"
        finally:
            self.result_output = temp_vars
            self.local_vars = temp_vars
            return self.result_output

    def get_result(self):
        """
        Gets the result of the operation.

        Returns:
            The result of the operation.
        """
        return self.result_output

    async def pause(self):
        """Pauses the operation and updates the status accordingly."""
        await super().pause()

    async def resume(self) -> None:
        """Resumes the operation and updates the status accordingly."""
        await super().resume()

    async def stop(self):
        """Stops the operation and updates the status accordingly."""
        await super().stop()

    async def reset(self) -> None:
        """Resets the operation and updates the status accordingly."""
        await super().reset()

    async def restart(self):
        """Restarts the operation and updates the status accordingly."""
        await super().restart()

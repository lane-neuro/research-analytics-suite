"""
A module that defines the CustomOperation class, a subclass of the Operation class.

The CustomOperation class is designed to handle custom operations that require function processing. It provides methods
for setting the function to be processed and executing the operations.

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
from neurobehavioral_analytics_suite.operation_manager.operations.Operation import Operation
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler


class CustomOperation(Operation):
    """
    A class used to represent a Custom Operation in the NeuroBehavioral Analytics Suite.

    This class provides methods for setting the data to be processed and executing the operations.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the custom operation instance.

        Args:
            error_handler (ErrorHandler): The error handler for managing errors.
            func (callable, optional): The function to be executed by the operation.
            name (str, optional): The name of the operation. Defaults to "CustomOperation".
            persistent (bool, optional): Whether the operation should run indefinitely. Defaults to False.
            is_cpu_bound (bool, optional): Whether the operation is CPU-bound. Defaults to False.
            concurrent (bool, optional): Whether child operations should run concurrently. Defaults to False.
            parent_operation (ABCOperation, optional): The parent operation. Defaults to None.
            local_vars (dict, optional): Local variables for the function execution. Defaults to None.
        """
        super().__init__(*args, **kwargs)

    def init_operation(self):
        """
        Initialize any resources or setup required for the operations before it starts.
        """
        super().init_operation()

    async def _execute_func(self):
        """
        Execute the function associated with the operation.

        Returns:
            dict: The result output after function execution.
        """
        temp_vars = self._local_vars.copy()
        try:
            if isinstance(self._func, str):  # If self._func is a string of code
                code = self._func
                self._func = lambda: exec(code, {}, temp_vars)
            elif callable(self._func):  # If self._func is a callable function
                if isinstance(self._func, types.MethodType):  # If self._func is a bound method
                    self._func = self._func
                else:
                    func = self._func
                    self._func = lambda: func()
            else:
                raise TypeError("self._func must be a string of Python code, a callable function, or a bound method.")
            await super()._execute_func()
        except Exception as e:
            self._handle_error(e)
        finally:
            self._result_output = temp_vars
            self._local_vars = temp_vars

    def get_result(self):
        """
        Retrieve the result of the operation, if applicable.

        Returns:
            The result of the operation.
        """
        return self._result_output

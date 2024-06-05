"""
A module that defines the Operation class, which is responsible for managing tasks.

The Operation class represents a task that can be started, stopped, paused, resumed, and reset. It also tracks the
progress of the task and handles any exceptions that occur during execution.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

import asyncio
from concurrent.futures import ProcessPoolExecutor
from neurobehavioral_analytics_suite.operation_manager.operations.ABCOperation import ABCOperation
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler


class Operation(ABCOperation):
    """
    An Operation class that defines a common interface for all operations, inherited from ABCOperation.

    This class requires that any child class implement the execute, start, pause, stop, and resume methods.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the operation instance.

        Args:
            error_handler (ErrorHandler): The error handler for managing errors.
            func (callable, optional): The function to be executed by the operation.
            name (str, optional): The name of the operation. Defaults to "Operation".
            local_vars (dict, optional): Local variables for the function execution. Defaults to None.
            persistent (bool, optional): Whether the operation should run indefinitely. Defaults to False.
            is_cpu_bound (bool, optional): Whether the operation is CPU-bound. Defaults to False.
            concurrent (bool, optional): Whether child operations should run concurrently. Defaults to False.
            parent_operation (ABCOperation, optional): The parent operation. Defaults to None.
        """
        super().__init__(*args, **kwargs)

    def init_operation(self):
        """
        Initialize any resources or setup required for the operation before it starts.
        """
        pass

    async def _execute_func(self):
        """
        Execute the function associated with the operation.
        """
        if self._is_cpu_bound:
            with ProcessPoolExecutor() as executor:
                self._result_output = executor.submit(self._func).result()
        else:
            if asyncio.iscoroutinefunction(self._func):
                self._result_output = await self._func()
            else:
                self._result_output = await asyncio.get_event_loop().run_in_executor(None, self._func)

    def get_result(self):
        """
        Retrieve the result of the operation, if applicable.

        Returns:
            The result of the operation.
        """
        return self._result_output

    def cleanup_operation(self):
        """
        Clean up any resources or perform any necessary teardown after the operation has completed or been stopped.
        """
        super().cleanup_operation()

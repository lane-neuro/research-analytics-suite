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
from research_analytics_suite.operation_manager.operations.ABCOperation import ABCOperation


class Operation(ABCOperation):
    """
    An Operation class that defines a common interface for all operations, inherited from ABCOperation.

    This class requires that any child class implement the execute, start, pause, stop, and resume methods.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the operation instance.

        Args:
            func (callable, optional): The function to be executed by the operation.
            name (str, optional): The name of the operation. Defaults to "Operation".
            local_vars (dict, optional): Local variables for the function execution. Defaults to None.
            persistent (bool, optional): Whether the operation should run indefinitely. Defaults to False.
            is_cpu_bound (bool, optional): Whether the operation is CPU-bound. Defaults to False.
            concurrent (bool, optional): Whether child operations should run concurrently. Defaults to False.
            parent_operation (ABCOperation, optional): The parent operation. Defaults to None.
        """
        super().__init__(*args, **kwargs)

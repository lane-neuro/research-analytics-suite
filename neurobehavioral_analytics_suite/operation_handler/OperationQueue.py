"""
A module that defines the OperationQueue class, which manages and executes Operation instances asynchronously in the
NeuroBehavioral Analytics Suite.

The OperationQueue class provides methods for adding operations to the queue, executing operations, and managing the
queue. It also sets up the Dask client for executing tasks and the asyncio event loop.

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
from dask.distributed import Client
from collections import deque
from typing import Optional

from neurobehavioral_analytics_suite.operation_handler.BaseOperation import BaseOperation
from neurobehavioral_analytics_suite.operation_handler.ConsoleOperation import ConsoleOperation
from neurobehavioral_analytics_suite.operation_handler.Operation import Operation
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler


class OperationQueue:
    """
    A class for managing and executing Operation instances.

    This class provides methods for adding operations to the queue, executing operations, and managing the queue. It
    also sets up the Dask client for executing tasks and the asyncio event loop.

    Attributes:
        queue (deque): A deque for storing Operation instances.
        error_handler (ErrorHandler): An instance of ErrorHandler to handle any exceptions that occur.
        client (Client): A Dask distributed client for executing tasks.
    """

    def __init__(self, error_handler: ErrorHandler = ErrorHandler()):
        """
        Initializes the OperationQueue with an empty deque, an ErrorHandler instance, a list for persistent tasks, and
        a Dask client.

        Args:
            error_handler (ErrorHandler): An instance of ErrorHandler to handle any exceptions that occur.
        """

        self.queue = deque()
        self.error_handler = error_handler
        self.console = None
        self.client = Client()

    def add_operation(self, operation: BaseOperation) -> None:
        """
        Adds an Operation instance to the queue.

        Args:
            operation (Operation): The Operation instance to add.
        """

        if operation.task and not operation.task.done():
            # print(f"add_operation: {operation} is already running")
            return
        self.queue.append(operation)
        # print(f"add_operation: {operation} added to queue")

    def add_console_operation(self, console: ConsoleOperation) -> None:
        """
        Adds a ConsoleOperation instance to the tasks list.
        """
        if self.console and self.console.task and not self.console.task.done():
            # print(f"add_console_operation: {self.console} is already running")
            return
        self.console = console
        self.add_operation(self.console)

    def remove_operation(self, operation: BaseOperation) -> None:
        """
        Removes a specific Operation instance from the queue.

        Args:
            operation (Operation): The Operation instance to remove.
        """
        if operation.task and not operation.task.done():
            # print(f"remove_operation: Operation: {operation.task.get_name()} is still running")
            return
        operation.stop()
        self.queue.remove(operation)

    def get_operation(self, index: int) -> Operation:
        """
        Returns a specific Operation instance from the queue based on its index.

        Args:
            index (int): The index of the Operation instance to return.

        Returns:
            Operation: The Operation instance at the specified index.
        """

        return self.queue[index]

    def get_operation_by_task(self, task: asyncio.Task) -> Optional[Operation]:
        """
        Returns the Operation instance associated with a specific task.

        Args:
            task (asyncio.Task): The task to find the associated Operation instance for.

        Returns:
            Operation: The Operation instance associated with the task.
        """

        for operation in self.queue:
            if operation.task == task:
                return operation
        return None

    def insert_operation(self, index, operation) -> None:
        """
        Inserts an Operation instance at a specific position in the queue.

        Args:
            index (int): The position at which to insert the Operation instance.
            operation (Operation): The Operation instance to insert.
        """

        self.queue.insert(index, operation)

    def is_empty(self) -> bool:
        """
        Checks if the queue is empty.

        Returns:
            bool: True if the queue is empty, False otherwise.
        """
        return len(self.queue) == 0

    def size(self) -> int:
        """
        Returns the number of operations in the queue.

        Returns:
            int: The number of operations in the queue.
        """

        return len(self.queue)

    def peek(self) -> Operation:
        """
        Returns the operation at the front of the queue without removing it.

        Returns:
            Operation: The operation at the front of the queue.
        """

        return self.queue[0]

    def clear(self) -> None:
        """
        Removes all operations from the queue.
        """

        self.queue.clear()

    def contains(self, operation) -> bool:
        """
        Checks if an operation is in the queue.

        Args:
            operation (Operation): The operation to check.

        Returns:
            bool: True if the operation is in the queue, False otherwise.
        """
        return operation in self.queue

    def has_pending_operations(self) -> bool:
        """
        Checks if there are any pending operations in the queue.

        Returns:
            bool: True if there are pending operations, False otherwise.
        """
        return any(operation.status == "pending" for operation in self.queue)

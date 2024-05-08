"""
A module for the OperationQueue class, which manages and executes Operation instances asynchronously in the
NeuroBehavioral Analytics Suite.

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
import nest_asyncio
from dask.distributed import Client
from collections import deque


class OperationQueue:
    """
    A queue for managing and executing Operation instances.

    Attributes:
        queue (deque): A deque for storing Operation instances.
        client (Client): A Dask distributed client for executing tasks.
    """

    def __init__(self):
        """
        Initializes the OperationQueue.

        The queue is initially empty.
        The Dask client is created with default parameters.
        """

        self.queue = deque()
        self.client = Client()

    def add_operation(self, operation):
        """
        Adds an Operation instance to the queue.

        Args:
            operation (Operation): The Operation instance to add.
        """

        self.queue.append(operation)

    async def execute_all(self):
        """
        Executes all Operation instances in the queue.

        This method uses the Dask client to execute the operations asynchronously.
        It waits for all operations to complete before returning.
        """

        # Apply the nest_asyncio patch to enable nested use of asyncio's event loop
        nest_asyncio.apply()

        # Create a list of tasks for asyncio to monitor
        tasks = [self.client.submit(operation.execute) for operation in self.queue]

        # Wait for the tasks to complete
        await asyncio.gather(*tasks)

        # Clear the queue
        self.queue.clear()

    async def execute_operation(self, operation):
        """
        Executes a single Operation in the queue.
        """

        # Apply the nest_asyncio patch to enable nested use of asyncio's event loop
        nest_asyncio.apply()

        # Create a task for the operation
        task = self.client.submit(operation.start)

        await asyncio.gather(task)

    def remove_operation(self, operation):
        """
        Removes a specific Operation instance from the queue.

        Args:
            operation (Operation): The Operation instance to remove.
        """
        self.queue.remove(operation)

    def get_operation(self, index):
        """
        Returns a specific Operation instance from the queue based on its index.

        Args:
            index (int): The index of the Operation instance to return.

        Returns:
            Operation: The Operation instance at the specified index.
        """
        return self.queue[index]

    def insert_operation(self, index, operation):
        """
        Inserts an Operation instance at a specific position in the queue.

        Args:
            index (int): The position at which to insert the Operation instance.
            operation (Operation): The Operation instance to insert.
        """
        self.queue.insert(index, operation)

    def is_empty(self):
        """
        Checks if the queue is empty.

        Returns:
            bool: True if the queue is empty, False otherwise.
        """
        return len(self.queue) == 0

    def size(self):
        """
        Returns the number of operations in the queue.

        Returns:
            int: The number of operations in the queue.
        """
        return len(self.queue)

    def peek(self):
        """
        Returns the operation at the front of the queue without removing it.

        Returns:
            Operation: The operation at the front of the queue.
        """
        return self.queue[0]

    def clear(self):
        """
        Removes all operations from the queue.
        """
        self.queue.clear()

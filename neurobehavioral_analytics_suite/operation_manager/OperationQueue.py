"""
OperationQueue Module.

This module defines the OperationQueue class, which manages a queue of operations within the neurobehavioral analytics
suite. It provides methods to add, remove, move, and retrieve operations in the queue, ensuring efficient management
and execution of operations.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

from collections import deque
from typing import Optional, Any
from neurobehavioral_analytics_suite.operation_manager.operations.Operation import Operation
from neurobehavioral_analytics_suite.operation_manager.OperationChain import OperationChain


class OperationQueue:
    """
    A class to manage a queue of operations.

    This class provides methods to add, remove, move, & retrieve operations in the queue, ensuring efficient management
    and execution of operations.
    """

    def __init__(self, logger, error_handler):
        """
        Initializes the OperationQueue with a logger and error handler.

        Args:
            logger: Logger instance for logging messages.
            error_handler: Error handler for managing errors.
        """
        self.queue = deque()
        self.logger = logger
        self.error_handler = error_handler

    async def add_operation_to_queue(self, operation: Operation) -> Operation:
        """
        Adds an operation to the queue.

        Args:
            operation (Operation): The operation to add to the queue.

        Returns:
            Operation: The added operation.
        """
        if operation.parent_operation is None:
            if not isinstance(operation, OperationChain):
                operation = OperationChain(operation)
            self.queue.append(operation)
        else:
            op_head = self.get_chain_by_operation(operation.parent_operation)
            if op_head:
                op_head.add_operation_to_chain(operation)

        return self.get_operation_in_chain(self.get_chain_by_operation(operation), operation)

    def insert_operation_in_chain(self, index: int, operation_chain: OperationChain, operation: Operation) -> None:
        """
        Inserts an operation in a chain at a specific index.

        Args:
            index (int): The index at which to insert the operation.
            operation_chain (OperationChain): The operation chain to insert the operation into.
            operation (Operation): The operation to insert.
        """
        if isinstance(operation_chain, OperationChain):
            current_node = operation_chain.head
            for i in range(index):
                if current_node:
                    current_node = current_node.next_node
            if current_node:
                current_node.operation = operation

    def remove_operation_from_chain(self, operation_chain: OperationChain, operation: Operation) -> None:
        """
        Removes an operation from a chain.

        Args:
            operation_chain (OperationChain): The operation chain to remove the operation from.
            operation (Operation): The operation to remove.
        """
        if isinstance(operation_chain, OperationChain):
            operation_chain.remove_operation(operation)
            if operation_chain.is_empty():
                self.queue.remove(operation_chain)

    def move_operation(self, operation: Operation, new_index: int) -> None:
        """
        Moves an operation to a new index in its chain.

        Args:
            operation (Operation): The operation to move.
            new_index (int): The new index to move the operation to.
        """
        operation_chain = self.get_chain_by_operation(operation)
        if operation_chain:
            operation_chain.remove_operation(operation)
            self.insert_operation_in_chain(new_index, operation_chain, operation)

    def remove_operation_from_queue(self, operation: Operation) -> None:
        """
        Removes an operation from the queue.

        Args:
            operation (Operation): The operation to remove.
        """
        if isinstance(operation, OperationChain):
            self.queue.remove(operation)
        elif isinstance(operation, Operation):
            operation_chain = next((op for op in self.queue if op.head.operation == operation), None)
            if operation_chain:
                operation_chain.remove_operation(operation)
                if operation_chain.is_empty():
                    self.queue.remove(operation_chain)

    def get_head_operation_from_chain(self, operation_chain: OperationChain) -> Operation:
        """
        Gets the head operation from a chain.

        Args:
            operation_chain (OperationChain): The operation chain to get the head operation from.

        Returns:
            Operation: The head operation.
        """
        if isinstance(operation_chain, OperationChain):
            return operation_chain.head.operation

    def get_chain_by_operation(self, operation: Operation) -> OperationChain:
        """
        Gets the operation chain that contains a specific operation.

        Args:
            operation (Operation): The operation to find the chain for.

        Returns:
            OperationChain: The operation chain that contains the operation.
        """
        return next((op for op in self.queue if op.head.operation == operation), None)

    def get_operation_in_chain(self, operation_chain: OperationChain, operation: Operation) -> Operation:
        """
        Gets a specific operation in a chain.

        Args:
            operation_chain (OperationChain): The operation chain to search.
            operation (Operation): The operation to find.

        Returns:
            Operation: The found operation.
        """
        if isinstance(operation_chain, OperationChain):
            current_node = operation_chain.head
            while current_node:
                if current_node.operation == operation:
                    return current_node.operation
                current_node = current_node.next_node

    def get_operation_by_type(self, operation_type: type):
        """
        Gets an operation of a specific type.

        Args:
            operation_type (type): The type of operation to find.

        Returns:
            Operation: The found operation.
        """
        for operation_chain in self.queue:
            for node in operation_chain:
                if isinstance(type(node.operation), operation_type):
                    return node.operation
        self.logger.error(f"No operation found of type {operation_type.__name__}")

    def find_operation_by_task(self, task) -> Operation:
        """
        Finds an operation by its associated task.

        Args:
            task: The task associated with the operation to find.

        Returns:
            Operation: The found operation.
        """
        for operation_chain in self.queue:
            for node in operation_chain:
                if node.operation.task == task:
                    return node.operation
        self.logger.error(f"No operation found for task {task}")

    def is_empty(self) -> bool:
        """
        Checks if the queue is empty.

        Returns:
            bool: True if the queue is empty, False otherwise.
        """
        return len(self.queue) == 0

    def size(self) -> int:
        """
        Gets the size of the queue.

        Returns:
            int: The size of the queue.
        """
        return len(self.queue)

    def clear(self) -> None:
        """Clears the queue."""
        self.queue.clear()

    def contains(self, operation: Operation) -> bool:
        """
        Checks if the queue contains a specific operation.

        Args:
            operation (Operation): The operation to check for.

        Returns:
            bool: True if the queue contains the operation, False otherwise.
        """
        if isinstance(operation, OperationChain):
            return operation in self.queue
        elif isinstance(operation, Operation):
            return any(op.head.operation == operation for op in self.queue)

    async def has_waiting_operations(self) -> bool:
        """
        Checks if the queue has any waiting operations.

        Returns:
            bool: True if the queue has waiting operations, False otherwise.
        """
        return any(await self.get_head_operation_from_chain(op).status == "waiting" for op in self.queue)

    async def dequeue(self) -> Optional[Any]:
        """
        Dequeues the first operation chain from the queue.

        Returns:
            OperationChain: The dequeued operation chain, or None if the queue is empty.
        """
        if self.is_empty():
            return None
        return self.queue.popleft()

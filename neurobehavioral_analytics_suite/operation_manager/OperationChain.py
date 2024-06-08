"""
OperationChain Module.

This module defines the OperationChain class, which manages a chain of operations within the neurobehavioral analytics 
suite. It allows adding and removing operations, checking if the chain is empty, counting the operations, and iterating 
over the chain.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from neurobehavioral_analytics_suite.operation_manager.OperationNode import OperationNode
from neurobehavioral_analytics_suite.operation_manager.operations.ABCOperation import ABCOperation


class OperationChain:
    """
    A class to manage a chain of operations.

    This class provides methods to add and remove operations, check if the chain is empty, count the operations,
    and iterate over the chain of operations.
    """

    def __init__(self, operation: ABCOperation = None):
        """
        Initializes the OperationChain with an optional initial operation.

        Args:
            operation (Operation, optional): An initial operation to add to the chain. Defaults to None.
        """
        self.head = None
        if isinstance(operation, ABCOperation):
            self.add_operation_to_chain(operation)

    def add_operation_to_chain(self, operation: ABCOperation) -> None:
        """
        Adds an operation to the end of the chain.

        Args:
            operation (Operation): The operation to add to the chain.
        """
        if not self.head:
            self.head = OperationNode(operation)
        else:
            current_node = self.head
            while current_node.next_node:
                current_node = current_node.next_node
            current_node.next_node = OperationNode(operation)

    def remove_operation(self, operation: ABCOperation) -> None:
        """
        Removes an operation from the chain.

        Args:
            operation (Operation): The operation to remove from the chain.
        """
        if self.head and self.head.operation == operation:
            self.head = self.head.next_node
        else:
            current_node = self.head
            while current_node and current_node.next_node:
                if current_node.next_node.operation == operation:
                    current_node.next_node = current_node.next_node.next_node
                    break
                current_node = current_node.next_node

    def is_empty(self) -> bool:
        """
        Checks if the chain is empty.

        Returns:
            bool: True if the chain is empty, False otherwise.
        """
        return not self.head

    def count_operations(self) -> int:
        """
        Counts the number of operations in the chain.

        Returns:
            int: The number of operations in the chain.
        """
        count = 0
        current_node = self.head
        while current_node:
            count += 1
            current_node = current_node.next_node
        return count

    def contains(self, operation: ABCOperation) -> bool:
        """
        Checks if the chain contains a specific operation.

        Args:
            operation (Operation): The operation to check for.

        Returns:
            bool: True if the chain contains the operation, False otherwise.
        """
        current_node = self.head
        while current_node:
            if current_node.operation == operation:
                return True
            current_node = current_node.next_node
        return False

    def __iter__(self):
        """
        Iterates over the operations in the chain.

        Yields:
            OperationNode: The next operation node in the chain.
        """
        current_node = self.head
        while current_node:
            yield current_node
            current_node = current_node.next_node

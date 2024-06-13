"""
OperationStatusChecker Module.

This module defines the OperationStatusChecker class, which is responsible for checking the status of operations within
the research analytics suite. It provides methods to get the status of a specific operation and to get the status
of all operations in the queue.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

from research_analytics_suite.operation_manager.OperationChain import OperationChain
from research_analytics_suite.operation_manager.operations.ABCOperation import ABCOperation


class OperationStatusChecker:
    """
    A class to check the status of operations.

    This class provides methods to get the status of a specific operation and to get the status of all operations in
    the queue.
    """

    def __init__(self, queue):
        """
        Initializes the OperationStatusChecker with the necessary components.

        Args:
            queue: Queue holding operations to be checked.
        """
        self.queue = queue

    def get_operation_status(self, operation: ABCOperation) -> str:
        """
        Returns the status of a specific operation.

        Args:
            operation (ABCOperation): The operation to get the status of.

        Returns:
            str: The status of the operation.
        """
        return operation.status

    def get_all_operations_status(self) -> dict:
        """
        Returns the status of all operations in the queue.

        Returns:
            dict: A dictionary mapping operation instances to their status.
        """
        status_dict = {}
        for operation_chain in self.queue.queue:
            if isinstance(operation_chain, OperationChain):
                current_node = operation_chain.head
                while current_node is not None:
                    status_dict[current_node.operation] = current_node.operation.status
                    current_node = current_node.next_node
            else:
                status_dict[operation_chain] = operation_chain.status
        return status_dict

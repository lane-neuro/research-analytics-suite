"""
Module description.

Longer description.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from neurobehavioral_analytics_suite.operation_manager.OperationChain import OperationChain


class OperationStatusChecker:
    def __init__(self, handler, queue):
        self.handler = handler
        self.queue = queue

    def get_operation_status(self, operation) -> str:
        """
        Returns the status of a specific operation.

        Args:
            operation (Operation): The operation to get the status of.

        Returns:
            str: The status of the operation.
        """
        return operation.status

    def get_all_operations_status(self):
        """
        Returns the status of all operations in the queue.

        Returns:
            dict: A dictionary mapping operation instances to their status.
        """
        status_dict = {}
        for operation_node in self.queue.queue:
            if isinstance(operation_node, OperationChain):
                current_node = operation_node.head
                while current_node is not None:
                    status_dict[current_node.operation] = current_node.operation.status
                    current_node = current_node.next_node
            else:
                status_dict[operation_node] = operation_node.status
        return status_dict

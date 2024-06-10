"""
OperationNode Module.

This module defines the OperationNode class, which represents a node in an operation chain within the
research analytics suite. Each node contains an operation and a reference to the next node in the chain.

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


class OperationNode:
    """
    A class to represent a node in an operation chain.

    Each node contains an operation and a reference to the next node in the chain.
    """

    def __init__(self, operation: ABCOperation, next_node: 'OperationNode' = None):
        """
        Initializes the OperationNode with an operation and an optional reference to the next node.

        Args:
            operation (Operation): The operation to store in this node.
            next_node (OperationNode, optional): The next node in the chain. Defaults to None.
        """
        self.operation = operation
        self.next_node = next_node

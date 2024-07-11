"""
OperationStatusChecker Module.

This module defines the OperationStatusChecker class, which is responsible for checking the status of operations within
the research analytics suite. It provides methods to get the status of a specific operation and to get the status
of all operations in the sequencer.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from research_analytics_suite.commands import command, register_commands
from research_analytics_suite.operation_manager.chains.OperationChain import OperationChain
from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation


@register_commands
class OperationStatusChecker:
    """
    A class to check the status of operations.

    This class provides methods to get the status of a specific operation and to get the status of all operations in
    the sequencer.
    """

    def __init__(self, sequencer):
        """
        Initializes the OperationStatusChecker with the necessary components.

        Args:
            sequencer: Sequencer holding operations to be checked.
        """
        self.sequencer = sequencer

    @command
    def get_operation_status(self, operation: BaseOperation) -> str:
        """
        Returns the status of a specific operation.

        Args:
            operation (BaseOperation): The operation to get the status of.

        Returns:
            str: The status of the operation.
        """
        return operation.status

    @command
    def get_all_operations_status(self) -> dict:
        """
        Returns the status of all operations in the sequencer.

        Returns:
            dict: A dictionary mapping operation instances to their status.
        """
        status_dict = {}
        for operation_chain in self.sequencer.sequencer:
            if isinstance(operation_chain, OperationChain):
                current_node = operation_chain.head
                while current_node is not None:
                    status_dict[current_node.operation] = current_node.operation.status
                    current_node = current_node.next_node
            else:
                status_dict[operation_chain] = operation_chain.status
        return status_dict

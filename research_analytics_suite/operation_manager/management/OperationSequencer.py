"""
OperationSequencer Module.

This module defines the OperationSequencer class, which manages a sequencer of operations within the research analytics
suite. It provides methods to add, remove, move, and retrieve operations in the sequencer, ensuring efficient management
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
import json
from collections import deque
from typing import Optional, Any

from research_analytics_suite.commands import command, register_commands
from research_analytics_suite.operation_manager.chains.OperationChain import OperationChain
from research_analytics_suite.operation_manager.nodes.OperationNode import OperationNode
from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation
from research_analytics_suite.utils.CustomLogger import CustomLogger
from research_analytics_suite.operation_manager.operations.core.workspace import pack_as_local_reference


@register_commands
class OperationSequencer:
    """
    A class to manage a sequencer of operations.

    This class provides methods to add, remove, move, & retrieve operations in the sequencer, ensuring efficient
    management and execution of operations.
    """

    def __init__(self):
        """
        Initializes the OperationSequencer with a logger and error handler.
        """
        self.sequencer = deque()
        self._logger = CustomLogger()

    @command
    async def add_operation_to_sequencer(self, operation: BaseOperation):
        """
        Adds an operation to the sequencer.

        Args:
            operation (Operation): The operation to add to the sequencer.
        """
        self._logger.debug(f"Adding operation to sequencer: {operation.name} with rID: {operation.runtime_id}")

        if operation.parent_operation is None:
            if not isinstance(operation, OperationChain):
                operation_chain = OperationChain(operation)
            else:
                operation_chain = operation
            self.sequencer.append(operation_chain)
            self._logger.debug(f"Operation {operation.name} added as a new chain.")
        else:
            parent_chain = self.get_chain_by_operation(operation.parent_operation)
            if parent_chain:
                parent_chain.add_operation_to_chain(operation)
                await operation.parent_operation.link_child_operation(operation)
                self._logger.debug(f"Operation {operation.name} added to parent chain of {operation.parent_operation.name}.")

    @command
    def insert_operation_in_chain(self, index: int, operation_chain: OperationChain, operation: BaseOperation) -> None:
        """
        Inserts an operation in a chain at a specific index.

        Args:
            index (int): The index at which to insert the operation.
            operation_chain (OperationChain): The operation chain to insert the operation into.
            operation (Operation): The operation to insert.
        """
        if isinstance(operation_chain, OperationChain):
            current_node = operation_chain.head
            for i in range(index - 1):
                if current_node:
                    current_node = current_node.next_node
            if current_node:
                new_node = OperationNode(operation, current_node.next_node)
                current_node.next_node = new_node

    @command
    def remove_operation_from_chain(self, operation_chain: OperationChain, operation: BaseOperation) -> None:
        """
        Removes an operation from a chain.

        Args:
            operation_chain (OperationChain): The operation chain to remove the operation from.
            operation (Operation): The operation to remove.
        """
        if isinstance(operation_chain, OperationChain):
            operation_chain.remove_operation(operation)
            if operation_chain.is_empty():
                self.sequencer.remove(operation_chain)

    @command
    def move_operation(self, operation: BaseOperation, new_index: int) -> None:
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

    @command
    def remove_operation_from_sequencer(self, operation: BaseOperation) -> None:
        """
        Removes an operation from the sequencer.

        Args:
            operation (Operation): The operation to remove.
        """
        for chain in self.sequencer:
            if chain.head.operation == operation:
                self.sequencer.remove(chain)
                return
            elif chain.contains(operation):
                chain.remove_operation(operation)
                if chain.is_empty():
                    self.sequencer.remove(chain)
                return

    @command
    def get_head_operation_from_chain(self, operation_chain: OperationChain) -> Optional[BaseOperation]:
        """
        Gets the head operation from a chain.

        Args:
            operation_chain (OperationChain): The operation chain to get the head operation from.

        Returns:
            Optional[BaseOperation]: The head operation, or None if the chain is empty.
        """
        if isinstance(operation_chain, OperationChain) and not operation_chain.is_empty():
            return operation_chain.head.operation
        return None

    @command
    def get_chain_by_operation(self, operation: 'BaseOperation') -> Optional[OperationChain]:
        """
        Gets the operation chain that contains a specific operation.

        Args:
            operation (Operation): The operation to find the chain for.

        Returns:
            Optional[OperationChain]: The operation chain that contains the operation, or None if not found.
        """
        for chain in self.sequencer:
            if chain.contains(operation):
                return chain
        return None

    @command
    def get_operation_in_chain(self, operation_chain: OperationChain, operation: BaseOperation) \
            -> Optional[BaseOperation]:
        """
        Gets a specific operation in a chain.

        Args:
            operation_chain (OperationChain): The operation chain to search.
            operation (Operation): The operation to find.

        Returns:
            Optional[BaseOperation]: The found operation, or None if not found.
        """
        if isinstance(operation_chain, OperationChain):
            for node in operation_chain:
                if node.operation == operation:
                    return node.operation
        return None

    @command
    def get_operation_by_type(self, operation_type) -> Optional[BaseOperation]:
        """
        Gets an operation of a specific type.

        Args:
            operation_type: The type of operation to find.

        Returns:
            Optional[BaseOperation]: The found operation, or None if not found.
        """
        for chain in self.sequencer:
            for node in chain:
                if isinstance(node.operation, operation_type):
                    return node.operation
        self._logger.error(Exception(f"No operation found of type {operation_type.__name__}"), self.__class__.__name__)
        return None

    @command
    def find_operation_by_task(self, task) -> Optional[BaseOperation]:
        """
        Finds an operation by its associated task.

        Args:
            task: The task associated with the operation to find.

        Returns:
            Optional[BaseOperation]: The found operation, or None if not found.
        """
        for chain in self.sequencer:
            for node in chain:
                if node.operation.task == task:
                    return node.operation
        self._logger.error(Exception(f"No operation found for task {task}"), self.__class__.__name__)
        return None

    @command
    def is_empty(self) -> bool:
        """
        Checks if the sequencer is empty.

        Returns:
            bool: True if the sequencer is empty, False otherwise.
        """
        return len(self.sequencer) == 0

    @command
    def size(self) -> int:
        """
        Gets the size of the sequencer.

        Returns:
            int: The size of the sequencer.
        """
        return len(self.sequencer)

    @command
    def clear(self) -> None:
        """Clears the sequencer."""
        self.sequencer.clear()

    @command
    def contains(self, operation: BaseOperation) -> bool:
        """
        Checks if the sequencer contains a specific operation.

        Args:
            operation (Operation): The operation to check for.

        Returns:
            bool: True if the sequencer contains the operation, False otherwise.
        """
        return any(chain.contains(operation) for chain in self.sequencer)

    @command
    async def has_waiting_operations(self) -> bool:
        """
        Checks if the sequencer has any waiting operations.

        Returns:
            bool: True if the sequencer has waiting operations, False otherwise.
        """
        return any(self.get_head_operation_from_chain(chain).status == "waiting" for chain in self.sequencer)

    async def dequeue(self) -> Optional[OperationChain]:
        """
        Dequeues the first operation chain from the sequencer.

        Returns:
            Optional[OperationChain]: The dequeued operation chain, or None if the sequencer is empty.
        """
        if self.is_empty():
            return None
        return self.sequencer.popleft()

    @command
    def to_dict(self) -> list:
        """
        Converts the sequencer to a dictionary representation.

        Returns:
            list: The sequencer represented as a list of dictionaries.
        """
        return [self._convert_chain_to_dict(chain) for chain in self.sequencer]

    def _convert_chain_to_dict(self, chain: OperationChain) -> dict:
        chain_dict = {
            "operations": []
        }
        current_node = chain.head
        while current_node:
            chain_dict["operations"].append(self._convert_node_to_dict(current_node))
            current_node = current_node.next_node
        return chain_dict

    def _convert_node_to_dict(self, node: OperationNode) -> dict:
        node_dict = {
            "operation_name": node.operation.name,
            "operation_status": node.operation.status,
            "next_node": self._convert_node_to_dict(node.next_node) if node.next_node else None
        }
        return node_dict

    @command
    def to_json(self) -> str:
        """
        Converts the sequencer to a JSON string.

        Returns:
            str: The sequencer represented as a JSON string.
        """
        _sequencer_dict = self.to_dict()
        if not _sequencer_dict:
            return json.dumps({"Sequencer": "Empty"}, indent=4)
        return json.dumps(self.to_dict(), indent=4, default=self._json_default)

    def _json_default(self, obj: Any) -> Any:
        """
        Default JSON serializer.

        Args:
            obj (Any): The object to serialize.

        Returns:
            Any: The serialized object.
        """
        if isinstance(obj, BaseOperation):
            return pack_as_local_reference(obj)
        if isinstance(obj, OperationNode):
            return self._convert_node_to_dict(obj)
        if isinstance(obj, OperationChain):
            return self._convert_chain_to_dict(obj)
        return str(obj)  # Fallback to string conversion

    def __str__(self) -> str:
        """
        Converts the sequencer to a string.

        Returns:
            str: The sequencer represented as a string.
        """
        _sequencer_dict = self.to_dict()
        _sequencer_text = ""
        if not _sequencer_dict:
            _sequencer_text = "Sequencer is empty."
        else:
            for _chain in _sequencer_dict:
                _head_text = (f"\nHead: {_chain['operations'][0]['operation_name']} "
                              f"({_chain['operations'][0]['operation_status']})")
                _children_text = "\n\t->\t".join(
                    [f"{operation['operation_name']} "
                     f"({operation['operation_status']})" for operation in _chain['operations'][1:]])
                _chain_text = f"{_head_text}\n\t->\t{_children_text}"
                _sequencer_text += f"{_chain_text}\n"
        return _sequencer_text

    @command
    def print_sequencer(self) -> None:
        """
        Prints the sequencer in a readable format.
        """
        self._logger.info(self.__str__())

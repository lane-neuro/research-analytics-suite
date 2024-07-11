import pytest
from unittest.mock import MagicMock, patch

from research_analytics_suite.operation_manager import OperationChain
from research_analytics_suite.operation_manager.nodes import OperationNode
from research_analytics_suite.operation_manager.operations.core import BaseOperation


class TestOperationChain:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.operation1 = MagicMock(spec=BaseOperation, runtime_id="op1")
        self.operation2 = MagicMock(spec=BaseOperation, runtime_id="op2")
        self.operation3 = MagicMock(spec=BaseOperation, runtime_id="op3")
        self.operation_chain = OperationChain()

    def test_initialization_with_no_operation(self):
        operation_chain = OperationChain()
        assert operation_chain.head is None

    def test_initialization_with_operation(self):
        operation_chain = OperationChain(self.operation1)
        assert operation_chain.head.operation == self.operation1

    def test_add_operation_to_chain(self):
        self.operation_chain.add_operation_to_chain(self.operation1)
        assert self.operation_chain.head.operation == self.operation1

        self.operation_chain.add_operation_to_chain(self.operation2)
        assert self.operation_chain.head.next_node.operation == self.operation2

    def test_remove_operation(self):
        self.operation_chain.add_operation_to_chain(self.operation1)
        self.operation_chain.add_operation_to_chain(self.operation2)
        self.operation_chain.add_operation_to_chain(self.operation3)

        self.operation_chain.remove_operation(self.operation2)
        assert self.operation_chain.head.next_node.operation == self.operation3

    def test_remove_head_operation(self):
        self.operation_chain.add_operation_to_chain(self.operation1)
        self.operation_chain.add_operation_to_chain(self.operation2)

        self.operation_chain.remove_operation(self.operation1)
        assert self.operation_chain.head.operation == self.operation2

    def test_is_empty(self):
        assert self.operation_chain.is_empty()

        self.operation_chain.add_operation_to_chain(self.operation1)
        assert not self.operation_chain.is_empty()

    def test_count_operations(self):
        assert self.operation_chain.count_operations() == 0

        self.operation_chain.add_operation_to_chain(self.operation1)
        assert self.operation_chain.count_operations() == 1

        self.operation_chain.add_operation_to_chain(self.operation2)
        assert self.operation_chain.count_operations() == 2

    def test_contains_operation(self):
        self.operation_chain.add_operation_to_chain(self.operation1)
        assert self.operation_chain.contains(self.operation1)
        assert not self.operation_chain.contains(self.operation2)

    def test_iteration(self):
        self.operation_chain.add_operation_to_chain(self.operation1)
        self.operation_chain.add_operation_to_chain(self.operation2)

        operations = [node.operation for node in self.operation_chain]
        assert operations == [self.operation1, self.operation2]

    def test_add_none_operation(self):
        with patch('research_analytics_suite.operation_manager.nodes.OperationNode') as MockNode:
            self.operation_chain.add_operation_to_chain(None)
            MockNode.assert_not_called()

    def test_remove_non_existent_operation(self):
        self.operation_chain.add_operation_to_chain(self.operation1)
        self.operation_chain.remove_operation(self.operation2)  # Operation2 is not in the chain
        assert self.operation_chain.head.operation == self.operation1

    def test_duplicate_operations(self):
        self.operation_chain.add_operation_to_chain(self.operation1)
        self.operation_chain.add_operation_to_chain(self.operation1)
        assert self.operation_chain.count_operations() == 2

        operations = [node.operation for node in self.operation_chain]
        assert operations == [self.operation1, self.operation1]

    def test_iteration_over_empty_chain(self):
        operations = [node.operation for node in self.operation_chain]
        assert operations == []

    def test_add_same_operation_multiple_times(self):
        self.operation_chain.add_operation_to_chain(self.operation1)
        self.operation_chain.add_operation_to_chain(self.operation1)
        self.operation_chain.add_operation_to_chain(self.operation1)
        assert self.operation_chain.count_operations() == 3

    def test_remove_operation_from_empty_chain(self):
        self.operation_chain.remove_operation(self.operation1)
        assert self.operation_chain.head is None

    def test_remove_last_operation(self):
        self.operation_chain.add_operation_to_chain(self.operation1)
        self.operation_chain.remove_operation(self.operation1)
        assert self.operation_chain.is_empty()

    def test_chain_with_circular_reference(self):
        node1 = MagicMock(spec=OperationNode, operation=self.operation1)
        node2 = MagicMock(spec=OperationNode, operation=self.operation2)
        node3 = MagicMock(spec=OperationNode, operation=self.operation3)

        node1.next_node = node2
        node2.next_node = node3
        node3.next_node = node1  # Circular reference

        self.operation_chain.head = node1

        # This test checks if iteration can handle circular references
        operations = []
        for i, node in enumerate(self.operation_chain):
            operations.append(node.operation)
            if i > 10:  # Break after iterating more than the number of unique nodes to avoid infinite loop
                break

        assert operations[:3] == [self.operation1, self.operation2, self.operation3]

    def test_iteration_with_multiple_operations(self):
        self.operation_chain.add_operation_to_chain(self.operation1)
        self.operation_chain.add_operation_to_chain(self.operation2)
        self.operation_chain.add_operation_to_chain(self.operation3)

        operations = [node.operation for node in self.operation_chain]
        assert operations == [self.operation1, self.operation2, self.operation3]

    def test_remove_operation_from_middle(self):
        self.operation_chain.add_operation_to_chain(self.operation1)
        self.operation_chain.add_operation_to_chain(self.operation2)
        self.operation_chain.add_operation_to_chain(self.operation3)

        self.operation_chain.remove_operation(self.operation2)
        assert self.operation_chain.head.next_node.operation == self.operation3

    def test_remove_operation_from_end(self):
        self.operation_chain.add_operation_to_chain(self.operation1)
        self.operation_chain.add_operation_to_chain(self.operation2)
        self.operation_chain.add_operation_to_chain(self.operation3)

        self.operation_chain.remove_operation(self.operation3)

        operations = [node.operation for node in self.operation_chain]
        assert operations == [self.operation1, self.operation2]
        assert not self.operation_chain.contains(self.operation3)

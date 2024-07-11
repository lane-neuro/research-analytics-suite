# file path: tests/test_OperationSequencer.py
import pytest
from unittest.mock import MagicMock, patch
import json

from research_analytics_suite.operation_manager.management.OperationSequencer import OperationSequencer
from research_analytics_suite.operation_manager.chains.OperationChain import OperationChain
from research_analytics_suite.operation_manager.nodes.OperationNode import OperationNode
from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation
from research_analytics_suite.operation_manager.operations.core.workspace import pack_as_local_reference


@pytest.fixture
def mock_logger():
    with patch('research_analytics_suite.utils.CustomLogger') as MockLogger:
        yield MockLogger()


@pytest.fixture
def mock_operation():
    operation = MagicMock(spec=BaseOperation)
    operation.name = 'Test Operation'
    operation.runtime_id = '1234'
    operation.parent_operation = None
    operation.status = 'waiting'
    operation.unique_id = 'op1234'
    operation.task = 'Test Task'
    return operation


@pytest.fixture
def mock_operation_chain(mock_operation):
    operation_chain = MagicMock(spec=OperationChain)
    node = OperationNode(mock_operation)
    operation_chain.head = node
    operation_chain.contains.return_value = True
    operation_chain.is_empty.return_value = False
    operation_chain.remove_operation.return_value = None
    operation_chain.add_operation_to_chain.return_value = None
    operation_chain.__iter__.return_value = iter([node])
    return operation_chain


class TestOperationSequencer:
    @pytest.fixture(autouse=True)
    def setup(self, mock_logger):
        self.sequencer = OperationSequencer()
        self.sequencer._logger = mock_logger

    @pytest.mark.asyncio
    async def test_add_operation_to_sequencer(self, mock_operation):
        await self.sequencer.add_operation_to_sequencer(mock_operation)
        assert self.sequencer.sequencer[0].head.operation == mock_operation

    @pytest.mark.asyncio
    async def test_add_operation_with_parent(self, mock_operation, mock_operation_chain):
        parent_operation = MagicMock(spec=BaseOperation)
        parent_operation.name = 'Parent Operation'
        parent_operation.runtime_id = '5678'
        parent_operation.parent_operation = None
        mock_operation.parent_operation = parent_operation

        with patch.object(self.sequencer, 'get_chain_by_operation', return_value=mock_operation_chain):
            await self.sequencer.add_operation_to_sequencer(mock_operation)
            mock_operation_chain.add_operation_to_chain.assert_called_once_with(mock_operation)

    def test_insert_operation_in_chain(self, mock_operation, mock_operation_chain):
        self.sequencer.insert_operation_in_chain(1, mock_operation_chain, mock_operation)
        mock_operation_chain.head.next_node = OperationNode(mock_operation)

    def test_remove_operation_from_chain(self, mock_operation, mock_operation_chain):
        self.sequencer.remove_operation_from_chain(mock_operation_chain, mock_operation)
        mock_operation_chain.remove_operation.assert_called_once_with(mock_operation)

    def test_remove_operation_from_sequencer_head(self, mock_operation, mock_operation_chain):
        self.sequencer.sequencer.append(mock_operation_chain)
        self.sequencer.remove_operation_from_sequencer(mock_operation)
        assert not self.sequencer.sequencer

    def test_remove_only_operation_from_sequencer(self, mock_operation):
        # Create a chain with a single operation
        operation_chain = OperationChain(mock_operation)
        self.sequencer.sequencer.append(operation_chain)

        # Mock the is_empty method to return True after removal
        operation_chain.is_empty = MagicMock(return_value=True)

        self.sequencer.remove_operation_from_sequencer(mock_operation)
        assert len(self.sequencer.sequencer) == 0

    def test_remove_operation_from_sequencer_middle(self, mock_operation):
        # Create a chain with multiple operations
        operation1 = mock_operation
        operation2 = MagicMock(spec=BaseOperation)
        operation2.name = 'Operation 2'
        operation2.runtime_id = '5678'
        operation2.parent_operation = operation1
        operation2.status = 'waiting'
        operation2.unique_id = 'op5678'
        operation2.task = 'Task 2'

        node1 = OperationNode(operation1)
        node2 = OperationNode(operation2)
        node1.next_node = node2

        operation_chain = OperationChain(operation1)
        operation_chain.head = node1

        self.sequencer.sequencer.append(operation_chain)
        self.sequencer.remove_operation_from_sequencer(operation2)
        assert operation_chain.head.next_node is None
        assert len(self.sequencer.sequencer) == 1

    def test_remove_operation_from_empty_sequencer(self, mock_operation):
        self.sequencer.remove_operation_from_sequencer(mock_operation)
        assert self.sequencer.is_empty()

    def test_remove_non_existent_operation(self, mock_operation):
        # Create another operation that will be in the chain
        another_operation = MagicMock(spec=BaseOperation)
        another_operation.name = 'Another Operation'
        another_operation.runtime_id = '5678'

        # Create a mock operation chain with the other operation
        another_node = OperationNode(another_operation)
        operation_chain = MagicMock(spec=OperationChain)
        operation_chain.head = another_node
        operation_chain.contains.return_value = False

        self.sequencer.sequencer.append(operation_chain)
        self.sequencer.remove_operation_from_sequencer(mock_operation)
        assert len(self.sequencer.sequencer) == 1

    def test_remove_operation_and_check_chain_empty(self, mock_operation, mock_operation_chain):
        mock_operation_chain.is_empty.return_value = True
        self.sequencer.sequencer.append(mock_operation_chain)
        self.sequencer.remove_operation_from_sequencer(mock_operation)
        assert not self.sequencer.sequencer

    def test_move_operation(self, mock_operation, mock_operation_chain):
        with patch.object(self.sequencer, 'get_chain_by_operation', return_value=mock_operation_chain):
            self.sequencer.move_operation(mock_operation, 1)
            mock_operation_chain.remove_operation.assert_called_once_with(mock_operation)

    def test_get_head_operation_from_chain(self, mock_operation_chain):
        result = self.sequencer.get_head_operation_from_chain(mock_operation_chain)
        assert result == mock_operation_chain.head.operation

    def test_get_chain_by_operation(self, mock_operation, mock_operation_chain):
        self.sequencer.sequencer.append(mock_operation_chain)
        result = self.sequencer.get_chain_by_operation(mock_operation)
        assert result == mock_operation_chain

    def test_get_operation_in_chain(self, mock_operation, mock_operation_chain):
        mock_operation_chain.contains.return_value = False
        mock_operation_chain.__iter__.return_value = iter([OperationNode(mock_operation)])
        result = self.sequencer.get_operation_in_chain(mock_operation_chain, mock_operation)
        assert result == mock_operation

    def test_get_operation_by_type(self, mock_operation, mock_operation_chain):
        mock_operation_chain.head.operation = mock_operation
        self.sequencer.sequencer.append(mock_operation_chain)

        with patch('research_analytics_suite.operation_manager.operations.core.BaseOperation', new=MagicMock()):
            result = self.sequencer.get_operation_by_type(BaseOperation)
            assert result == mock_operation

    def test_find_operation_by_task(self, mock_operation, mock_operation_chain):
        task = 'Test Task'
        mock_operation.task = task
        mock_operation_chain.head.operation = mock_operation
        self.sequencer.sequencer.append(mock_operation_chain)
        result = self.sequencer.find_operation_by_task(task)
        assert result == mock_operation

    def test_is_empty(self):
        assert self.sequencer.is_empty()

    def test_size(self):
        assert self.sequencer.size() == 0

    def test_clear(self):
        self.sequencer.sequencer.append(MagicMock())
        self.sequencer.clear()
        assert self.sequencer.is_empty()

    def test_contains(self, mock_operation, mock_operation_chain):
        self.sequencer.sequencer.append(mock_operation_chain)
        assert self.sequencer.contains(mock_operation)

    @pytest.mark.asyncio
    async def test_has_waiting_operations(self, mock_operation_chain):
        self.sequencer.sequencer.append(mock_operation_chain)
        result = await self.sequencer.has_waiting_operations()
        assert result

    @pytest.mark.asyncio
    async def test_dequeue(self):
        operation_chain = MagicMock(spec=OperationChain)
        self.sequencer.sequencer.append(operation_chain)
        result = await self.sequencer.dequeue()
        assert result == operation_chain

    def test_to_dict(self, mock_operation_chain):
        self.sequencer.sequencer.append(mock_operation_chain)
        result = self.sequencer.to_dict()
        assert isinstance(result, list)
        assert "operations" in result[0]

    def test_str(self, mock_operation_chain):
        self.sequencer.sequencer.append(mock_operation_chain)
        result = str(self.sequencer)
        assert isinstance(result, str)

    def test_print_sequencer(self, mock_operation_chain):
        self.sequencer.sequencer.append(mock_operation_chain)
        self.sequencer.print_sequencer()
        self.sequencer._logger.info.assert_called()

    def test_to_json_empty(self):
        result = self.sequencer.to_json()
        expected = json.dumps({"Sequencer": "Empty"}, indent=4)
        assert result == expected

    def test_to_json_non_empty(self, mock_operation_chain):
        self.sequencer.sequencer.append(mock_operation_chain)
        result = self.sequencer.to_json()
        expected_dict = self.sequencer.to_dict()
        expected_json = json.dumps(expected_dict, indent=4)
        assert result == expected_json

    def test_json_default_with_base_operation(self, mock_operation):
        result = self.sequencer._json_default(mock_operation)
        assert result == pack_as_local_reference(mock_operation)

    def test_json_default_with_operation_node(self, mock_operation):
        node = OperationNode(mock_operation)
        result = self.sequencer._json_default(node)
        expected = {
            "operation_name": mock_operation.name,
            "operation_status": mock_operation.status,
            "next_node": None
        }
        assert result == expected

    def test_json_default_with_operation_chain(self, mock_operation_chain):
        result = self.sequencer._json_default(mock_operation_chain)
        expected = {
            "operations": [
                {
                    "operation_name": mock_operation_chain.head.operation.name,
                    "operation_status": mock_operation_chain.head.operation.status,
                    "next_node": None
                }
            ]
        }
        assert result == expected

    def test_json_default_with_other_object(self):
        other_obj = {"key": "value"}
        result = self.sequencer._json_default(other_obj)
        assert result == str(other_obj)
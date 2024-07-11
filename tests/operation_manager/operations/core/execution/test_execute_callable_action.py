import pytest
from collections import namedtuple
from unittest.mock import MagicMock

from research_analytics_suite.operation_manager.operations.core.execution.PrepareAction import _execute_callable_action

# Define the MemorySlot namedtuple with additional fields
MemorySlot = namedtuple('MemorySlot', ['name', 'data', 'memory_id', 'operation_required'])


@pytest.mark.asyncio
class TestExecuteCallableAction:
    async def test_action_with_memory_inputs(self):
        # Mock the t_action callable
        t_action = MagicMock(return_value="result")

        # Mock memory inputs with the additional parameters
        memory_inputs = [
            MemorySlot(name='input1', data=(str, 'value1'), memory_id=1, operation_required='read'),
            MemorySlot(name='input2', data=(str, 'value2'), memory_id=2, operation_required='write')
        ]

        # Get the action callable
        action_callable = _execute_callable_action(t_action, memory_inputs)

        # Call the action callable and get the result
        result = action_callable()

        # Assert that the result is as expected
        assert result == "result"
        # Assert that t_action was called with the correct arguments
        t_action.assert_called_once_with('value1', 'value2')

    async def test_action_without_memory_inputs(self):
        # Mock the t_action callable
        t_action = MagicMock(return_value=None)

        # Get the action callable without memory inputs
        action_callable = _execute_callable_action(t_action)

        # Call the action callable
        result = action_callable()

        # Assert that the result is None
        assert result is None
        # Assert that t_action was called with no arguments
        t_action.assert_called_once_with()
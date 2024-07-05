import pytest
import asyncio
import numpy as np
from unittest.mock import MagicMock


@pytest.fixture
def memory_output():
    """Fixture for creating a MemoryOutput instance."""
    from research_analytics_suite.operation_manager.operations.core.memory import MemoryOutput
    return MemoryOutput(name="test_memory_output")


@pytest.fixture
def memory_slot():
    """Fixture for creating a mock memory slot."""
    slot = MagicMock()
    slot.data = {'values': [0.1, 0.5, 0.9]}
    return slot


def test_initialization(memory_output):
    """Test that the MemoryOutput class initializes correctly."""
    assert memory_output.name == "test_memory_output"
    from research_analytics_suite.operation_manager.operations.core.memory import MemoryOutput
    assert isinstance(memory_output, MemoryOutput)


@pytest.mark.asyncio
async def test_aggregate_results(memory_output, memory_slot):
    """Test the aggregate_results method."""
    memory_output.slots = [memory_slot]
    result = await memory_output.aggregate_results()
    expected_result = {'values': [0.1, 0.5, 0.9]}
    assert result == expected_result

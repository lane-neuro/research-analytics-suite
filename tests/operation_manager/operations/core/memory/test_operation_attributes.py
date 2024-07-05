# tests\operation_manager\operations\core\memory\test_operation_attributes.py

import pytest
import asyncio
from unittest.mock import patch, AsyncMock

from research_analytics_suite.operation_manager.operations.core.memory.OperationAttributes import OperationAttributes


@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_initialization():
    op_attr = OperationAttributes(
        name='TestOperation',
        version='1.0',
        description='Test description',
        category_id='cat123',
        author='TestAuthor',
        github='https://github.com/test/repo',
        email='test@example.com',
        unique_id='unique123',
        action='test_action',
        required_inputs={'input1': 'value1'},
        parent_operation=None,
        inheritance=[],
        is_loop=False,
        is_cpu_bound=False,
        parallel=True
    )

    assert op_attr._name is None
    assert op_attr._version is None
    assert not op_attr._initialized


@pytest.mark.asyncio
async def test_export_attributes_before_initialization():
    op_attr = OperationAttributes(
        name='TestOperation',
        version='1.0',
        description='Test description',
        category_id='cat123',
        author='TestAuthor',
        github='https://github.com/test/repo',
        email='test@example.com',
        unique_id='unique123',
        action='test_action',
        required_inputs={'input1': 'value1'},
        parent_operation=None,
        inheritance=[],
        is_loop=False,
        is_cpu_bound=False,
        parallel=True
    )

    attributes = op_attr.export_attributes()
    assert attributes['name'] is None


@pytest.mark.asyncio
async def test_export_attributes_after_initialization():
    op_attr = OperationAttributes(
        name='TestOperation',
        version='1.0',
        description='Test description',
        category_id='cat123',
        author='TestAuthor',
        github='https://github.com/test/repo',
        email='test@example.com',
        unique_id='unique123',
        action='test_action',
        required_inputs={'input1': 'value1'},
        parent_operation=None,
        inheritance=[],
        is_loop=False,
        is_cpu_bound=False,
        parallel=True
    )

    await op_attr.initialize()

    attributes = op_attr.export_attributes()
    assert attributes['name'] == 'TestOperation'
    assert attributes['version'] == '1.0'
    assert attributes['description'] == 'Test description'
    assert attributes['category_id'] == 'cat123'
    assert attributes['author'] == 'TestAuthor'
    assert attributes['github'] == 'https://github.com/test/repo'
    assert attributes['email'] == 'test@example.com'
    assert attributes['unique_id'] == 'unique123'
    assert attributes['action'] == 'test_action'
    assert attributes['required_inputs'] == {'input1': 'value1'}
    assert attributes['parent_operation'] is None
    assert attributes['inheritance'] == []
    assert not attributes['is_loop']
    assert not attributes['is_cpu_bound']
    assert attributes['parallel']


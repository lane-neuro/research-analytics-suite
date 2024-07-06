# tests/operation_manager/operations/core/memory/test_operation_attributes.py
import pytest
import asyncio
from unittest.mock import patch, AsyncMock

from research_analytics_suite.operation_manager.operations.core.memory.OperationAttributes import OperationAttributes


@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


class TestOperationAttributes:

    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.op_attr = OperationAttributes(
            name='TestOperation',
            version='1.0',
            description='Test description',
            category_id=123,
            author='TestAuthor',
            github='https://github.com/test/repo',
            email='test@example.com',
            action='test_action',
            required_inputs={'input1': 'value1'},
            parent_operation=None,
            inheritance=[],
            is_loop=False,
            is_cpu_bound=False,
            parallel=True
        )

    @pytest.mark.asyncio
    async def test_initialization(self):
        assert self.op_attr._name is None
        assert self.op_attr._version is None
        assert not self.op_attr._initialized

    @pytest.mark.asyncio
    async def test_export_attributes_before_initialization(self):
        attributes = self.op_attr.export_attributes()
        assert attributes['name'] == 'No name'

    @pytest.mark.asyncio
    async def test_export_attributes_after_initialization(self):
        await self.op_attr.initialize()
        attributes = self.op_attr.export_attributes()
        assert attributes['name'] == 'TestOperation'
        assert attributes['version'] == '1.0'
        assert attributes['description'] == 'Test description'
        assert attributes['category_id'] == 123
        assert attributes['author'] == 'TestAuthor'
        assert attributes['github'] == 'https://github.com/test/repo'
        assert attributes['email'] == 'test@example.com'
        assert attributes['unique_id'] == f'https://github.com/test/repo_TestOperation_1.0'
        assert attributes['action'] == 'test_action'
        assert attributes['required_inputs'] == {'input1': 'value1'}
        assert attributes['parent_operation'] is None
        assert attributes['inheritance'] == []
        assert not attributes['is_loop']
        assert not attributes['is_cpu_bound']
        assert attributes['parallel']

    @pytest.mark.asyncio
    async def test_invalid_data_types(self):
        op_attr_invalid = OperationAttributes(
            name=123,  # Invalid type: should be str
            version=1.0,  # Invalid type: should be str
            description=123,  # Invalid type: should be str
            category_id='123',  # Invalid type: should be int
            author=123,  # Invalid type: should be str
            github=123,  # Invalid type: should be str
            email=123,  # Invalid type: should be str
            unique_id=123,  # Invalid type: should be str
            action=None,  # Invalid type: should be any valid action type
            required_inputs='input1',  # Invalid type: should be dict
            parent_operation='parent',  # Invalid type: should be OperationAttributes or None
            inheritance='inheritance',  # Invalid type: should be list
            is_loop='False',  # Invalid type: should be bool
            is_cpu_bound='False',  # Invalid type: should be bool
            parallel='True'  # Invalid type: should be bool
        )

        await op_attr_invalid.initialize()

        attributes = op_attr_invalid.export_attributes()
        assert attributes['name'] == 'No name'
        assert attributes['version'] == '0.0.1'
        assert attributes['description'] == 'None'
        assert attributes['category_id'] == 1
        assert attributes['author'] == 'No author'
        assert attributes['github'] == '[no-github]'
        assert attributes['email'] == '[no-email]'
        assert attributes['unique_id'] == '[no-github]_No name_0.0.1'
        assert attributes['action'] is None
        assert attributes['required_inputs'] == {}
        assert attributes['parent_operation'] is None
        assert attributes['inheritance'] == []
        assert not attributes['is_loop']
        assert not attributes['is_cpu_bound']
        assert not attributes['parallel']

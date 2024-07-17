# tests/test_operation_attributes.py
from unittest.mock import MagicMock

import pytest
import asyncio


class TestOperationAttributes:

    @pytest.fixture(autouse=True)
    def setup_method(self):
        from research_analytics_suite.operation_manager.operations.core.memory.OperationAttributes import \
            OperationAttributes
        self.op_attr = OperationAttributes(
            name='TestOperation',
            version='1.0',
            description='Test description',
            category_id=123,
            author='TestAuthor',
            github='test-author',
            email='test@example.com',
            action='test_action',
            required_inputs={'input1': str},
            parent_operation=None,
            inheritance=[MagicMock(), MagicMock()],
            is_loop=False,
            is_cpu_bound=False,
            parallel=True
        )

    def test_initialization(self):
        assert self.op_attr.name == '[no-name]'
        assert self.op_attr.version == '0.0.1'
        assert not self.op_attr._initialized

    def test_export_attributes_before_initialization(self):
        self.op_attr._initialized = False
        attributes = self.op_attr.export_attributes()
        assert attributes['name'] == '[no-name]'
        assert attributes['version'] == '0.0.1'
        assert attributes['description'] == '[no-description]'
        assert attributes['category_id'] == -1
        assert attributes['author'] == '[no-author]'
        assert attributes['github'] == '[no-github]'
        assert attributes['email'] == '[no-email]'
        assert attributes['unique_id'] == '[no-github]_[no-name]_0.0.1'
        assert attributes['action'] is None
        assert attributes['required_inputs'] == {}
        assert attributes['parent_operation'] is None
        assert attributes['inheritance'] == []
        assert not attributes['is_loop']
        assert not attributes['is_cpu_bound']
        assert not attributes['parallel']

    @pytest.mark.asyncio
    async def test_export_attributes_after_initialization(self):
        await self.op_attr.initialize()
        attributes = self.op_attr.export_attributes()
        assert attributes['name'] == 'TestOperation'
        assert attributes['version'] == '1.0'
        assert attributes['description'] == 'Test description'
        assert attributes['category_id'] == 123
        assert attributes['author'] == 'TestAuthor'
        assert attributes['github'] == 'test-author'
        assert attributes['email'] == 'test@example.com'
        assert attributes['unique_id'] == 'test-author_TestOperation_1.0'
        assert attributes['action'] == 'test_action'
        assert attributes['required_inputs'] == {'input1': 'str'}
        assert attributes['parent_operation'] is None
        assert isinstance(attributes['inheritance'], list)
        assert len(attributes['inheritance']) == 2
        assert not attributes['is_loop']
        assert not attributes['is_cpu_bound']
        assert attributes['parallel']

    @pytest.mark.asyncio
    async def test_invalid_data_types(self):
        from research_analytics_suite.operation_manager.operations.core.memory.OperationAttributes import \
            OperationAttributes
        op_attr_invalid = OperationAttributes(
            name=123,
            version=1.0,
            description=123,
            category_id='123',
            author=123,
            github=123,
            email=123,
            unique_id=123,
            action=None,
            required_inputs='input1',
            parent_operation='parent',
            inheritance='inheritance',
            is_loop='False',
            is_cpu_bound='False',
            parallel='True'
        )

        await op_attr_invalid.initialize()

        attributes = op_attr_invalid.export_attributes()
        assert attributes['name'] == '[no-name]'
        assert attributes['version'] == '0.0.1'
        assert attributes['description'] == '[no-description]'
        assert attributes['category_id'] == -1
        assert attributes['author'] == '[no-author]'
        assert attributes['github'] == '[no-github]'
        assert attributes['email'] == '[no-email]'
        assert attributes['unique_id'] == '[no-github]_[no-name]_0.0.1'
        assert attributes['action'] is None
        assert attributes['required_inputs'] == {}
        assert attributes['parent_operation'] is None
        assert attributes['inheritance'] == []
        assert not attributes['is_loop']
        assert not attributes['is_cpu_bound']
        assert not attributes['parallel']

    @pytest.mark.asyncio
    async def test_edge_case_empty_fields(self):
        from research_analytics_suite.operation_manager.operations.core.memory.OperationAttributes import \
            OperationAttributes
        op_attr_empty = OperationAttributes(
            name='',
            version='',
            description='',
            category_id=0,
            author='',
            github='',
            email='',
            action='',
            required_inputs={},
            parent_operation=None,
            inheritance=[],
            is_loop=False,
            is_cpu_bound=False,
            parallel=False
        )

        await op_attr_empty.initialize()

        attributes = op_attr_empty.export_attributes()
        assert attributes['name'] == '[no-name]'
        assert attributes['version'] == '0.0.1'
        assert attributes['description'] == '[no-description]'
        assert attributes['category_id'] == -1
        assert attributes['author'] == '[no-author]'
        assert attributes['github'] == '[no-github]'
        assert attributes['email'] == '[no-email]'
        assert attributes['unique_id'] == '[no-github]_[no-name]_0.0.1'
        assert attributes['action'] is None
        assert attributes['required_inputs'] == {}
        assert attributes['parent_operation'] is None
        assert attributes['inheritance'] == []
        assert not attributes['is_loop']
        assert not attributes['is_cpu_bound']
        assert not attributes['parallel']

    @pytest.mark.asyncio
    async def test_partial_initialization(self):
        from research_analytics_suite.operation_manager.operations.core.memory.OperationAttributes import \
            OperationAttributes
        op_attr_partial = OperationAttributes(
            name='PartialTest',
            version='1.1',
            description='Partial description',
            category_id=456,
            author='PartialAuthor',
            github='partial-author',
            email='partial@example.com',
            action='partial_action',
            required_inputs={'input1': 'str'},
            parent_operation=None,
            inheritance=[],
            is_loop=True,
            is_cpu_bound=True,
            parallel=False
        )

        await op_attr_partial.initialize()

        attributes = op_attr_partial.export_attributes()
        assert attributes['name'] == 'PartialTest'
        assert attributes['version'] == '1.1'
        assert attributes['description'] == 'Partial description'
        assert attributes['category_id'] == 456
        assert attributes['author'] == 'PartialAuthor'
        assert attributes['github'] == 'partial-author'
        assert attributes['email'] == 'partial@example.com'
        assert attributes['unique_id'] == 'partial-author_PartialTest_1.1'
        assert attributes['action'] == 'partial_action'
        assert attributes['required_inputs'] == {'input1': 'str'}
        assert attributes['parent_operation'] is None
        assert attributes['inheritance'] == []
        assert attributes['is_loop']
        assert attributes['is_cpu_bound']
        assert not attributes['parallel']

    @pytest.mark.asyncio
    async def test_missing_required_inputs(self):
        from research_analytics_suite.operation_manager.operations.core.memory.OperationAttributes import \
            OperationAttributes
        op_attr_no_inputs = OperationAttributes(
            name='NoInputs',
            version='1.2',
            description='No inputs description',
            category_id=789,
            author='NoInputsAuthor',
            github='noinputs-author',
            email='noinputs@example.com',
            action='noinputs_action',
            required_inputs=None,
            parent_operation=None,
            inheritance=[],
            is_loop=True,
            is_cpu_bound=True,
            parallel=True
        )

        await op_attr_no_inputs.initialize()

        attributes = op_attr_no_inputs.export_attributes()
        assert attributes['name'] == 'NoInputs'
        assert attributes['version'] == '1.2'
        assert attributes['description'] == 'No inputs description'
        assert attributes['category_id'] == 789
        assert attributes['author'] == 'NoInputsAuthor'
        assert attributes['github'] == 'noinputs-author'
        assert attributes['email'] == 'noinputs@example.com'
        assert attributes['unique_id'] == 'noinputs-author_NoInputs_1.2'
        assert attributes['action'] == 'noinputs_action'
        assert attributes['required_inputs'] == {}
        assert attributes['parent_operation'] is None
        assert attributes['inheritance'] == []
        assert attributes['is_loop']
        assert attributes['is_cpu_bound']
        assert attributes['parallel']

import json

import pytest
import ast
import tempfile
import os
from unittest.mock import patch, MagicMock

from research_analytics_suite.operation_manager import translate_item, get_attributes_from_disk, \
    get_attributes_from_operation, get_attributes_from_dict, get_attributes_from_module
from research_analytics_suite.operation_manager.operations.core.OperationAttributes import OperationAttributes


# Helper fixtures
@pytest.fixture
def sample_dict():
    return {
        'name': 'test_name',
        'version': '0.0.2',
        'description': 'test_description',
        'category_id': 1,
        'author': 'test_author'
    }


@pytest.fixture
def sample_module():
    class SampleModule:
        name = "sample"
        version = "1.0"
        description = "A sample module"

        def execute(self):
            return "Executing"

    return SampleModule


@pytest.fixture
async def sample_operation():
    operation = MagicMock()
    operation.export_attributes.return_value = {
        'name': 'operation_name',
        'version': '0.1.0',
        'description': 'An operation'
    }
    return operation


@pytest.fixture
def temp_file():
    # Create a temporary file and write valid JSON content
    temp = tempfile.NamedTemporaryFile(delete=False)
    with open(temp.name, 'w') as f:
        json.dump({"key": "value"}, f)  # Example JSON content
    temp.close()
    yield temp.name
    # Ensure cleanup after test
    if os.path.exists(temp.name):
        os.remove(temp.name)


@pytest.fixture
def temp_dir():
    # Create a temporary directory
    temp_directory = tempfile.TemporaryDirectory()
    yield temp_directory.name
    # Cleanup the directory after the test
    temp_directory.cleanup()


class TestUtils:

    # Test translate_item function
    def test_translate_item_str(self):
        item = ast.Str(s='test_string')
        assert translate_item(item) == 'test_string'

    def test_translate_item_num(self):
        item = ast.Num(n=42)
        assert translate_item(item) == 42

    def test_translate_item_nameconstant(self):
        item = ast.NameConstant(value=True)
        assert translate_item(item) is True

    def test_translate_item_list(self):
        item = ast.List(elts=[ast.Num(n=1), ast.Num(n=2)])
        assert translate_item(item) == [1, 2]

    def test_translate_item_dict(self):
        item = ast.Dict(keys=[ast.Str(s='key')], values=[ast.Num(n=42)])
        assert translate_item(item) == {'key': 42}

    def test_translate_item_tuple(self):
        item = ast.Tuple(elts=[ast.Str(s='a'), ast.Str(s='b')])
        assert translate_item(item) == ('a', 'b')

    def test_translate_item_name(self):
        item = ast.Name(id='variable_name')
        assert translate_item(item) == 'variable_name'

    def test_translate_item_attribute(self):
        item = ast.Attribute(attr='attribute_name')
        assert translate_item(item) == 'attribute_name'

    # Test get_attributes_from_module function
    @pytest.mark.asyncio
    async def test_get_attributes_from_module(self, sample_module):
        class SampleModule:
            name = "sample"
            version = "1.0"
            description = "A sample module"

            def execute(self):
                return "Executing"

        # Make sure the source code is stripped of any leading whitespace
        attributes = await get_attributes_from_module(SampleModule)
        assert isinstance(attributes, OperationAttributes)
        assert attributes.name == "sample"

    # Test get_attributes_from_operation function
    @pytest.mark.asyncio
    async def test_get_attributes_from_operation(self, sample_operation):
        attributes = await get_attributes_from_operation(sample_operation)
        assert isinstance(attributes, OperationAttributes)
        sample_operation.export_attributes.assert_called_once()

    # Test get_attributes_from_dict function
    @pytest.mark.asyncio
    async def test_get_attributes_from_dict(self, sample_dict):
        attributes = await get_attributes_from_dict(sample_dict)
        assert isinstance(attributes, OperationAttributes)
        assert attributes.name == sample_dict['name']

    # Additional tests for edge cases
    @pytest.mark.asyncio
    async def test_get_attributes_from_disk_invalid_path(self):
        with patch('research_analytics_suite.operation_manager.operations.core.workspace.load_from_disk',
                   side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                await get_attributes_from_disk('invalid/path')

    @pytest.mark.asyncio
    async def test_get_attributes_from_module_no_execute(self):
        class NoExecuteModule:
            name = "sample"
            version = "1.0"
            description = "A sample module"

        attributes = await get_attributes_from_module(NoExecuteModule)
        assert attributes.action is None

    @pytest.mark.asyncio
    async def test_get_attributes_from_dict_missing_values(self, sample_dict):
        sample_dict.pop('name')
        attributes = await get_attributes_from_dict(sample_dict)
        assert attributes.name == '[no-name]'

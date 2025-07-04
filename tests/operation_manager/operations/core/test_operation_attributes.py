import asyncio
import pytest
import time
from unittest.mock import patch, MagicMock

from research_analytics_suite.operation_manager.operations.core import OperationAttributes


@pytest.fixture(scope='function')
def mock_logger():
    with patch('research_analytics_suite.utils.CustomLogger', new_callable=MagicMock) as mock_logger:
        yield mock_logger

@pytest.fixture(scope='function')
def mock_memory_manager():
    with patch('research_analytics_suite.data_engine.memory.MemoryManager', new_callable=MagicMock) as mock_manager:
        # Set up mock return values for slot_data, slot_name, and slot_type
        mock_manager.slot_data.side_effect = lambda slot_id: "test_data" if slot_id else None
        mock_manager.slot_name.side_effect = lambda slot_id: f"slot_{slot_id}" if slot_id else None
        mock_manager.slot_type.side_effect = lambda slot_id: str if slot_id else None
        yield mock_manager
        mock_manager.reset_mock()


class TestOperationAttributes:

    @pytest.mark.asyncio
    async def test_initialization_with_kwargs(self, mock_logger):
        attrs = OperationAttributes(
            name='test_name', version='0.0.2', description='test_description',
            category_id=1, author='test_author', github='@test_github',
            email='test@example.com', action='test_action', required_inputs={'test_slot': str},
            parent_operation=None, inheritance=[], is_loop=True, is_cpu_bound=False, is_gpu_bound=True, parallel=True
        )
        await attrs.initialize()

        assert attrs.name == 'test_name'
        assert attrs.version == '0.0.2'
        assert attrs.description == 'test_description'
        assert attrs.category_id == 1
        assert attrs.author == 'test_author'
        assert attrs.github == 'test_github'
        assert attrs.email == 'test@example.com'
        assert attrs.action == 'test_action'
        # assert attrs.required_inputs == {'test_slot': str}
        assert attrs.parent_operation is None
        assert attrs.inheritance == []
        assert attrs.is_loop is True
        assert attrs.is_cpu_bound is False
        assert attrs.is_gpu_bound is True
        assert attrs.parallel is True

    @pytest.mark.asyncio
    async def test_initialization_with_args(self, mock_logger):
        attrs = OperationAttributes(
            {'name': 'test_name', 'version': '0.0.2', 'description': 'test_description',
             'category_id': 1, 'author': 'test_author', 'github': '@test_github',
             'email': 'test@example.com', 'action': 'test_action', 'required_inputs': {'input1': str},
             'parent_operation': None, 'inheritance': [], 'is_loop': True, 'is_cpu_bound': False,
             'is_gpu_bound': True, 'parallel': True}
        )
        await attrs.initialize()

        assert attrs.name == 'test_name'
        assert attrs.version == '0.0.2'
        assert attrs.description == 'test_description'
        assert attrs.category_id == 1
        assert attrs.author == 'test_author'
        assert attrs.github == 'test_github'
        assert attrs.email == 'test@example.com'
        assert attrs.action == 'test_action'
        # assert attrs.required_inputs == {'input1': str}
        assert attrs.parent_operation is None
        assert attrs.inheritance == []
        assert attrs.is_loop is True
        assert attrs.is_cpu_bound is False
        assert attrs.is_gpu_bound is True
        assert attrs.parallel is True

    @pytest.mark.asyncio
    async def test_initialization_with_defaults(self, mock_logger):
        attrs = OperationAttributes()
        await attrs.initialize()

        assert attrs.name == '[no-name]'
        assert attrs.version == '0.0.1'
        assert attrs.description == '[no-description]'
        assert attrs.category_id == -1
        assert attrs.author == '[no-author]'
        assert attrs.github == '[no-github]'
        assert attrs.email == '[no-email]'
        assert attrs.action is None
        assert attrs.required_inputs == {}
        assert attrs.parent_operation is None
        assert attrs.inheritance == []
        assert attrs.is_loop is False
        assert attrs.is_cpu_bound is False
        assert attrs.is_gpu_bound is False
        assert attrs.parallel is False

    @pytest.mark.asyncio
    async def test_initialization_mixed_args_kwargs(self, mock_logger):
        # Mixed args and kwargs provided, kwargs should take precedence
        attrs = OperationAttributes(
            {'name': 'arg_name', 'version': '0.0.1', 'description': 'arg_description'},
            name='kwarg_name', version='0.0.2', description='kwarg_description',
            category_id=2, author='kwarg_author', github='@kwarg_github',
            email='kwarg@example.com', action='kwarg_action', required_inputs={'input1': str},
            parent_operation=None, inheritance=['kwarg_inheritance'], is_loop=True,
            is_cpu_bound=True, is_gpu_bound=False, parallel=False
        )
        await attrs.initialize()

        # Assertions to ensure kwargs take precedence over args
        assert attrs.name == 'kwarg_name'
        assert attrs.version == '0.0.2'
        assert attrs.description == 'kwarg_description'
        assert attrs.category_id == 2
        assert attrs.author == 'kwarg_author'
        assert attrs.github == 'kwarg_github'
        assert attrs.email == 'kwarg@example.com'
        assert attrs.action == 'kwarg_action'
        # assert attrs.required_inputs == {'input1': str}
        assert attrs.parent_operation is None
        assert attrs.inheritance == ['kwarg_inheritance']
        assert attrs.is_loop is True
        assert attrs.is_cpu_bound is True
        assert attrs.is_gpu_bound is False
        assert attrs.parallel is False

    @pytest.mark.asyncio
    async def test_initialization_priority_kwargs_over_args(self, mock_logger):
        attrs = OperationAttributes(
            {'name': 'arg_name'}, name='kwarg_name', version='0.0.2'
        )
        await attrs.initialize()

        assert attrs.name == 'kwarg_name'
        assert attrs.version == '0.0.2'

    @pytest.mark.asyncio
    async def test_initialization_priority_args_over_none(self, mock_logger):
        attrs = OperationAttributes(
            {'name': 'arg_name'}
        )
        await attrs.initialize()

        assert attrs.name == 'arg_name'

    @pytest.mark.asyncio
    async def test_initialization_partial_overlap_args_kwargs(self, mock_logger):
        attrs = OperationAttributes(
            {'name': 'arg_name', 'version': '0.0.1'},
            name='kwarg_name', description='kwarg_description',
            category_id=2, author='kwarg_author'
        )
        await attrs.initialize()

        assert attrs.name == 'kwarg_name'  # kwarg should override arg
        assert attrs.version == '0.0.1'  # no kwarg provided, so arg is used
        assert attrs.description == 'kwarg_description'
        assert attrs.category_id == 2
        assert attrs.author == 'kwarg_author'

    @pytest.mark.asyncio
    async def test_initialization_empty_args_valid_kwargs(self, mock_logger):
        attrs = OperationAttributes(
            name='kwarg_name', version='0.0.2', description='kwarg_description',
            category_id=2, author='kwarg_author', github='@kwarg_github',
            email='kwarg@example.com', action='kwarg_action', required_inputs={'input1': str},
            parent_operation=None, inheritance=['kwarg_inheritance'], is_loop=True,
            is_cpu_bound=True, is_gpu_bound=False, parallel=False
        )
        await attrs.initialize()

        assert attrs.name == 'kwarg_name'
        assert attrs.version == '0.0.2'
        assert attrs.description == 'kwarg_description'
        assert attrs.category_id == 2
        assert attrs.author == 'kwarg_author'
        assert attrs.github == 'kwarg_github'
        assert attrs.email == 'kwarg@example.com'
        assert attrs.action == 'kwarg_action'
        # assert attrs.required_inputs == {'input1': str}
        assert attrs.parent_operation is None
        assert attrs.inheritance == ['kwarg_inheritance']
        assert attrs.is_loop is True
        assert attrs.is_cpu_bound is True
        assert attrs.is_gpu_bound is False
        assert attrs.parallel is False

    @pytest.mark.asyncio
    async def test_initialization_invalid_args_valid_kwargs(self, mock_logger):
        attrs = OperationAttributes(
            {'name': 123, 'version': 456},  # Invalid types
            name='kwarg_name', version='0.0.2', description='kwarg_description',
            category_id=2, author='kwarg_author', github='@kwarg_github',
            email='kwarg@example.com', action='kwarg_action', required_inputs={'input1': str},
            parent_operation=None, inheritance=['kwarg_inheritance'], is_loop=True,
            is_cpu_bound=True, is_gpu_bound=False, parallel=False
        )
        await attrs.initialize()

        assert attrs.name == 'kwarg_name'
        assert attrs.version == '0.0.2'
        assert attrs.description == 'kwarg_description'
        assert attrs.category_id == 2
        assert attrs.author == 'kwarg_author'
        assert attrs.github == 'kwarg_github'
        assert attrs.email == 'kwarg@example.com'
        assert attrs.action == 'kwarg_action'
        # assert attrs.required_inputs == {'input1': str}
        assert attrs.parent_operation is None
        assert attrs.inheritance == ['kwarg_inheritance']
        assert attrs.is_loop is True
        assert attrs.is_cpu_bound is True
        assert attrs.is_gpu_bound is False
        assert attrs.parallel is False

    @pytest.mark.asyncio
    async def test_initialization_with_no_args_or_kwargs(self, mock_logger):
        attrs = OperationAttributes()
        await attrs.initialize()

        assert attrs.name == '[no-name]'
        assert attrs.version == '0.0.1'
        assert attrs.description == '[no-description]'
        assert attrs.category_id == -1
        assert attrs.author == '[no-author]'
        assert attrs.github == '[no-github]'
        assert attrs.email == '[no-email]'
        assert attrs.action is None
        assert attrs.required_inputs == {}
        assert attrs.parent_operation is None
        assert attrs.inheritance == []
        assert attrs.is_loop is False
        assert attrs.is_cpu_bound is False
        assert attrs.is_gpu_bound is False
        assert attrs.parallel is False

    @pytest.mark.asyncio
    async def test_invalid_data_types(self, mock_logger):
        attrs = OperationAttributes(
            name=123, version=456, description=789,
            category_id='invalid', author=None, github=True,
            email=[], action={}, required_inputs='invalid',
            parent_operation='invalid', inheritance='invalid', is_loop='invalid',
            is_cpu_bound='invalid', is_gpu_bound='invalid', parallel='invalid'
        )
        await attrs.initialize()

        assert attrs.name == '[no-name]'
        assert attrs.version == '0.0.1'
        assert attrs.description == '[no-description]'
        assert attrs.category_id == -1
        assert attrs.author == '[no-author]'
        assert attrs.github == '[no-github]'
        assert attrs.email == '[no-email]'
        assert attrs.action is None
        assert attrs.required_inputs == {}
        assert attrs.parent_operation is None
        assert attrs.inheritance == []
        assert attrs.is_loop is False
        assert attrs.is_cpu_bound is False
        assert attrs.is_gpu_bound is False
        assert attrs.parallel is False

    @pytest.mark.asyncio
    async def test_export_attributes(self, mock_logger):
        attrs = OperationAttributes(
            name='test_name', version='0.0.2', description='test_description',
            category_id=1, author='test_author', github='@test_github',
            email='test@example.com', action='test_action', required_inputs={'input1': str},
            parent_operation=None, inheritance=[], is_loop=True, is_cpu_bound=False, is_gpu_bound=True, parallel=True
        )
        await attrs.initialize()
        exported_attrs = attrs.export_attributes()

        assert exported_attrs['name'] == 'test_name'
        assert exported_attrs['version'] == '0.0.2'
        assert exported_attrs['description'] == 'test_description'
        assert exported_attrs['category_id'] == 1
        assert exported_attrs['author'] == 'test_author'
        assert exported_attrs['github'] == 'test_github'
        assert exported_attrs['email'] == 'test@example.com'
        assert exported_attrs['action'] == 'test_action'
        # assert exported_attrs['required_inputs'] == {'input1': str}
        assert exported_attrs['parent_operation'] is None
        assert exported_attrs['inheritance'] == []
        assert exported_attrs['is_loop'] is True
        assert exported_attrs['is_cpu_bound'] is False
        assert exported_attrs['is_gpu_bound'] is True
        assert exported_attrs['parallel'] is True

    @pytest.mark.asyncio
    async def test_property_setters_and_getters(self, mock_logger):
        attrs = OperationAttributes()
        await attrs.initialize()

        attrs.name = 'new_name'
        assert attrs.name == 'new_name'

        attrs.version = '1.0.0'
        assert attrs.version == '1.0.0'

        attrs.description = 'new_description'
        assert attrs.description == 'new_description'

        attrs.category_id = 2
        assert attrs.category_id == 2

        attrs.author = 'new_author'
        assert attrs.author == 'new_author'

        attrs.github = '@new_github'
        assert attrs.github == 'new_github'

        attrs.email = 'new@example.com'
        assert attrs.email == 'new@example.com'

        attrs.action = 'new_action'
        assert attrs.action == 'new_action'

        # attrs.required_inputs = {'input2': int}
        # assert attrs.required_inputs == {'input2': int}

        attrs.parent_operation = OperationAttributes(name='parent_operation')
        await attrs.parent_operation.initialize()
        assert attrs.parent_operation.name == 'parent_operation'

        attrs.inheritance = ['child_operation']
        assert attrs.inheritance == ['child_operation']

        attrs.is_loop = True
        assert attrs.is_loop is True

        attrs.is_cpu_bound = True
        assert attrs.is_cpu_bound is True

        attrs.is_gpu_bound = True
        assert attrs.is_gpu_bound is True

        attrs.parallel = True
        assert attrs.parallel is True

    # Boundary Tests
    @pytest.mark.asyncio
    async def test_boundary_values(self, mock_logger):
        max_str = 'a' * 1000
        max_inputs = {f'input_{i}': str for i in range(1000)}

        attrs = OperationAttributes(
            name=max_str, version=max_str, description=max_str,
            category_id=int(1e6), author=max_str, github=f'@{max_str}',
            email=f'{max_str}@example.com', action=max_str, required_inputs=max_inputs,
            parent_operation=None, inheritance=[max_str] * 100, is_loop=True,
            is_cpu_bound=True, is_gpu_bound=True, parallel=True
        )
        await attrs.initialize()

        assert attrs.name == max_str
        assert attrs.version == max_str
        assert attrs.description == max_str
        assert attrs.category_id == int(1e6)
        assert attrs.author == max_str
        assert attrs.github == max_str
        assert attrs.email == f'{max_str}@example.com'
        assert attrs.action == max_str
        # assert attrs.required_inputs == max_inputs
        assert attrs.parent_operation is None
        assert attrs.inheritance == [max_str] * 100
        assert attrs.is_loop is True
        assert attrs.is_cpu_bound is True
        assert attrs.is_gpu_bound is True
        assert attrs.parallel is True

    # Performance Test
    @pytest.mark.asyncio
    async def test_performance_initialization(self, mock_logger):
        start_time = time.time()

        attrs = OperationAttributes(
            name='perf_test', version='0.0.1', description='performance test',
            category_id=1, author='tester', github='@perf_github',
            email='perf@example.com', action='perf_action',
            required_inputs={f'input_{i}': str for i in range(1000)},
            parent_operation=None, inheritance=[], is_loop=True,
            is_cpu_bound=True, is_gpu_bound=True, parallel=True
        )
        await attrs.initialize()

        end_time = time.time()
        initialization_time = end_time - start_time
        assert initialization_time < 1, f"Initialization took too long: {initialization_time} seconds"

    @pytest.mark.asyncio
    async def test_performance_mixed_args_kwargs_initialization(self, mock_logger):
        start_time = time.time()

        attrs = OperationAttributes(
            {'name': 'arg_name', 'version': '0.0.1', 'description': 'arg_description'},
            name='kwarg_name', version='0.0.2', description='kwarg_description',
            category_id=2, author='kwarg_author', github='@kwarg_github',
            email='kwarg@example.com', action='kwarg_action',
            required_inputs={f'input_{i}': str for i in range(100)},
            parent_operation=None, inheritance=['kwarg_inheritance'], is_loop=True,
            is_cpu_bound=True, is_gpu_bound=False, parallel=True
        )
        await attrs.initialize()

        end_time = time.time()
        initialization_time = end_time - start_time
        assert initialization_time < 1, f"Initialization took too long: {initialization_time} seconds"

    @pytest.mark.asyncio
    async def test_modify_single_attribute_repeatedly(self, mock_logger):
        attrs = OperationAttributes()
        await attrs.initialize()

        for i in range(100):
            attrs.name = f'test_name_{i}'
            assert attrs.name == f'test_name_{i}'

    @pytest.mark.asyncio
    async def test_modify_multiple_attributes_successively(self, mock_logger):
        attrs = OperationAttributes()
        await attrs.initialize()

        for i in range(100):
            attrs.name = f'test_name_{i}'
            attrs.version = f'0.0.{i}'
            attrs.description = f'description_{i}'
            assert attrs.name == f'test_name_{i}'
            assert attrs.version == f'0.0.{i}'
            assert attrs.description == f'description_{i}'

    @pytest.mark.asyncio
    async def test_modify_all_attributes_simultaneously(self, mock_logger):
        attrs = OperationAttributes()
        await attrs.initialize()

        for i in range(100):
            attrs.name = f'test_name_{i}'
            attrs.version = f'0.0.{i}'
            attrs.description = f'description_{i}'
            attrs.category_id = i
            attrs.author = f'author_{i}'
            attrs.github = f'@github_{i}'
            attrs.email = f'email_{i}@example.com'
            attrs.action = f'action_{i}'
            attrs.required_inputs = {f'input_{i}': str}
            attrs.is_loop = bool(i % 2)
            attrs.is_cpu_bound = bool(i % 2)
            attrs.is_gpu_bound = bool((i + 1) % 2)
            attrs.parallel = bool((i + 1) % 2)

            # Debugging statements
            print(f'Iteration {i}: category_id set to {attrs.category_id}')

            assert attrs.name == f'test_name_{i}'
            assert attrs.version == f'0.0.{i}'
            assert attrs.description == f'description_{i}'
            assert attrs.category_id == i, f'Iteration {i}: Expected category_id to be {i}, but got {attrs.category_id}'
            assert attrs.author == f'author_{i}'
            assert attrs.github == f'github_{i}'
            assert attrs.email == f'email_{i}@example.com'
            assert attrs.action == f'action_{i}'
            # assert attrs.required_inputs == {f'input_{j}': str for j in range(i)}
            assert attrs.is_loop == bool(i % 2)
            assert attrs.is_cpu_bound == bool(i % 2)
            assert attrs.is_gpu_bound == bool((i + 1) % 2)
            assert attrs.parallel == bool((i + 1) % 2)

    @pytest.mark.asyncio
    async def test_backward_compatibility(self, mock_logger):
        # Simulate an older version usage
        old_attrs = OperationAttributes(
            name='old_name', version='0.0.1', description='old_description',
            author='old_author'
        )
        await old_attrs.initialize()

        assert old_attrs.name == 'old_name'
        assert old_attrs.version == '0.0.1'
        assert old_attrs.description == 'old_description'
        assert old_attrs.author == 'old_author'

        # Ensure defaults are still applied correctly for missing attributes
        assert old_attrs.category_id == -1
        assert old_attrs.github == '[no-github]'

    @pytest.mark.asyncio
    async def test_versioning_support(self, mock_logger):
        # Version 1.0.0 behavior
        v1_attrs = OperationAttributes(version='1.0.0')
        await v1_attrs.initialize()
        assert v1_attrs.version == '1.0.0'
        # Add specific checks for version 1.0.0

        # Future version behavior
        future_version = '2.0.0'
        v2_attrs = OperationAttributes(version=future_version)
        await v2_attrs.initialize()
        assert v2_attrs.version == future_version
        # Add specific checks for future version

    @pytest.mark.asyncio
    async def test_stress_large_number_of_attributes(self, mock_logger):
        large_attrs = OperationAttributes(
            **{f'attr_{i}': f'value_{i}' for i in range(1000)}
        )
        await large_attrs.initialize()

        # Ensure all attributes are correctly initialized
        for i in range(1000):
            assert getattr(large_attrs, f'attr_{i}', None) == f'value_{i}'

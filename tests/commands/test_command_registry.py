import pytest
from unittest.mock import MagicMock, patch, Mock
from typing import List, Union, Dict

from research_analytics_suite.commands.CommandRegistry import CommandRegistry


class TestCommandRegistry:

    @pytest.fixture(autouse=True)
    def registry(self):
        registry = CommandRegistry()
        registry._logger = patch('research_analytics_suite.utils.CustomLogger').start()
        registry._logger.error = Mock()
        registry._logger.info = Mock()
        registry._config = MagicMock()
        registry._operation_control = MagicMock()
        registry._library_manifest = MagicMock()
        registry._workspace = MagicMock()

        registry._initialized = False  # Ensure it is uninitialized for each test
        yield registry
        registry._instance = None  # Reset singleton for isolation
        patch.stopall()

    @pytest.mark.asyncio
    async def test_initialization(self, registry):
        with patch('research_analytics_suite.utils.CustomLogger') as MockLogger, \
                patch('research_analytics_suite.utils.Config') as MockConfig, \
                patch('research_analytics_suite.operation_manager.control.OperationControl') as MockOperationControl, \
                patch('research_analytics_suite.library_manifest.LibraryManifest') as MockLibraryManifest, \
                patch('research_analytics_suite.data_engine.Workspace') as MockWorkspace:
            await registry.initialize()

            assert registry._logger is not None
            assert registry._config is not None
            assert registry._operation_control is not None
            assert registry._library_manifest is not None
            assert registry._workspace is not None
            assert registry._initialized

    def test_singleton_pattern(self):
        reg1 = CommandRegistry()
        reg2 = CommandRegistry()
        assert reg1 is reg2

    def test_register_command_with_single_return_type(self, registry):
        def sample_command(arg1: int, arg2: str) -> str:
            return f"{arg1} {arg2}"

        command_meta = {
            'func': sample_command,
            'name': 'sample_command',
            'class_name': None,
            'args': [{'name': 'arg1', 'type': int}, {'name': 'arg2', 'type': str}],
            'return_type': str,
            'is_method': False
        }
        registry._initialize_command(command_meta)
        assert 'sample_command' in registry._registry
        assert registry._registry['sample_command']['return_type'] == 'str'

    def test_register_command_with_list_return_type(self, registry):
        def sample_command(arg1: int, arg2: str) -> List[str]:
            return [str(arg1), arg2]

        command_meta = {
            'func': sample_command,
            'name': 'sample_command',
            'class_name': None,
            'args': [{'name': 'arg1', 'type': int}, {'name': 'arg2', 'type': str}],
            'return_type': list,
            'is_method': False
        }
        registry._initialize_command(command_meta)
        assert 'sample_command' in registry._registry
        assert registry._registry['sample_command']['return_type'] == 'list'

    def test_register_command_with_multiple_return_types(self, registry):
        def sample_command(arg1: int, arg2: str) -> Union[int, str]:
            return arg1 if arg1 > 0 else arg2

        command_meta = {
            'func': sample_command,
            'name': 'sample_command',
            'class_name': None,
            'args': [{'name': 'arg1', 'type': int}, {'name': 'arg2', 'type': str}],
            'return_type': [int, str],
            'is_method': False
        }
        registry._initialize_command(command_meta)
        assert 'sample_command' in registry._registry
        assert set(registry._registry['sample_command']['return_type']) == {'int', 'str'}

    def test_register_command_with_no_return_type(self, registry):
        def sample_command(arg1: int, arg2: str):
            pass

        command_meta = {
            'func': sample_command,
            'name': 'sample_command',
            'class_name': None,
            'args': [{'name': 'arg1', 'type': int}, {'name': 'arg2', 'type': str}],
            'return_type': None,
            'is_method': False
        }
        registry._initialize_command(command_meta)
        assert 'sample_command' in registry._registry
        assert registry._registry['sample_command']['return_type'] == 'None'

    def test_register_command_with_complex_type(self, registry):
        def sample_command(arg1: Dict[str, List[int]]) -> List[Dict[str, int]]:
            return [{k: v[0]} for k, v in arg1.items()]

        command_meta = {
            'func': sample_command,
            'name': 'sample_command',
            'class_name': None,
            'args': [{'name': 'arg1', 'type': Dict[str, List[int]]}],
            'return_type': List[Dict[str, int]],
            'is_method': False
        }
        registry._initialize_command(command_meta)
        assert 'sample_command' in registry._registry
        assert registry._registry['sample_command']['return_type'] == 'List[Dict[str, int]]'

    def test_register_instance(self, registry):
        class SampleClass:
            def method(self):
                return "instance method"

        instance = SampleClass()
        registry.register_instance(instance, 'runtime_1')
        assert registry._instances['runtime_1'] is instance

    @pytest.mark.asyncio
    async def test_execute_command_function(self, registry):
        def sample_command(arg1: int, arg2: str) -> str:
            return f"{arg1} {arg2}"

        registry._initialize_command({
            'func': sample_command,
            'name': 'sample_command',
            'class_name': None,
            'args': [{'name': 'arg1', 'type': int}, {'name': 'arg2', 'type': str}],
            'return_type': str,
            'is_method': False
        })
        result = await registry.execute_command('sample_command', None, 1, 'test')
        assert result == "1 test"

    @pytest.mark.asyncio
    async def test_execute_command_method(self, registry):
        class SampleClass:
            def method(self, arg: str) -> str:
                return f"Hello {arg}"

        instance = SampleClass()
        registry.register_instance(instance, 'runtime_1')
        registry._initialize_command({
            'func': SampleClass.method,
            'name': 'method',
            'class_name': 'SampleClass',
            'args': [{'name': 'arg', 'type': str}],
            'return_type': str,
            'is_method': True
        })
        result = await registry.execute_command('method', 'runtime_1', 'World')
        assert result == "Hello World"

    @patch('importlib.import_module')
    @patch('pkgutil.walk_packages')
    def test_discover_commands(self, mock_walk_packages, mock_import_module, registry):
        # Setup mock to simulate module and command discovery
        mock_module = MagicMock()
        mock_module.__path__ = ['mocked_path']
        mock_module.__name__ = 'mocked_module'
        mock_import_module.return_value = mock_module

        def sample_command():
            pass

        class SampleClass:
            def method(self):
                pass

        mock_walk_packages.return_value = [(None, 'mocked_module.sample_module', False)]
        mock_import_module.side_effect = lambda name: mock_module if name == 'mocked_module' else MagicMock(
            sample_command=sample_command,
            SampleClass=SampleClass
        )

        registry.discover_commands('mocked_module')

        assert 'sample_command' in registry._registry
        assert 'method' in registry._registry

    def test_pagination_next_page(self, registry):
        registry._registry = {f'command_{i}': {} for i in range(25)}  # Add sample commands
        registry.display_commands = MagicMock()
        registry.next_page()
        assert registry._current_page == 2
        registry.next_page()
        assert registry._current_page == 3

    def test_pagination_previous_page(self, registry):
        registry._current_page = 3
        registry._registry = {f'command_{i}': {} for i in range(25)}  # Add sample commands
        registry.display_commands = MagicMock()
        registry.previous_page()
        assert registry._current_page == 2
        registry.previous_page()
        assert registry._current_page == 1

    def test_clear_search(self, registry):
        registry._search_keyword = 'test'
        registry.display_commands = MagicMock()
        registry.clear_search()
        assert registry._search_keyword is None

    def test_clear_category(self, registry):
        registry._current_category = 'test_category'
        registry.display_commands = MagicMock()
        registry.clear_category()
        assert registry._current_category is None

    def test_search_commands(self, registry):
        def sample_command():
            pass

        command_meta = {
            'func': sample_command,
            'name': 'sample_command',
            'class_name': None,
            'args': [],
            'return_type': None,
            'is_method': False,
            'tags': ['test'],
            'description': 'sample description',
            'category': 'test_category'
        }
        registry._initialize_command(command_meta)
        results = registry.search_commands('sample')
        assert 'sample_command' in results

    def test_get_commands_by_category(self, registry):
        def sample_command():
            pass

        command_meta = {
            'func': sample_command,
            'name': 'sample_command',
            'class_name': None,
            'args': [],
            'return_type': None,
            'is_method': False,
            'category': 'test_category'
        }
        registry._initialize_command(command_meta)
        registry.categorize_commands()  # Ensure commands are categorized
        results = registry.get_commands_by_category('test_category')
        assert 'sample_command' in results

    def test_display_command_details(self, registry):
        def sample_command():
            pass

        command_meta = {
            'func': sample_command,
            'name': 'sample_command',
            'class_name': None,
            'args': [],
            'return_type': None,
            'is_method': False,
            'description': 'This is a test command.',
            'tags': ['test']
        }
        registry._initialize_command(command_meta)
        with patch.object(registry._logger, 'info') as mock_logger_info:
            registry.display_command_details('sample_command')
            mock_logger_info.assert_any_call(f"\nCommand: sample_command")
            mock_logger_info.assert_any_call(f"  Description:\tThis is a test command.")

    def test_display_nonexistent_command_details(self, registry):
        registry.display_command_details('nonexistent_command')
        registry._logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_initialize_with_missing_components(self, registry):
        with patch('research_analytics_suite.utils.CustomLogger', side_effect=Exception("Logger init failed")), \
                patch('research_analytics_suite.utils.Config'), \
                patch('research_analytics_suite.operation_manager.control.OperationControl'), \
                patch('research_analytics_suite.library_manifest.LibraryManifest'), \
                patch('research_analytics_suite.data_engine.Workspace'):
            with pytest.raises(Exception) as excinfo:
                await registry.initialize()
            assert str(excinfo.value) == "Logger init failed"
            registry._logger.error.assert_called()

    def test_register_command_with_nested_return_type(self, registry):
        def sample_command(arg1: int) -> List[Dict[str, Union[int, str]]]:
            return [{"key": arg1}]

        command_meta = {
            'func': sample_command,
            'name': 'sample_command',
            'class_name': None,
            'args': [{'name': 'arg1', 'type': int}],
            'return_type': List[Dict[str, Union[int, str]]],
            'is_method': False
        }
        registry._initialize_command(command_meta)
        assert 'sample_command' in registry._registry
        assert registry._registry['sample_command']['return_type'] == 'List[Dict[str, Union[int, str]]]'

    # Test for registry property
    def test_registry_property(self, registry):
        new_registry = {'new_command': {'name': 'new_command'}}
        registry.registry = new_registry
        assert registry.registry == new_registry

    # Test for search property
    def test_search_property(self, registry):
        registry.search = 'new_search'
        assert registry.search == 'new_search'

    # Test for categories property
    def test_categories_property(self, registry):
        registry._categories = {'cat1': {}, 'cat2': {}}
        assert registry.categories == {'cat1': {}, 'cat2': {}}

    # Test for current_page property
    def test_current_page_property(self, registry):
        registry._current_page = 5
        assert registry.current_page == 5

    # Test for page_size property
    def test_page_size_property(self, registry):
        registry.page_size = 20
        assert registry.page_size == 20

    # Test for current_category property
    def test_current_category_property(self, registry):
        registry.current_category = 'new_category'
        assert registry.current_category == 'new_category'

    def test_display_command_details_for_method(self, registry):
        class SampleClass:
            def method(self):
                """This is a method."""
                pass

        command_meta = {
            'func': SampleClass.method,
            'name': 'method',
            'class_name': 'SampleClass',
            'args': [],
            'return_type': None,
            'is_method': True,
            'description': 'This is a method.',
            'tags': ['test']
        }
        registry._initialize_command(command_meta)

        with patch.object(registry._logger, 'info') as mock_logger_info:
            registry.display_command_details('method')
            mock_logger_info.assert_any_call(f"  Class:\tSampleClass")
            mock_logger_info.assert_any_call(f"  Method:\tmethod")
import pytest
from unittest.mock import MagicMock, patch

from research_analytics_suite.commands import CommandRegistry


class TestCommandRegistry:

    @pytest.fixture(autouse=True)
    def registry(self):
        registry = CommandRegistry()
        registry._initialized = False  # Ensure it is uninitialized for each test
        yield registry
        registry._instance = None  # Reset singleton for isolation

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

    def test_register_command(self, registry):
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

    def test_register_instance(self, registry):
        class SampleClass:
            def method(self):
                return "instance method"

        instance = SampleClass()
        registry.register_instance(instance, 'runtime_1')
        assert registry._instances['runtime_1'] is instance

    def test_execute_command_function(self, registry):
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
        result = registry.execute_command('sample_command', None, 1, 'test')
        assert result == "1 test"

    def test_execute_command_method(self, registry):
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
        result = registry.execute_command('method', 'runtime_1', 'World')
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
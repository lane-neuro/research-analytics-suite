from unittest.mock import patch

from research_analytics_suite.commands import register_commands, command


class TestRegisterCommandsDecorator:

    @patch('research_analytics_suite.commands.CommandDecorators.temp_command_registry', new_callable=list)
    def test_register_single_command(self, mock_temp_command_registry):
        @register_commands
        class TestClass:
            @command
            def test_method(self, a: int) -> str:
                return "test"

        assert len(mock_temp_command_registry) == 1
        assert mock_temp_command_registry[0]['name'] == 'test_method'
        assert mock_temp_command_registry[0]['class_name'] == 'TestClass'
        assert mock_temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int}
        ]
        assert mock_temp_command_registry[0]['return_type'] == str
        assert mock_temp_command_registry[0]['is_method'] is True

    @patch('research_analytics_suite.commands.CommandDecorators.temp_command_registry', new_callable=list)
    def test_register_multiple_commands(self, mock_temp_command_registry):
        @register_commands
        class TestClass:
            @command
            def test_method_1(self, a: int) -> str:
                return "test1"

            @command
            def test_method_2(self, b: str) -> int:
                return 42

        assert len(mock_temp_command_registry) == 2
        assert mock_temp_command_registry[0]['name'] == 'test_method_1'
        assert mock_temp_command_registry[0]['class_name'] == 'TestClass'
        assert mock_temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int}
        ]
        assert mock_temp_command_registry[0]['return_type'] == str
        assert mock_temp_command_registry[0]['is_method'] is True

        assert mock_temp_command_registry[1]['name'] == 'test_method_2'
        assert mock_temp_command_registry[1]['class_name'] == 'TestClass'
        assert mock_temp_command_registry[1]['args'] == [
            {'name': 'b', 'type': str}
        ]
        assert mock_temp_command_registry[1]['return_type'] == int
        assert mock_temp_command_registry[1]['is_method'] is True

    @patch('research_analytics_suite.commands.CommandDecorators.temp_command_registry', new_callable=list)
    def test_register_no_commands(self, mock_temp_command_registry):
        @register_commands
        class TestClass:
            def regular_method(self):
                pass

        assert len(mock_temp_command_registry) == 0

    @patch('research_analytics_suite.commands.CommandDecorators.temp_command_registry', new_callable=list)
    def test_mixed_command_non_command_methods(self, mock_temp_command_registry):
        @register_commands
        class TestClass:
            @command
            def command_method(self, a: int) -> str:
                return "command"

            def non_command_method(self):
                pass

        assert len(mock_temp_command_registry) == 1
        assert mock_temp_command_registry[0]['name'] == 'command_method'
        assert mock_temp_command_registry[0]['class_name'] == 'TestClass'
        assert mock_temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int}
        ]
        assert mock_temp_command_registry[0]['return_type'] == str
        assert mock_temp_command_registry[0]['is_method'] is True

    @patch('research_analytics_suite.commands.CommandDecorators.temp_command_registry', new_callable=list)
    def test_register_command_with_default_args(self, mock_temp_command_registry):
        @register_commands
        class TestClass:
            @command
            def method_with_defaults(self, a: int, b: str = "default") -> str:
                return "test"

        assert len(mock_temp_command_registry) == 1
        assert mock_temp_command_registry[0]['name'] == 'method_with_defaults'
        assert mock_temp_command_registry[0]['class_name'] == 'TestClass'
        assert mock_temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int},
            {'name': 'b', 'type': str}
        ]
        assert mock_temp_command_registry[0]['return_type'] == str
        assert mock_temp_command_registry[0]['is_method'] is True

    @patch('research_analytics_suite.commands.CommandDecorators.temp_command_registry', new_callable=list)
    def test_register_command_with_variable_args(self, mock_temp_command_registry):
        @register_commands
        class TestClass:
            @command
            def method_with_varargs(self, *args: int) -> str:
                return "test"

        assert len(mock_temp_command_registry) == 1
        assert mock_temp_command_registry[0]['name'] == 'method_with_varargs'
        assert mock_temp_command_registry[0]['class_name'] == 'TestClass'
        assert mock_temp_command_registry[0]['args'] == [
            {'name': 'args', 'type': int}
        ]
        assert mock_temp_command_registry[0]['return_type'] == str
        assert mock_temp_command_registry[0]['is_method'] is True

    @patch('research_analytics_suite.commands.CommandDecorators.temp_command_registry', new_callable=list)
    def test_register_static_method(self, mock_temp_command_registry):
        @register_commands
        class TestClass:
            @staticmethod
            @command
            def static_method(a: int) -> str:
                return "test"

        assert len(mock_temp_command_registry) == 1
        assert mock_temp_command_registry[0]['name'] == 'static_method'
        assert mock_temp_command_registry[0]['class_name'] == 'TestClass'
        assert mock_temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int}
        ]
        assert mock_temp_command_registry[0]['return_type'] == str
        assert mock_temp_command_registry[0]['is_method'] is False

    @patch('research_analytics_suite.commands.CommandDecorators.temp_command_registry', new_callable=list)
    def test_register_class_method(self, mock_temp_command_registry):
        @register_commands
        class TestClass:
            @classmethod
            @command
            def class_method(cls, a: int) -> str:
                return "test"

        assert len(mock_temp_command_registry) == 1
        assert mock_temp_command_registry[0]['name'] == 'class_method'
        assert mock_temp_command_registry[0]['class_name'] == 'TestClass'
        assert mock_temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int}
        ]
        assert mock_temp_command_registry[0]['return_type'] == str
        assert mock_temp_command_registry[0]['is_method'] is True

    @patch('research_analytics_suite.commands.CommandDecorators.temp_command_registry', new_callable=list)
    def test_register_command_with_complex_types(self, mock_temp_command_registry):
        @register_commands
        class TestClass:
            @command
            def method_with_complex_types(self, a: dict, b: list) -> dict:
                return {"test": "value"}

        assert len(mock_temp_command_registry) == 1
        assert mock_temp_command_registry[0]['name'] == 'method_with_complex_types'
        assert mock_temp_command_registry[0]['class_name'] == 'TestClass'
        assert mock_temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': dict},
            {'name': 'b', 'type': list}
        ]
        assert mock_temp_command_registry[0]['return_type'] == dict
        assert mock_temp_command_registry[0]['is_method'] is True

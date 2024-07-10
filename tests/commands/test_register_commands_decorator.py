import pytest
import inspect
from typing import get_type_hints
from unittest.mock import patch

from research_analytics_suite.commands.CommandRegistry import register_commands, command


class TestRegisterCommandsDecorator:

    @patch('research_analytics_suite.commands.CommandRegistry.temp_command_registry', new_callable=list)
    def test_register_single_command(self, mock_temp_command_registry):
        @register_commands
        class TestClass:
            @command
            def test_method(self, a: int) -> str:
                return "test"

        assert len(mock_temp_command_registry) == 1
        assert mock_temp_command_registry[0]['name'] == 'TestClass.test_method'
        assert mock_temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int}
        ]
        assert mock_temp_command_registry[0]['return_type'] == str
        assert mock_temp_command_registry[0]['is_method'] is True

    @patch('research_analytics_suite.commands.CommandRegistry.temp_command_registry', new_callable=list)
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
        assert mock_temp_command_registry[0]['name'] == 'TestClass.test_method_1'
        assert mock_temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int}
        ]
        assert mock_temp_command_registry[0]['return_type'] == str
        assert mock_temp_command_registry[0]['is_method'] is True

        assert mock_temp_command_registry[1]['name'] == 'TestClass.test_method_2'
        assert mock_temp_command_registry[1]['args'] == [
            {'name': 'b', 'type': str}
        ]
        assert mock_temp_command_registry[1]['return_type'] == int
        assert mock_temp_command_registry[1]['is_method'] is True

    @patch('research_analytics_suite.commands.CommandRegistry.temp_command_registry', new_callable=list)
    def test_register_no_commands(self, mock_temp_command_registry):
        @register_commands
        class TestClass:
            def regular_method(self):
                pass

        assert len(mock_temp_command_registry) == 0

    @patch('research_analytics_suite.commands.CommandRegistry.temp_command_registry', new_callable=list)
    def test_mixed_command_non_command_methods(self, mock_temp_command_registry):
        @register_commands
        class TestClass:
            @command
            def command_method(self, a: int) -> str:
                return "command"

            def non_command_method(self):
                pass

        assert len(mock_temp_command_registry) == 1
        assert mock_temp_command_registry[0]['name'] == 'TestClass.command_method'
        assert mock_temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int}
        ]
        assert mock_temp_command_registry[0]['return_type'] == str
        assert mock_temp_command_registry[0]['is_method'] is True

# test_register_commands_decorator.py

import pytest
import inspect
from typing import get_type_hints

from research_analytics_suite.commands.CommandRegistry import temp_command_registry, register_commands, command


@pytest.fixture(autouse=True)
def clear_registry():
    """
    Fixture to clear the temporary command registry before each test.
    """
    temp_command_registry.clear()
    yield
    temp_command_registry.clear()


class TestRegisterCommandsDecorator:
    def test_register_single_command(self):
        @register_commands
        class TestClass:
            @command
            def test_method(self, a: int) -> str:
                return "test"

        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == 'TestClass.test_method'
        assert temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int}
        ]
        assert temp_command_registry[0]['return_type'] == str
        assert temp_command_registry[0]['is_method'] is True

    def test_register_multiple_commands(self):
        @register_commands
        class TestClass:
            @command
            def test_method_1(self, a: int) -> str:
                return "test1"

            @command
            def test_method_2(self, b: str) -> int:
                return 42

        assert len(temp_command_registry) == 2
        assert temp_command_registry[0]['name'] == 'TestClass.test_method_1'
        assert temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int}
        ]
        assert temp_command_registry[0]['return_type'] == str
        assert temp_command_registry[0]['is_method'] is True

        assert temp_command_registry[1]['name'] == 'TestClass.test_method_2'
        assert temp_command_registry[1]['args'] == [
            {'name': 'b', 'type': str}
        ]
        assert temp_command_registry[1]['return_type'] == int
        assert temp_command_registry[1]['is_method'] is True

    def test_register_no_commands(self):
        @register_commands
        class TestClass:
            def regular_method(self):
                pass

        assert len(temp_command_registry) == 0

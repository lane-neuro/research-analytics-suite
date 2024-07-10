# test_command_decorator.py

import pytest
import inspect
from typing import get_type_hints
from research_analytics_suite.commands.CommandRegistry import command, temp_command_registry


@pytest.fixture(autouse=True)
def clear_registry():
    """
    Fixture to clear the temporary command registry before each test.
    """
    temp_command_registry.clear()
    yield
    temp_command_registry.clear()


class TestCommandDecorator:
    def test_command_registration(self):
        @command
        def test_func(a: int, b: str) -> bool:
            return True

        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == 'test_func'
        assert temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int},
            {'name': 'b', 'type': str}
        ]
        assert temp_command_registry[0]['return_type'] == bool

    def test_method_registration(self):
        class TestClass:
            @command
            def test_method(self, a: int) -> str:
                return "test"

        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == 'test_method'
        assert temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int}
        ]
        assert temp_command_registry[0]['return_type'] == str
        assert temp_command_registry[0]['is_method'] is True

    def test_no_return_type(self):
        @command
        def test_func_no_return(a: int):
            pass

        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == 'test_func_no_return'
        assert temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int}
        ]
        assert temp_command_registry[0]['return_type'] is None

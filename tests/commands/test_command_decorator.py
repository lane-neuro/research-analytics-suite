# test_command_decorator.py

import pytest
import inspect
from typing import get_type_hints, Optional
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

    def test_default_arguments(self):
        @command
        def test_func_default(a: int = 10, b: str = 'default') -> Optional[str]:
            return None

        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == 'test_func_default'
        assert temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int},
            {'name': 'b', 'type': str}
        ]
        assert temp_command_registry[0]['return_type'] == Optional[str]

    def test_various_types(self):
        @command
        def test_func_various(a: int, b: float, c: bool, d: Optional[str] = None) -> list:
            return [a, b, c, d]

        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == 'test_func_various'
        assert temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int},
            {'name': 'b', 'type': float},
            {'name': 'c', 'type': bool},
            {'name': 'd', 'type': Optional[str]}
        ]
        assert temp_command_registry[0]['return_type'] == list

    def test_keyword_only_arguments(self):
        @command
        def test_func_kw_only(a: int, *, b: str) -> dict:
            return {'a': a, 'b': b}

        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == 'test_func_kw_only'
        assert temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int},
            {'name': 'b', 'type': str}
        ]
        assert temp_command_registry[0]['return_type'] == dict

    def test_self_handling(self):
        class TestClass:
            @command
            def test_method(self, a: int, b: str) -> bool:
                return True

        instance = TestClass()
        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == 'test_method'
        assert temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int},
            {'name': 'b', 'type': str}
        ]
        assert temp_command_registry[0]['return_type'] == bool
        assert temp_command_registry[0]['is_method'] is True

    def test_var_args(self):
        @command
        def test_func_var_args(a: int, *args: str) -> list:
            return [a, *args]

        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == 'test_func_var_args'
        assert temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int},
            {'name': 'args', 'type': str}
        ]
        assert temp_command_registry[0]['return_type'] == list

    def test_var_kwargs(self):
        @command
        def test_func_var_kwargs(a: int, **kwargs: str) -> dict:
            return {'a': a, **kwargs}

        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == 'test_func_var_kwargs'
        assert temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int},
            {'name': 'kwargs', 'type': str}
        ]
        assert temp_command_registry[0]['return_type'] == dict

    def test_combined_args(self):
        @command
        def test_func_combined(a: int, b: str, *args: float, c: bool = True, **kwargs: int) -> tuple:
            return (a, b, args, c, kwargs)

        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == 'test_func_combined'
        assert temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int},
            {'name': 'b', 'type': str},
            {'name': 'args', 'type': float},
            {'name': 'c', 'type': bool},
            {'name': 'kwargs', 'type': int}
        ]
        assert temp_command_registry[0]['return_type'] == tuple
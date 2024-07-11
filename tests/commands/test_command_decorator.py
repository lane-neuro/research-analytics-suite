import asyncio
from functools import wraps

import pytest
from typing import Optional, List, Dict, Union, Callable, Any
from research_analytics_suite.commands.CommandDecorators import command, temp_command_registry


# Define some user-defined types
class User:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age


class Product:
    def __init__(self, _id: int, name: str, price: float):
        self.id = _id
        self.name = name
        self.price = price


@pytest.fixture(autouse=True)
def clear_registry():
    """
    Fixture to clear the temporary command registry before each test.
    """
    temp_command_registry.clear()
    yield
    temp_command_registry.clear()


def additional_decorator(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapped


class TestCommandDecorator:
    def test_command_registration(self):
        @command
        def test_func(a: int, b: str) -> bool:
            return True

        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == 'test_func'
        assert temp_command_registry[0]['class_name'] is None
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
        assert temp_command_registry[0]['class_name'] == 'TestClass'
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
        assert temp_command_registry[0]['class_name'] is None
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
        assert temp_command_registry[0]['class_name'] is None
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
        assert temp_command_registry[0]['class_name'] is None
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
        assert temp_command_registry[0]['class_name'] is None
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
        assert temp_command_registry[0]['class_name'] == 'TestClass'
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
        assert temp_command_registry[0]['class_name'] is None
        assert temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int},
            {'name': 'args', 'type': str}
        ]
        assert temp_command_registry[0]['return_type'] == list
        assert temp_command_registry[0]['is_method'] is False

    def test_var_kwargs(self):
        @command
        def test_func_var_kwargs(a: int, **kwargs: str) -> dict:
            return {'a': a, **kwargs}

        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == 'test_func_var_kwargs'
        assert temp_command_registry[0]['class_name'] is None
        assert temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int},
            {'name': 'kwargs', 'type': str}
        ]
        assert temp_command_registry[0]['return_type'] == dict
        assert temp_command_registry[0]['is_method'] is False

    def test_combined_args(self):
        @command
        def test_func_combined(a: int, b: str, *args: float, c: bool = True, **kwargs: int) -> tuple:
            return (a, b, args, c, kwargs)

        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == 'test_func_combined'
        assert temp_command_registry[0]['class_name'] is None
        assert temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int},
            {'name': 'b', 'type': str},
            {'name': 'args', 'type': float},
            {'name': 'c', 'type': bool},
            {'name': 'kwargs', 'type': int}
        ]
        assert temp_command_registry[0]['return_type'] == tuple
        assert temp_command_registry[0]['is_method'] is False

    def test_user_defined_types(self):
        @command
        def test_func_user_defined(user: User, product: Product) -> str:
            return f"{user.name} bought {product.name}"

        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == 'test_func_user_defined'
        assert temp_command_registry[0]['class_name'] is None
        assert temp_command_registry[0]['args'] == [
            {'name': 'user', 'type': User},
            {'name': 'product', 'type': Product}
        ]
        assert temp_command_registry[0]['return_type'] == str
        assert temp_command_registry[0]['is_method'] is False

    def test_complex_nested_types(self):
        @command
        def test_func_nested(a: List[Dict[str, Optional[User]]]) -> List[Dict[str, Optional[User]]]:
            return a

        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == 'test_func_nested'
        assert temp_command_registry[0]['class_name'] is None
        assert temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': List[Dict[str, Optional[User]]]}
        ]
        assert temp_command_registry[0]['return_type'] == List[Dict[str, Optional[User]]]
        assert temp_command_registry[0]['is_method'] is False

    def test_complex_default_values(self):
        @command
        def test_func_complex_defaults(a: int = 1, b: List[int] = [1, 2, 3],
                                       c: Dict[str, str] = {"key": "value"}) -> None:
            pass

        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == 'test_func_complex_defaults'
        assert temp_command_registry[0]['class_name'] is None
        assert temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int},
            {'name': 'b', 'type': List[int]},
            {'name': 'c', 'type': Dict[str, str]}
        ]
        assert temp_command_registry[0]['return_type'] is None
        assert temp_command_registry[0]['is_method'] is False

    def test_callable_argument(self):
        @command
        def test_func_callable(a: int, b: callable) -> None:
            pass

        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == 'test_func_callable'
        assert temp_command_registry[0]['class_name'] is None
        assert temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int},
            {'name': 'b', 'type': callable}
        ]
        assert temp_command_registry[0]['return_type'] is None
        assert temp_command_registry[0]['is_method'] is False

    def test_lambda_argument(self):
        @command
        def test_func_lambda(a: int, func: Callable[[int], int]) -> int:
            return func(a)

        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == 'test_func_lambda'
        assert temp_command_registry[0]['class_name'] is None
        assert temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int},
            {'name': 'func', 'type': Callable[[int], int]}
        ]
        assert temp_command_registry[0]['return_type'] == int
        assert temp_command_registry[0]['is_method'] is False

    def test_async_function(self):
        @command
        async def test_func_async(a: int, b: str) -> bool:
            await asyncio.sleep(0.1)
            return True

        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == 'test_func_async'
        assert temp_command_registry[0]['class_name'] is None
        assert temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int},
            {'name': 'b', 'type': str}
        ]
        assert temp_command_registry[0]['return_type'] == bool
        assert temp_command_registry[0]['is_method'] is False

    def test_async_method(self):
        class TestClass:
            @command
            async def test_method_async(self, a: int) -> str:
                await asyncio.sleep(0.1)
                return "test"

        instance = TestClass()
        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == 'test_method_async'
        assert temp_command_registry[0]['class_name'] == 'TestClass'
        assert temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int}
        ]
        assert temp_command_registry[0]['return_type'] == str
        assert temp_command_registry[0]['is_method'] is True

    def test_union_types(self):
        @command
        def test_func_union(a: Union[int, str], b: Optional[bool] = None) -> Union[str, None]:
            return str(a) if b else None

        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == 'test_func_union'
        assert temp_command_registry[0]['class_name'] is None
        assert temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': Union[int, str]},
            {'name': 'b', 'type': Optional[bool]}
        ]
        assert temp_command_registry[0]['return_type'] == Union[str, None]
        assert temp_command_registry[0]['is_method'] is False

    def test_mixed_type_hints(self):
        @command
        def test_func_mixed(a: int, b: Union[str, float], func: Callable[[int], str]) -> str:
            return func(a)

        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == 'test_func_mixed'
        assert temp_command_registry[0]['class_name'] is None
        assert temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int},
            {'name': 'b', 'type': Union[str, float]},
            {'name': 'func', 'type': Callable[[int], str]}
        ]
        assert temp_command_registry[0]['return_type'] == str
        assert temp_command_registry[0]['is_method'] is False

    def test_multiple_decorators(self):
        @additional_decorator
        @command
        def test_func_multiple_decorators(a: int, b: str) -> str:
            return f"{a} - {b}"

        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == 'test_func_multiple_decorators'
        assert temp_command_registry[0]['class_name'] is None
        assert temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int},
            {'name': 'b', 'type': str}
        ]
        assert temp_command_registry[0]['return_type'] == str
        assert temp_command_registry[0]['is_method'] is False

    def test_missing_type_hints(self):
        @command
        def test_func_missing_type_hints(a, b):
            return a + b

        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == 'test_func_missing_type_hints'
        assert temp_command_registry[0]['class_name'] is None
        assert temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': any},
            {'name': 'b', 'type': any}
        ]
        assert temp_command_registry[0]['return_type'] is None
        assert temp_command_registry[0]['is_method'] is False

    def test_invalid_type_hints(self):
        @command
        def test_func_invalid_type_hints(a: "invalid_type") -> str:
            return str(a)

        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == 'test_func_invalid_type_hints'
        assert temp_command_registry[0]['class_name'] is None
        assert temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': 'invalid_type'}
        ]
        assert temp_command_registry[0]['return_type'] == str

    def test_no_arguments(self):
        @command
        def test_func_no_arguments() -> None:
            pass

        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == 'test_func_no_arguments'
        assert temp_command_registry[0]['class_name'] is None
        assert temp_command_registry[0]['args'] == []
        assert temp_command_registry[0]['return_type'] is None
        assert temp_command_registry[0]['is_method'] is False

    def test_untyped_arguments(self):
        @command
        def test_func_untyped_arguments(a, b: int) -> Any:
            return a + b

        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == 'test_func_untyped_arguments'
        assert temp_command_registry[0]['class_name'] is None
        assert temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': any},
            {'name': 'b', 'type': int}
        ]
        assert temp_command_registry[0]['return_type'] == Any
        assert temp_command_registry[0]['is_method'] is False

    def test_edge_case_function_name(self):
        @command
        def __str__(a: int, b: int) -> str:
            return f"{a} + {b}"

        assert len(temp_command_registry) == 1
        assert temp_command_registry[0]['name'] == '__str__'
        assert temp_command_registry[0]['class_name'] is None
        assert temp_command_registry[0]['args'] == [
            {'name': 'a', 'type': int},
            {'name': 'b', 'type': int}
        ]
        assert temp_command_registry[0]['return_type'] == str
        assert temp_command_registry[0]['is_method'] is False

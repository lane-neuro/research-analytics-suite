import pytest
import pytest_asyncio
import ast
from types import SimpleNamespace

# Assuming SAFE_BUILTINS and SAFE_MODULES are defined elsewhere
SAFE_BUILTINS = {'None': None, 'True': True, 'False': False}
SAFE_MODULES = {}


# Mock MemorySlot class for testing
class MemorySlot:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    async def get_data_by_key(self, key):
        return self.value


@pytest_asyncio.fixture
async def code_executor():
    from research_analytics_suite.operation_manager.operations.core.execution.PrepareAction import _execute_code_action

    async def execute(code, memory_inputs=None):
        action_callable = await _execute_code_action(code, memory_inputs)
        return await action_callable()

    return execute


class TestExecuteCodeAction:

    @pytest.mark.asyncio
    async def test_simple_code_execution(self, code_executor):
        code = "result = 1 + 1"
        result = await code_executor(code)
        assert result['result'] == 2

    @pytest.mark.asyncio
    async def test_code_with_memory_inputs(self, code_executor):
        memory_inputs = [
            MemorySlot('a', 10),
            MemorySlot('b', 20)
        ]
        code = "result = a + b"
        result = await code_executor(code, memory_inputs)
        assert result['result'] == 30

    @pytest.mark.asyncio
    async def test_code_with_none_input(self, code_executor):
        memory_inputs = [
            MemorySlot('a', (type(None),))
        ]
        code = "result = a is None"
        result = await code_executor(code, memory_inputs)
        assert result['result'] is True

    @pytest.mark.asyncio
    async def test_code_with_import_module(self, code_executor):
        memory_inputs = [
            MemorySlot('math', ('module', 'math'))
        ]
        code = "result = math.sqrt(16)"
        result = await code_executor(code, memory_inputs)
        assert result['result'] == 4.0

    @pytest.mark.asyncio
    async def test_code_with_function_input(self, code_executor):
        def test_func(x):
            return x * 2

        memory_inputs = [
            MemorySlot('double', ('function', test_func)),
            MemorySlot('value', 5)
        ]
        code = "result = double(value)"
        result = await code_executor(code, memory_inputs)
        assert result['result'] == 10

    @pytest.mark.asyncio
    async def test_code_with_class_input(self, code_executor):
        class TestClass:
            def __init__(self, x):
                self.x = x

            def get_value(self):
                return self.x

        memory_inputs = [
            MemorySlot('TestClass', ('class', TestClass)),
            MemorySlot('value', 5)
        ]
        code = """
tc = TestClass(value)
result = tc.get_value()
"""
        result = await code_executor(code, memory_inputs)
        assert result['result'] == 5

    @pytest.mark.asyncio
    async def test_code_with_error(self, code_executor):
        code = "result = 1 / 0"
        with pytest.raises(RuntimeError, match="Error executing code:"):
            await code_executor(code)

    @pytest.mark.asyncio
    async def test_invalid_import(self, code_executor):
        memory_inputs = [
            MemorySlot('nonexistent', ('module', 'nonexistent_module'))
        ]
        code = "result = nonexistent is None"
        result = await code_executor(code, memory_inputs)
        assert result['result'] is True

    @pytest.mark.asyncio
    async def test_handling_builtin_function(self, code_executor):
        memory_inputs = [
            MemorySlot('print', ('builtin_function_or_method', print)),
            MemorySlot('value', "Hello, World!")
        ]
        code = "result = print(value)"
        result = await code_executor(code, memory_inputs)
        assert result['result'] is None

    @pytest.mark.asyncio
    async def test_handling_method_wrapper(self, code_executor):
        class Example:
            def method(self):
                return "example"

        instance = Example()
        memory_inputs = [
            MemorySlot('method', ('method-wrapper', instance.method)),
        ]
        code = "result = method()"
        result = await code_executor(code, memory_inputs)
        assert result['result'] == "example"

    @pytest.mark.asyncio
    async def test_handling_general_callable(self, code_executor):
        class CallableClass:
            def __call__(self, x):
                return x * 3

        callable_instance = CallableClass()
        memory_inputs = [
            MemorySlot('callable_instance', ('function', callable_instance)),
            MemorySlot('value', 4)
        ]
        code = "result = callable_instance(value)"
        result = await code_executor(code, memory_inputs)
        assert result['result'] == 12

    @pytest.mark.asyncio
    async def test_code_with_callable_tuple(self, code_executor):
        def increment(x):
            return x + 1

        memory_inputs = [
            MemorySlot('inc', (increment, 5))
        ]
        code = "result = inc"
        result = await code_executor(code, memory_inputs)
        assert result['result'] == 6

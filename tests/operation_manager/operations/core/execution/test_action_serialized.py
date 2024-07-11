import pytest
import inspect

from research_analytics_suite.operation_manager.operations.core.execution import action_serialized


class TestActionSerialized:
    def test_action_is_string(self):
        action = "test_string"
        result = action_serialized(action)
        assert result == "test_string"

    def test_action_is_callable_with_source(self):
        def sample_function():
            return "sample"

        result = action_serialized(sample_function)
        source = inspect.getsource(sample_function).strip()
        assert result.strip() == source.strip()

    def test_action_is_property(self):
        class SampleClass:
            @property
            def sample_property(self):
                return "sample"

        result = action_serialized(SampleClass.sample_property)
        expected_repr = f"<property object at {hex(id(SampleClass.sample_property))}>"
        assert result == expected_repr

    def test_action_is_other_type(self):
        action = 42
        result = action_serialized(action)
        assert result == repr(action)


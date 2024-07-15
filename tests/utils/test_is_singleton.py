import pytest
from unittest.mock import MagicMock

from research_analytics_suite.utils.SingletonChecker import is_singleton


class TestIsSingleton:

    def test_singleton_class(self):
        class SingletonClass:
            _instance = None

            def __new__(cls, *args, **kwargs):
                if cls._instance is None:
                    cls._instance = super(SingletonClass, cls).__new__(cls, *args, **kwargs)
                return cls._instance

        SingletonClass._instance = SingletonClass()
        assert is_singleton(SingletonClass) is True

    def test_regular_class(self):
        class RegularClass:
            pass

        assert is_singleton(RegularClass) is False

    def test_non_singleton_class_with_instance_attr(self):
        class NonSingletonClass:
            _instance = object()  # Different instance

        assert is_singleton(NonSingletonClass) is False

    def test_class_without_instance_attr(self):
        class NoInstanceAttrClass:
            pass

        assert is_singleton(NoInstanceAttrClass) is False

    def test_class_with_instance_attr_none(self):
        class NoneInstanceAttrClass:
            _instance = None

        assert is_singleton(NoneInstanceAttrClass) is False

    def test_class_with_instance_attr_invalid_type(self):
        class InvalidInstanceAttrClass:
            _instance = 12345  # Invalid type for _instance

        assert is_singleton(InvalidInstanceAttrClass) is False

    def test_class_with_instance_attr_different_instance(self):
        class DifferentInstanceClass:
            _instance = object()

        assert is_singleton(DifferentInstanceClass) is False

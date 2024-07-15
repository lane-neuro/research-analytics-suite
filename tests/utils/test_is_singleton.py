import pytest
from unittest.mock import MagicMock

from research_analytics_suite.utils.SingletonChecker import is_singleton


class TestIsSingleton:

    def test_singleton_class(self):
        SingletonClass = MagicMock()
        SingletonClass._instance = SingletonClass

        assert is_singleton(SingletonClass) is True

    def test_regular_class(self):
        RegularClass = MagicMock()
        if hasattr(RegularClass, '_instance'):
            del RegularClass._instance

        assert is_singleton(RegularClass) is False

    def test_non_singleton_class_with_instance_attr(self):
        NonSingletonClass = MagicMock()
        NonSingletonClass._instance = MagicMock()  # Different instance

        assert is_singleton(NonSingletonClass) is False

    def test_class_without_instance_attr(self):
        NoInstanceAttrClass = MagicMock()
        if hasattr(NoInstanceAttrClass, '_instance'):
            del NoInstanceAttrClass._instance

        assert is_singleton(NoInstanceAttrClass) is False

    def test_class_with_instance_attr_none(self):
        NoneInstanceAttrClass = MagicMock()
        NoneInstanceAttrClass._instance = None

        assert is_singleton(NoneInstanceAttrClass) is False

    def test_class_with_instance_attr_invalid_type(self):
        InvalidInstanceAttrClass = MagicMock()
        InvalidInstanceAttrClass._instance = 12345  # Invalid type for _instance

        assert is_singleton(InvalidInstanceAttrClass) is False

    def test_class_with_instance_attr_different_instance(self):
        DifferentInstanceClass = MagicMock()
        DifferentInstanceClass._instance = MagicMock()

        assert is_singleton(DifferentInstanceClass) is False

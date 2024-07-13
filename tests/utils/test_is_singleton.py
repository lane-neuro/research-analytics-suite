import pytest
from unittest.mock import MagicMock

from research_analytics_suite.utils.SingletonChecker import is_singleton


class TestIsSingleton:

    def test_singleton_class(self):
        SingletonMeta = MagicMock()
        SingletonMeta._instances = {MagicMock(): MagicMock()}

        SingletonClass = MagicMock()
        SingletonClass.__class__ = SingletonMeta
        SingletonMeta._instances[SingletonClass] = SingletonClass

        assert is_singleton(SingletonClass) is True

    def test_regular_class(self):
        RegularMeta = MagicMock()
        RegularMeta._instances = {}

        RegularClass = MagicMock()
        RegularClass.__class__ = RegularMeta

        assert is_singleton(RegularClass) is False

    def test_non_singleton_meta_class(self):
        NonSingletonMeta = MagicMock()
        NonSingletonMeta._instances = {}

        NonSingletonClass = MagicMock()
        NonSingletonClass.__class__ = NonSingletonMeta

        assert is_singleton(NonSingletonClass) is False

    def test_meta_without_instances_attr(self):
        NoInstancesMeta = MagicMock()
        del NoInstancesMeta._instances

        NoInstancesClass = MagicMock()
        NoInstancesClass.__class__ = NoInstancesMeta

        assert is_singleton(NoInstancesClass) is False

    def test_meta_with_non_dict_instances(self):
        NonDictInstancesMeta = MagicMock()
        NonDictInstancesMeta._instances = []

        NonDictInstancesClass = MagicMock()
        NonDictInstancesClass.__class__ = NonDictInstancesMeta

        assert is_singleton(NonDictInstancesClass) is False

    # Edge case tests
    def test_meta_with_instances_none(self):
        """
        Test when the metaclass has _instances set to None.
        """
        NoneInstancesMeta = MagicMock()
        NoneInstancesMeta._instances = None

        NoneInstancesClass = MagicMock()
        NoneInstancesClass.__class__ = NoneInstancesMeta

        assert is_singleton(NoneInstancesClass) is False

    def test_meta_with_instances_non_dict(self):
        """
        Test when the metaclass has _instances set to a non-dict type.
        """
        NonDictInstancesMeta = MagicMock()
        NonDictInstancesMeta._instances = []

        NonDictInstancesClass = MagicMock()
        NonDictInstancesClass.__class__ = NonDictInstancesMeta

        assert is_singleton(NonDictInstancesClass) is False

    def test_meta_with_uninitialized_instances(self):
        """
        Test when the metaclass has _instances but it's not properly initialized.
        """
        UninitializedInstancesMeta = MagicMock()
        UninitializedInstancesMeta._instances = MagicMock()

        UninitializedInstancesClass = MagicMock()
        UninitializedInstancesClass.__class__ = UninitializedInstancesMeta

        assert is_singleton(UninitializedInstancesClass) is False

    def test_class_without_class_attr_explicit(self):
        """
        Test when the class object does not have a __class__ attribute.
        """
        NoClassAttr = MagicMock()
        del NoClassAttr.__class__

        assert is_singleton(NoClassAttr) is False

    def test_class_without_class_attr(self):
        """
        Test when the class object does not have a __class__ attribute.
        """
        NoClassAttr = MagicMock()
        del NoClassAttr.__class__

        assert is_singleton(NoClassAttr) is False

    def test_class_with_class_attr_none(self):
        """
        Test when the class object has a __class__ attribute set to None.
        """
        NoneClassAttr = MagicMock()
        NoneClassAttr.__class__ = None

        assert is_singleton(NoneClassAttr) is False

    def test_class_with_class_attr_invalid_type(self):
        """
        Test when the class object has a __class__ attribute set to an invalid type.
        """
        InvalidClassAttr = MagicMock()
        InvalidClassAttr.__class__ = 12345  # Invalid type for __class__

        assert is_singleton(InvalidClassAttr) is False
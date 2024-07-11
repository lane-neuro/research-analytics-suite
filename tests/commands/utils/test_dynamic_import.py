import typing
import pytest
import sys
import os
from collections import deque
from research_analytics_suite.commands.utils import dynamic_import

class TestDynamicImport:
    @classmethod
    def setup_class(cls):
        # Ensure the current directory is in the Python path
        sys.path.append(os.path.abspath('.'))

        # Setup code if needed, like defining some classes to import dynamically
        cls.example_class_code = """
class ExampleClass:
    pass

class CustomClass:
    pass
"""
        # Write the example class to a temporary module
        with open('example_module.py', 'w') as f:
            f.write(cls.example_class_code)

    @classmethod
    def teardown_class(cls):
        # Teardown code if needed, like cleaning up temporary files
        os.remove('example_module.py')
        sys.path.remove(os.path.abspath('.'))

    def test_import_existing_class(self):
        import_string = 'example_module.ExampleClass'
        imported_class = dynamic_import(import_string)
        assert imported_class.__name__ == 'ExampleClass'

    def test_import_non_existing_class(self):
        import_string = 'example_module.NonExistingClass'
        assert dynamic_import(import_string) is type(any)

    def test_import_invalid_string(self):
        import_string = 'invalid_module_string'
        assert dynamic_import(import_string) is type(any)

    def test_import_type_object(self):
        class DummyClass:
            pass

        assert dynamic_import(DummyClass) == DummyClass

    def test_import_forward_ref(self):
        forward_ref = typing.ForwardRef('example_module.ExampleClass')
        imported_class = dynamic_import(forward_ref)
        assert imported_class.__name__ == 'ExampleClass'

    def test_import_optional_str(self):
        import_string = 'Optional[str]'
        imported_class = dynamic_import(import_string)
        assert imported_class == typing.Optional[str]

    def test_import_list_int(self):
        import_string = 'List[int]'
        imported_class = dynamic_import(import_string)
        assert imported_class == typing.List[int]

    def test_import_dict_str_int(self):
        import_string = 'Dict[str, int]'
        imported_class = dynamic_import(import_string)
        assert imported_class == typing.Dict[str, int]

    def test_import_builtin_type(self):
        import_string = 'int'
        imported_class = dynamic_import(import_string)
        assert imported_class == int

    def test_import_nested_typing_alias(self):
        import_string = 'List[Optional[int]]'
        imported_class = dynamic_import(import_string)
        assert imported_class == typing.List[typing.Optional[int]]

    def test_import_union_typing_alias(self):
        import_string = 'Union[int, str]'
        imported_class = dynamic_import(import_string)
        assert imported_class == typing.Union[int, str]

    def test_import_tuple_typing_alias(self):
        import_string = 'Tuple[int, str]'
        imported_class = dynamic_import(import_string)
        assert imported_class == typing.Tuple[int, str]

    def test_import_custom_class(self):
        import_string = 'example_module.CustomClass'
        imported_class = dynamic_import(import_string)
        assert imported_class.__name__ == 'CustomClass'

    def test_import_builtin_collection(self):
        import_string = 'collections.deque'
        imported_class = dynamic_import(import_string)
        assert imported_class == deque

    def test_import_complex_typing_alias(self):
        import_string = 'Dict[str, List[Optional[int]]]'
        imported_class = dynamic_import(import_string)
        assert imported_class == typing.Dict[str, typing.List[typing.Optional[int]]]

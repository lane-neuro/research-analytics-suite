import pytest
from unittest import mock

from research_analytics_suite.library_manifest.utils import check_verified


class TestCheckVerified:
    @pytest.fixture(autouse=True)
    def setup_class(self):
        # This runs before each test in the class
        self.module_name_valid = 'valid_module'
        self.module_name_invalid = 'invalid_module'

    def test_check_verified_valid_module(self):
        with mock.patch('importlib.import_module') as mocked_import:
            mocked_import.return_value = True
            assert check_verified(self.module_name_valid) == True
            mocked_import.assert_called_once_with(f'operation_library.{self.module_name_valid}')

    def test_check_verified_invalid_module(self):
        with mock.patch('importlib.import_module', side_effect=ImportError):
            assert check_verified(self.module_name_invalid) == False

    def test_check_verified_import_error(self):
        with mock.patch('importlib.import_module', side_effect=ImportError):
            assert check_verified('non_existent_module') == False

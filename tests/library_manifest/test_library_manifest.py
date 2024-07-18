import pytest
import pytest_asyncio
from unittest import mock
from research_analytics_suite.library_manifest import LibraryManifest


class TestLibraryManifest:

    @pytest_asyncio.fixture(autouse=True)
    async def setup_class(self):
        self.library_manifest = LibraryManifest()

        # Mock the Config, CustomLogger, and OperationControl
        self.library_manifest._config = mock.MagicMock()
        self.library_manifest._config.BASE_DIR = 'mock_base_dir'
        self.library_manifest._config.WORKSPACE_NAME = 'mock_workspace'
        self.library_manifest._config.WORKSPACE_OPERATIONS_DIR = 'mock_operations_dir'

        self.library_manifest._logger = mock.MagicMock()
        self.library_manifest._operation_control = mock.MagicMock()
        self.library_manifest._operation_control.operation_manager.add_operation_with_parameters = mock.AsyncMock(
            return_value=mock.MagicMock(is_ready=True)
        )

        # Mock importlib.import_module to return a dummy module with a __path__ attribute
        with mock.patch('importlib.import_module', side_effect=self.mock_import_module):
            await self.library_manifest.initialize()

    def mock_import_module(self, name):
        if name == 'operation_library':
            mock_module = mock.MagicMock()
            mock_module.__path__ = ['dummy_path']
            return mock_module
        raise ModuleNotFoundError(f"No module named '{name}'")

    def test_initialize(self):
        assert self.library_manifest._initialized is True

    def test_get_library(self):
        assert isinstance(self.library_manifest.get_library(), dict)

    def test_add_category(self):
        unique_id = 9999
        self.library_manifest.add_category(unique_id, "Test Category")
        assert unique_id in self.library_manifest._categories
        assert self.library_manifest._categories[9999].name == "Test Category"

    def test_add_operation_from_attributes(self):
        from research_analytics_suite.operation_manager.operations.core.OperationAttributes import \
            OperationAttributes
        operation_attributes = mock.MagicMock(spec=OperationAttributes)
        operation_attributes.category_id = 9999
        self.library_manifest.add_category(9999, "Test Category")
        self.library_manifest.add_operation_from_attributes(operation_attributes)
        assert operation_attributes in self.library_manifest._categories[9999].operations

    @pytest.mark.asyncio
    async def test_build_base_library(self):
        await self.library_manifest.build_base_library()
        assert len(self.library_manifest.get_library()) > 0

    def test_get_categories(self):
        categories = self.library_manifest.get_categories()
        assert isinstance(dict(categories), dict)

    @pytest.mark.asyncio
    async def test_update_user_manifest(self):
        await self.library_manifest._update_user_manifest()
        assert self.library_manifest._initialized is True

    @pytest.mark.asyncio
    async def test_load_user_library(self):
        import json
        mock_operation_json = json.dumps({
            "category_id": 9999,
            "name": "Mock Operation"
        })

        with mock.patch('os.path.exists', return_value=True):
            with mock.patch('os.listdir', return_value=['mock_operation.json']):
                with mock.patch('builtins.open', mock.mock_open(read_data=mock_operation_json)):
                    from research_analytics_suite.operation_manager.operations.core.OperationAttributes import OperationAttributes
                    mock_get_attributes_from_disk = mock.AsyncMock(
                        return_value=mock.MagicMock(spec=OperationAttributes)
                    )

                    with mock.patch(
                            'research_analytics_suite.operation_manager.operations.core.memory.get_attributes_from_disk',
                            mock_get_attributes_from_disk):
                        await self.library_manifest.load_user_library()

                        # Verify that the operation was added to the library
                        assert 9999 in self.library_manifest._categories
                        assert len(self.library_manifest._categories[9999].operations) > 0

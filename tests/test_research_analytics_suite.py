import pytest
import asyncio
import os
from unittest.mock import patch, AsyncMock, MagicMock

from research_analytics_suite import ResearchAnalyticsSuite


@pytest.mark.asyncio
class TestResearchAnalyticsSuite:

    @pytest.fixture(autouse=True)
    def setup_suite(self):
        """
        Setup method to initialize the suite before each test.
        """
        self.suite = ResearchAnalyticsSuite()

    @pytest.mark.asyncio
    async def test_initialize_components(self):
        """
        Test the _initialize_components method.
        """
        with patch.object(self.suite._logger, 'initialize', new=AsyncMock()) as logger_initialize, \
             patch.object(self.suite._memory_manager, 'initialize', new=AsyncMock()) as memory_initialize, \
             patch.object(self.suite._config, 'initialize', new=AsyncMock()) as config_initialize, \
             patch.object(self.suite._operation_control, 'initialize', new=AsyncMock()) as operation_initialize, \
             patch.object(self.suite._library_manifest, 'initialize', new=AsyncMock()) as library_initialize, \
             patch.object(self.suite._workspace, 'initialize', new=AsyncMock()) as workspace_initialize:
            await self.suite._initialize_components()
            logger_initialize.assert_called_once()
            memory_initialize.assert_called_once()
            config_initialize.assert_called_once()
            operation_initialize.assert_called_once()
            library_initialize.assert_called_once()
            workspace_initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_new_workspace(self):
        """
        Test the create_new_workspace method.
        """
        self.suite._args = MagicMock()
        self.suite._args.directory = os.path.normpath('/tmp/test_workspace')
        self.suite._args.name = 'test_workspace'
        expected_workspace_path = os.path.normpath('/tmp/test_workspace/test_workspace')

        with patch('os.makedirs', new=MagicMock()) as makedirs_mock, \
             patch.object(self.suite._workspace, 'create_workspace', new=AsyncMock()) as create_workspace_mock, \
             patch.object(self.suite._logger, 'info', new=MagicMock()) as logger_info_mock, \
             patch.object(self.suite, 'ensure_unique_workspace', new=AsyncMock(return_value=expected_workspace_path)) as ensure_unique_mock:
            await self.suite.create_new_workspace()
            makedirs_mock.assert_called_once_with(os.path.normpath('/tmp/test_workspace'), exist_ok=True)
            ensure_unique_mock.assert_called_once_with(expected_workspace_path)
            logger_info_mock.assert_called_once_with(f'Creating New Workspace at: {expected_workspace_path}')
            create_workspace_mock.assert_called_once_with(os.path.normpath('/tmp/test_workspace'), 'test_workspace')

    @pytest.mark.asyncio
    async def test_ensure_unique_workspace(self):
        """
        Test the ensure_unique_workspace method.
        """
        self.suite._args = MagicMock()
        self.suite._args.directory = os.path.normpath('/tmp')
        self.suite._args.name = 'workspace'
        base_path = os.path.normpath('/tmp/workspace')
        unique_path = os.path.normpath('/tmp/workspace_1')

        with patch('os.makedirs', side_effect=[FileExistsError, None]) as makedirs_mock, \
                patch.object(self.suite._logger, 'debug', new=MagicMock()) as logger_debug_mock:
            result = await self.suite.ensure_unique_workspace(base_path)
            makedirs_mock.assert_any_call(base_path, exist_ok=False)
            makedirs_mock.assert_any_call(unique_path, exist_ok=False)
            logger_debug_mock.assert_called_with(f"Workspace {base_path} already exists. Trying a new name.")
            assert logger_debug_mock.call_count > 0
            assert result == unique_path

    @pytest.mark.asyncio
    async def test_open_existing_workspace(self):
        """
        Test the open_existing_workspace method.
        """
        self.suite._args = MagicMock()
        self.suite._args.open_workspace = 'existing_workspace'
        self.suite._args.config = None
        self.suite._args.directory = os.path.normpath('/tmp')
        expected_workspace_path = os.path.normpath('/tmp/existing_workspace')

        with patch('os.path.exists', return_value=True) as path_exists_mock, \
             patch.object(self.suite._workspace, 'load_workspace', new=AsyncMock()) as load_workspace_mock, \
             patch.object(self.suite._logger, 'info', new=MagicMock()) as logger_info_mock:
            await self.suite.open_existing_workspace()
            path_exists_mock.assert_called_once_with(expected_workspace_path)
            logger_info_mock.assert_called_once_with(f'Opening Existing Workspace at:\t{expected_workspace_path}')
            load_workspace_mock.assert_called_once_with(expected_workspace_path)

    @pytest.mark.asyncio
    async def test_launch(self):
        """
        Test the _launch method.
        """
        self.suite._args = MagicMock()
        self.suite._args.gui = 'false'

        with patch.object(self.suite, '_initialize_components', new=AsyncMock()) as init_components_mock, \
                patch.object(self.suite, '_setup_workspace', new=AsyncMock()) as setup_workspace_mock, \
                patch.object(self.suite._logger, 'info', new=MagicMock()) as logger_info_mock, \
                patch.object(self.suite._workspace, 'save_current_workspace', new=AsyncMock()) as save_workspace_mock, \
                patch('asyncio.get_event_loop', return_value=MagicMock(close=MagicMock())):
            await self.suite._launch()
            init_components_mock.assert_called_once()
            setup_workspace_mock.assert_called_once()
            save_workspace_mock.assert_called_once()
            logger_info_mock.assert_any_call('Saving Workspace...')

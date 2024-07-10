import pytest
import asyncio
import os
from unittest.mock import patch, AsyncMock, MagicMock, Mock
import sys

from research_analytics_suite import ResearchAnalyticsSuite


class TestResearchAnalyticsSuite:

    @pytest.fixture(autouse=True)
    def setup_suite(self):
        """
        Setup method to initialize the suite before each test.
        """
        self.suite = ResearchAnalyticsSuite()

    @pytest.mark.asyncio
    async def test_component_initialization(self):
        """
        Test that all components are initialized correctly.
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
    async def test_setup_workspace_new(self):
        """
        Test the _setup_workspace method for a new workspace.
        """
        self.suite._args = MagicMock()
        self.suite._args.open_workspace = os.path.normpath('/tmp/test_workspace')

        with patch('os.makedirs', new=MagicMock()) as makedirs_mock, \
                patch.object(self.suite._workspace, 'create_workspace', new=AsyncMock()) as create_workspace_mock, \
                patch.object(self.suite._logger, 'info', new=MagicMock()) as logger_info_mock:
            await self.suite._setup_workspace()
            makedirs_mock.assert_called_once_with(os.path.normpath('/tmp/test_workspace'), exist_ok=True)
            create_workspace_mock.assert_called_once_with(os.path.normpath('/tmp'), 'test_workspace')
            logger_info_mock.assert_called_once_with(f"Workspace '{os.path.normpath('/tmp/test_workspace')}' does not exist. Creating a new workspace...")

    @pytest.mark.asyncio
    async def test_setup_workspace_existing(self):
        """
        Test the _setup_workspace method for an existing workspace.
        """
        self.suite._args = MagicMock()
        self.suite._args.open_workspace = os.path.normpath('/tmp/existing_workspace')

        with patch('os.path.exists', return_value=True) as path_exists_mock, \
                patch.object(self.suite._workspace, 'load_workspace', new=AsyncMock()) as load_workspace_mock, \
                patch.object(self.suite._logger, 'info', new=MagicMock()) as logger_info_mock:
            await self.suite._setup_workspace()
            path_exists_mock.assert_called_once_with(os.path.normpath('/tmp/existing_workspace'))
            load_workspace_mock.assert_called_once_with(os.path.normpath('/tmp/existing_workspace'))
            logger_info_mock.assert_called_once_with(f"Opening existing workspace at '{os.path.normpath('/tmp/existing_workspace')}'")

    @pytest.mark.asyncio
    async def test_launch_without_gui(self):
        """
        Test the _launch method without GUI.
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

    @pytest.mark.asyncio
    async def test_launch_with_gui(self):
        """
        Test the _launch method with GUI.
        """
        self.suite._args = MagicMock()
        self.suite._args.gui = 'true'

        with patch.object(self.suite, '_initialize_components', new=AsyncMock()) as init_components_mock, \
                patch.object(self.suite, '_setup_workspace', new=AsyncMock()) as setup_workspace_mock, \
                patch.object(self.suite._logger, 'info', new=MagicMock()) as logger_info_mock, \
                patch.object(self.suite._workspace, 'save_current_workspace', new=AsyncMock()) as save_workspace_mock, \
                patch('asyncio.get_event_loop', return_value=MagicMock(close=MagicMock())), \
                patch('research_analytics_suite.gui.GuiLauncher.setup_main_window', new=AsyncMock()) as setup_main_window_mock:
            await self.suite._launch()
            init_components_mock.assert_called_once()
            setup_workspace_mock.assert_called_once()
            save_workspace_mock.assert_called_once()
            logger_info_mock.assert_any_call('Saving Workspace...')
            assert setup_main_window_mock.call_count == 1

    def test_run(self):
        """
        Test the run method.
        """
        with patch.object(self.suite, '_parse_launch_args', new=MagicMock()) as parse_args_mock, \
                patch('asyncio.run', new=MagicMock()) as asyncio_run_mock, \
                patch('nest_asyncio.apply', new=MagicMock()) as nest_asyncio_apply_mock, \
                patch('asyncio.get_event_loop',
                      return_value=MagicMock(run_forever=MagicMock(), close=MagicMock())) as event_loop_mock, \
                patch('sys.exit', new=MagicMock()) as sys_exit_mock:
            self.suite.run()
            parse_args_mock.assert_called_once()
            asyncio_run_mock.assert_called_once()
            nest_asyncio_apply_mock.assert_called_once()
            sys_exit_mock.assert_called_once()

    def test_parse_launch_args(self):
        """
        Test the _parse_launch_args method with various arguments.
        """
        test_args = [
            ['-g', 'false', '-o', 'existing_workspace'],
            ['-g', 'true', '-o', 'new_workspace'],
            ['-g', 'false'],
            ['-g', 'true'],
            ['-o', 'existing_workspace']
        ]

        expected_args = [
            {'gui': 'false', 'open_workspace': 'existing_workspace'},
            {'gui': 'true', 'open_workspace': 'new_workspace'},
            {'gui': 'false', 'open_workspace': os.path.expanduser('~/Research-Analytics-Suite/workspaces/default_workspace')},
            {'gui': 'true', 'open_workspace': os.path.expanduser('~/Research-Analytics-Suite/workspaces/default_workspace')},
            {'gui': 'true', 'open_workspace': 'existing_workspace'}
        ]

        for i, args in enumerate(test_args):
            with patch.object(sys, 'argv', ['test'] + args):
                self.suite._parse_launch_args()
                assert vars(self.suite._args) == expected_args[i]

    @pytest.mark.asyncio
    async def test_invalid_workspace_path(self):
        """
        Test handling of invalid workspace path.
        """
        self.suite._args = MagicMock()
        self.suite._args.open_workspace = 'invalid_workspace_path'

        with patch('os.path.exists', return_value=False) as path_exists_mock, \
                patch.object(self.suite._logger, 'info', new=MagicMock()) as logger_info_mock, \
                patch.object(self.suite._logger, 'debug', new=MagicMock()) as logger_debug_mock, \
                patch.object(self.suite._workspace, 'create_workspace', new=AsyncMock()) as create_workspace_mock:
            await self.suite._setup_workspace()
            logger_info_mock.assert_called_once_with(
                f"Workspace '{os.path.normpath('invalid_workspace_path')}' does not exist. Creating a new workspace...")

    def test_run_keyboard_interrupt(self):
        """
        Test the run method handling KeyboardInterrupt.
        """
        with patch.object(self.suite, '_parse_launch_args', new=MagicMock()), \
             patch('asyncio.run', side_effect=KeyboardInterrupt), \
             patch('nest_asyncio.apply', new=MagicMock()), \
             patch('asyncio.get_event_loop', return_value=MagicMock(run_forever=MagicMock(), close=MagicMock())):
            with patch('builtins.print') as mocked_print:
                with pytest.raises(SystemExit):
                    self.suite.run()
                mocked_print.assert_any_call('Exiting Research Analytics Suite..')

    def test_run_general_exception(self):
        """
        Test the run method handling general Exception.
        """
        with patch.object(self.suite, '_parse_launch_args', new=MagicMock()), \
             patch('asyncio.run', side_effect=Exception('Test Exception')), \
             patch('nest_asyncio.apply', new=MagicMock()), \
             patch('asyncio.get_event_loop', return_value=MagicMock(run_forever=MagicMock(), close=MagicMock())):
            with patch('research_analytics_suite.utils.CustomLogger', new=MagicMock(error=MagicMock())) as logger_mock,\
                    pytest.raises(SystemExit):
                self.suite.run()
                logger_mock.error.assert_called_once()

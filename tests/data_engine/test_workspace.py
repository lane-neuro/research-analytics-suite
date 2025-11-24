"""
Comprehensive test suite for Workspace.py

Tests cover:
- Workspace initialization and singleton behavior
- Universal Data Engine operations (load, save, transform, analyze)
- Workspace creation, loading, and switching
- Performance monitoring and optimization
- Streaming data processing
- Health checks and error handling
"""
import pytest
import asyncio
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, Mock, call
import pandas as pd

from research_analytics_suite.data_engine.Workspace import Workspace
from research_analytics_suite.data_engine.UniversalDataEngine import UniversalDataEngine
from research_analytics_suite.data_engine.core.DataContext import DataContext
from research_analytics_suite.data_engine.core.DataProfile import DataProfile


class TestWorkspace:
    """Test suite for Workspace class"""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup test environment with mocked dependencies"""
        # Reset singleton
        Workspace._instance = None

        # Create temporary directory for test workspaces
        self.test_dir = Path(tempfile.mkdtemp())

        with patch('research_analytics_suite.utils.CustomLogger') as MockLogger, \
             patch('research_analytics_suite.utils.Config') as MockConfig, \
             patch('research_analytics_suite.library_manifest.LibraryManifest') as MockManifest, \
             patch('research_analytics_suite.data_engine.memory.MemoryManager') as MockMemoryManager:

            # Setup mock logger
            self.mock_logger = MagicMock()
            self.mock_logger.error = MagicMock()
            self.mock_logger.debug = MagicMock()
            self.mock_logger.info = MagicMock()
            self.mock_logger.warning = MagicMock()
            self.mock_logger.initialize = AsyncMock()
            self.mock_logger.reconfigure_for_workspace = MagicMock()
            self.mock_logger.clear_file_handlers = MagicMock()
            MockLogger.return_value = self.mock_logger

            # Setup mock config
            self.mock_config = MagicMock()
            self.mock_config.WORKSPACE_NAME = "TestWorkspace"
            self.mock_config.BASE_DIR = str(self.test_dir)
            self.mock_config.DATA_DIR = "data"
            self.mock_config.LOG_DIR = "logs"
            self.mock_config.WORKSPACE_DIR = "workspace"
            self.mock_config.WORKSPACE_OPERATIONS_DIR = "workspace/operations"
            self.mock_config.BACKUP_DIR = "backup"
            self.mock_config.EXPORT_DIR = "export"
            self.mock_config.ENGINE_DIR = "engine"
            self.mock_config.copy_with = MagicMock(return_value={
                "BASE_DIR": str(self.test_dir),
                "WORKSPACE_NAME": "TestWorkspace",
                "DATA_DIR": "data",
                "LOG_DIR": "logs",
                "WORKSPACE_DIR": "workspace",
                "BACKUP_DIR": "backup",
                "EXPORT_DIR": "export",
                "ENGINE_DIR": "engine"
            })
            self.mock_config.save_to_file = AsyncMock()
            self.mock_config.reload_from_file = AsyncMock(return_value=self.mock_config)
            MockConfig.return_value = self.mock_config
            MockConfig.save_dict_to_file = AsyncMock()

            # Setup mock library manifest
            self.mock_manifest = MagicMock()
            self.mock_manifest.load_user_library = AsyncMock()
            self.mock_manifest.reset_for_workspace = AsyncMock()
            MockManifest.return_value = self.mock_manifest

            # Setup mock memory manager
            self.mock_memory_manager = MagicMock()
            self.mock_memory_manager.initialize = AsyncMock()
            self.mock_memory_manager.reset = AsyncMock()
            self.mock_memory_manager.set_config = MagicMock()
            self.mock_memory_manager.rebind_to_db = AsyncMock()
            MockMemoryManager.return_value = self.mock_memory_manager

            # Create workspace instance
            self.workspace = Workspace()
            self.workspace._logger = self.mock_logger
            self.workspace._config = self.mock_config
            self.workspace._memory_manager = self.mock_memory_manager
            self.workspace._library_manifest = self.mock_manifest

        yield

        # Cleanup
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        Workspace._instance = None

    # ========================
    # Initialization Tests
    # ========================

    def test_singleton_pattern(self):
        """Test that Workspace follows singleton pattern"""
        workspace1 = Workspace()
        workspace2 = Workspace()
        assert workspace1 is workspace2

    @pytest.mark.asyncio
    async def test_initialize_workspace(self):
        """Test workspace initialization"""
        await self.workspace.initialize()

        assert self.workspace._initialized is True
        assert self.workspace._universal_engine is not None
        assert isinstance(self.workspace._universal_engine, UniversalDataEngine)
        assert self.workspace._workspace_profile is not None
        assert self.workspace._optimization_settings is not None

    @pytest.mark.asyncio
    async def test_initialize_with_custom_config(self):
        """Test workspace initialization with custom config"""
        custom_config = MagicMock()
        custom_config.WORKSPACE_NAME = "CustomWorkspace"

        await self.workspace.initialize(config=custom_config)

        assert self.workspace._config == custom_config
        assert self.workspace._initialized is True

    @pytest.mark.asyncio
    async def test_initialize_twice_no_duplicate(self):
        """Test that initializing twice doesn't duplicate initialization"""
        await self.workspace.initialize()
        first_engine = self.workspace._universal_engine

        await self.workspace.initialize()
        second_engine = self.workspace._universal_engine

        assert first_engine is second_engine

    @pytest.mark.asyncio
    async def test_get_engine_property(self):
        """Test engine property getter"""
        await self.workspace.initialize()
        engine = self.workspace.engine

        assert isinstance(engine, UniversalDataEngine)
        assert engine == self.workspace._universal_engine

    @pytest.mark.asyncio
    async def test_get_engine_command(self):
        """Test get_engine command method"""
        await self.workspace.initialize()
        engine = self.workspace.get_engine()

        assert isinstance(engine, UniversalDataEngine)
        assert engine == self.workspace._universal_engine

    # ========================
    # Data Operations Tests
    # ========================

    @pytest.mark.asyncio
    async def test_load_data_success(self):
        """Test successful data loading"""
        await self.workspace.initialize()

        # Mock DataContext and DataProfile
        mock_profile = MagicMock(spec=DataProfile)
        mock_profile.data_type = "csv"
        mock_profile.size_mb = 10.5

        mock_context = MagicMock(spec=DataContext)
        mock_context.profile = mock_profile

        self.workspace._universal_engine.load_data = AsyncMock(return_value=mock_context)

        result = await self.workspace.load_data("test.csv")

        assert result == mock_context
        assert "csv" in self.workspace._workspace_profile['data_types_processed']

    @pytest.mark.asyncio
    async def test_load_data_not_initialized(self):
        """Test loading data when workspace not initialized"""
        with pytest.raises(RuntimeError, match="Workspace not initialized"):
            await self.workspace.load_data("test.csv")

    @pytest.mark.asyncio
    async def test_load_data_with_type_hint(self):
        """Test loading data with data type hint"""
        await self.workspace.initialize()

        mock_profile = MagicMock(spec=DataProfile)
        mock_profile.data_type = "json"
        mock_profile.size_mb = 5.0

        mock_context = MagicMock(spec=DataContext)
        mock_context.profile = mock_profile

        self.workspace._universal_engine.load_data = AsyncMock(return_value=mock_context)

        result = await self.workspace.load_data("test.json", data_type="json")

        self.workspace._universal_engine.load_data.assert_called_once_with(
            "test.json", "json"
        )

    @pytest.mark.asyncio
    async def test_save_data_success(self):
        """Test successful data saving"""
        await self.workspace.initialize()

        self.workspace._universal_engine.save_data = AsyncMock(return_value=True)

        result = await self.workspace.save_data(
            data={"test": "data"},
            destination="output.json"
        )

        assert result is True
        self.workspace._universal_engine.save_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_data_not_initialized(self):
        """Test saving data when workspace not initialized"""
        with pytest.raises(RuntimeError, match="Workspace not initialized"):
            await self.workspace.save_data({"test": "data"}, "output.json")

    @pytest.mark.asyncio
    async def test_save_data_with_profile(self):
        """Test saving data with custom profile"""
        await self.workspace.initialize()

        mock_profile = MagicMock(spec=DataProfile)
        self.workspace._universal_engine.save_data = AsyncMock(return_value=True)

        result = await self.workspace.save_data(
            data={"test": "data"},
            destination="output.json",
            data_profile=mock_profile
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_transform_data_success(self):
        """Test data transformation"""
        await self.workspace.initialize()

        transformed_data = {"transformed": True}
        self.workspace._universal_engine.transform_data = AsyncMock(
            return_value=transformed_data
        )

        result = await self.workspace.transform_data(
            data={"original": True},
            operation="normalize"
        )

        assert result == transformed_data

    @pytest.mark.asyncio
    async def test_transform_data_not_initialized(self):
        """Test transforming data when workspace not initialized"""
        with pytest.raises(RuntimeError, match="Workspace not initialized"):
            await self.workspace.transform_data({"data": "value"}, "operation")

    @pytest.mark.asyncio
    async def test_analyze_workspace_data(self):
        """Test workspace data analysis"""
        await self.workspace.initialize()

        mock_analysis = {
            'profile': {
                'size_mb': 500,
                'data_type': 'csv',
                'fits_in_memory': True
            }
        }

        self.workspace._universal_engine.analyze_data = AsyncMock(
            return_value=mock_analysis
        )

        result = await self.workspace.analyze_workspace_data("test.csv")

        assert 'workspace_context' in result
        assert 'workspace_name' in result['workspace_context']
        assert 'performance_recommendations' in result['workspace_context']

    @pytest.mark.asyncio
    async def test_analyze_workspace_data_not_initialized(self):
        """Test analyzing data when workspace not initialized"""
        with pytest.raises(RuntimeError, match="Workspace not initialized"):
            await self.workspace.analyze_workspace_data("test.csv")

    # ========================
    # Optimization Tests
    # ========================

    @pytest.mark.asyncio
    async def test_auto_optimize_workspace(self):
        """Test automatic workspace optimization"""
        await self.workspace.initialize()

        mock_stats = {
            'operations_count': 100,
            'avg_duration': 2.5
        }

        self.workspace._universal_engine.get_performance_stats = MagicMock(
            return_value=mock_stats
        )

        result = await self.workspace.auto_optimize_workspace()

        assert 'current_performance' in result
        assert 'workspace_patterns' in result
        assert 'optimization_opportunities' in result
        assert 'recommended_settings' in result

    @pytest.mark.asyncio
    async def test_auto_optimize_with_large_datasets(self):
        """Test optimization recommendations for large datasets"""
        await self.workspace.initialize()

        # Set up workspace to appear to be processing large datasets
        self.workspace._workspace_profile['data_types_processed'] = {
            'csv', 'parquet', 'json', 'hdf5'
        }

        self.workspace._universal_engine.get_performance_stats = MagicMock(
            return_value={'operations_count': 50}
        )

        result = await self.workspace.auto_optimize_workspace()

        assert 'optimization_opportunities' in result

    @pytest.mark.asyncio
    async def test_get_workspace_performance_stats(self):
        """Test retrieving workspace performance statistics"""
        await self.workspace.initialize()

        mock_engine_stats = {'operations': 10, 'avg_time': 1.5}
        self.workspace._universal_engine.get_performance_stats = MagicMock(
            return_value=mock_engine_stats
        )

        stats = self.workspace.get_workspace_performance_stats()

        assert 'workspace_info' in stats
        assert 'engine' in stats
        assert stats['engine']['universal_engine'] == mock_engine_stats
        # runtime_id and name should be accessible on the engine
        assert stats['engine']['engine_id'] is not None
        assert stats['engine']['engine_name'] is not None

    @pytest.mark.asyncio
    async def test_get_performance_recommendations_large_dataset(self):
        """Test performance recommendations for large datasets"""
        analysis = {
            'profile': {
                'size_mb': 2000,
                'data_type': 'csv',
                'fits_in_memory': False
            }
        }

        recommendations = self.workspace._get_performance_recommendations(analysis)

        assert len(recommendations) > 0
        assert any('distributed' in r.lower() for r in recommendations)
        assert any('streaming' in r.lower() for r in recommendations)

    @pytest.mark.asyncio
    async def test_get_performance_recommendations_time_series(self):
        """Test performance recommendations for time series data"""
        analysis = {
            'profile': {
                'size_mb': 100,
                'data_type': 'time_series',
                'fits_in_memory': True
            }
        }

        recommendations = self.workspace._get_performance_recommendations(analysis)

        assert any('time-series' in r.lower() for r in recommendations)

    def test_analyze_workspace_patterns(self):
        """Test workspace pattern analysis"""
        self.workspace._workspace_profile = {
            'data_types_processed': {'time_series', 'csv', 'json', 'parquet'}
        }

        patterns = self.workspace._analyze_workspace_patterns()

        assert 'data_types_used' in patterns
        assert 'streaming_data_detected' in patterns
        assert patterns['streaming_data_detected'] is True
        assert 'Multi-format optimization' in patterns['optimization_opportunities']

    # ========================
    # Streaming Tests
    # ========================

    @pytest.mark.asyncio
    async def test_stream_process_workspace_data(self):
        """Test streaming data processing"""
        await self.workspace.initialize()

        # Mock async generator
        async def mock_stream_process(*args, **kwargs):
            for i in range(3):
                yield f"chunk_{i}"

        self.workspace._universal_engine.stream_process = mock_stream_process

        results = await self.workspace.stream_process_workspace_data(
            source="large_file.csv",
            operation="normalize",
            chunk_size=1000
        )

        assert len(results) == 3
        assert results[0] == "chunk_0"
        assert results[2] == "chunk_2"

    @pytest.mark.asyncio
    async def test_stream_process_not_initialized(self):
        """Test streaming when workspace not initialized"""
        with pytest.raises(RuntimeError, match="Workspace not initialized"):
            await self.workspace.stream_process_workspace_data(
                "test.csv", "operation"
            )

    # ========================
    # Workspace Management Tests
    # ========================

    @pytest.mark.asyncio
    async def test_create_workspace_success(self):
        """Test successful workspace creation"""
        workspace_dir = self.test_dir / "workspaces" / "NewWorkspace"

        with patch.object(self.workspace, 'switch_to_workspace', new_callable=AsyncMock) as mock_switch:
            mock_switch.return_value = self.workspace

            result = await self.workspace.create_workspace(
                workspace_directory=str(workspace_dir / "NewWorkspace"),  # Pass child dir path
                workspace_name="NewWorkspace"
            )

            assert result == self.workspace
            # Check that switch_to_workspace was called
            mock_switch.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_workspace_already_exists_no_overwrite(self):
        """Test creating workspace that already exists without overwrite"""
        # Mock copy_with to return a dict with the correct BASE_DIR
        test_workspace_name = "ExistingWorkspace"
        workspace_path = self.test_dir / "workspaces" / test_workspace_name
        workspace_path.mkdir(parents=True, exist_ok=True)

        # Override the mock to return the expected base_dir
        def mock_copy_with(**kwargs):
            return {
                "BASE_DIR": str(self.test_dir),
                "WORKSPACE_NAME": kwargs.get("WORKSPACE_NAME", test_workspace_name),
                "DATA_DIR": "data",
                "LOG_DIR": "logs",
                "WORKSPACE_DIR": "workspace",
                "BACKUP_DIR": "backup",
                "EXPORT_DIR": "export",
                "ENGINE_DIR": "engine"
            }

        self.mock_config.copy_with = MagicMock(side_effect=mock_copy_with)

        with pytest.raises(FileExistsError):
            await self.workspace.create_workspace(
                workspace_directory=str(self.test_dir / "dummy"),
                workspace_name=test_workspace_name,
                overwrite=False
            )

    @pytest.mark.asyncio
    async def test_create_workspace_with_overwrite(self):
        """Test creating workspace with overwrite flag"""
        workspace_dir = self.test_dir / "workspaces" / "OverwriteWorkspace"
        workspace_dir.mkdir(parents=True, exist_ok=True)

        with patch.object(self.workspace, 'switch_to_workspace', new_callable=AsyncMock) as mock_switch:
            mock_switch.return_value = self.workspace

            result = await self.workspace.create_workspace(
                workspace_directory=str(workspace_dir),
                workspace_name="OverwriteWorkspace",
                overwrite=True
            )

            assert result == self.workspace

    @pytest.mark.asyncio
    async def test_save_current_workspace(self):
        """Test saving current workspace"""
        await self.workspace.initialize()

        workspace_root = self.test_dir / "workspaces" / "TestWorkspace"
        workspace_root.mkdir(parents=True, exist_ok=True)

        result = await self.workspace.save_current_workspace()

        assert result == str(workspace_root)
        self.mock_config.save_to_file.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_current_workspace_with_engine_config(self):
        """Test saving workspace with engine configuration"""
        await self.workspace.initialize()

        workspace_root = self.test_dir / "workspaces" / "TestWorkspace"
        (workspace_root / "data").mkdir(parents=True, exist_ok=True)

        result = await self.workspace.save_current_workspace()

        engine_config_path = workspace_root / "data" / "universal_engine.json"
        assert engine_config_path.exists()

    @pytest.mark.asyncio
    async def test_load_workspace_success(self):
        """Test successful workspace loading"""
        # Create workspace structure
        workspace_root = self.test_dir / "workspaces" / "LoadTest"
        workspace_root.mkdir(parents=True, exist_ok=True)
        (workspace_root / "data").mkdir(exist_ok=True)

        # Create config file
        config_data = {
            "BASE_DIR": str(self.test_dir),
            "WORKSPACE_NAME": "LoadTest",
            "DATA_DIR": "data",
            "LOG_DIR": "logs"
        }
        with open(workspace_root / "config.json", 'w') as f:
            json.dump(config_data, f)

        # Mock singleton reset methods
        with patch('research_analytics_suite.gui.NodeEditorManager.NodeEditorManager') as MockNode, \
             patch('research_analytics_suite.operation_manager.control.OperationControl.OperationControl') as MockOp, \
             patch('research_analytics_suite.commands.registry.CommandRegistry.CommandRegistry') as MockCmd:

            mock_node = MagicMock()
            mock_node.reset_for_workspace = AsyncMock()
            MockNode.return_value = mock_node

            mock_op = MagicMock()
            mock_op.reset_for_workspace = AsyncMock()
            MockOp.return_value = mock_op

            mock_cmd = MagicMock()
            mock_cmd.reset_for_workspace = AsyncMock()
            MockCmd.return_value = mock_cmd

            result = await self.workspace.load_workspace(str(workspace_root))

            assert result == self.workspace
            assert self.workspace._active_workspace_path == workspace_root

    @pytest.mark.asyncio
    async def test_load_workspace_not_found(self):
        """Test loading non-existent workspace"""
        result = await self.workspace.load_workspace("/nonexistent/path")
        assert result is None

    @pytest.mark.asyncio
    async def test_load_workspace_missing_config(self):
        """Test loading workspace without config.json"""
        workspace_root = self.test_dir / "workspaces" / "NoConfig"
        workspace_root.mkdir(parents=True, exist_ok=True)

        result = await self.workspace.load_workspace(str(workspace_root))
        assert result is None

    @pytest.mark.asyncio
    async def test_load_workspace_with_engine_config(self):
        """Test loading workspace with existing engine configuration"""
        workspace_root = self.test_dir / "workspaces" / "EngineConfig"
        (workspace_root / "data").mkdir(parents=True, exist_ok=True)

        # Create config
        config_data = {
            "BASE_DIR": str(self.test_dir),
            "WORKSPACE_NAME": "EngineConfig",
            "DATA_DIR": "data"
        }
        with open(workspace_root / "config.json", 'w') as f:
            json.dump(config_data, f)

        # Create engine config
        engine_config = {
            'engine_type': 'Universal',
            'engine_id': 'test-engine-id',
            'name': 'TestEngine',
            'workspace_profile': {
                'data_types_processed': ['csv', 'json']
            }
        }
        with open(workspace_root / "data" / "universal_engine.json", 'w') as f:
            json.dump(engine_config, f)

        with patch('research_analytics_suite.gui.NodeEditorManager.NodeEditorManager') as MockNode, \
             patch('research_analytics_suite.operation_manager.control.OperationControl.OperationControl') as MockOp, \
             patch('research_analytics_suite.commands.registry.CommandRegistry.CommandRegistry') as MockCmd:

            for MockClass in [MockNode, MockOp, MockCmd]:
                mock_instance = MagicMock()
                mock_instance.reset_for_workspace = AsyncMock()
                MockClass.return_value = mock_instance

            result = await self.workspace.load_workspace(str(workspace_root))

            assert result == self.workspace
            assert isinstance(self.workspace._workspace_profile['data_types_processed'], set)

    @pytest.mark.asyncio
    async def test_switch_to_workspace(self):
        """Test switching between workspaces"""
        workspace_root = self.test_dir / "workspaces" / "SwitchTest"
        workspace_root.mkdir(parents=True, exist_ok=True)

        with patch.object(self.workspace, 'close', new_callable=AsyncMock) as mock_close, \
             patch.object(self.workspace, 'load_workspace', new_callable=AsyncMock) as mock_load:

            mock_load.return_value = self.workspace

            result = await self.workspace.switch_to_workspace(str(workspace_root))

            mock_close.assert_called_once()
            mock_load.assert_called_once_with(str(workspace_root))

    def test_reset_workspace(self):
        """Test workspace reset"""
        self.workspace._initialized = True
        self.workspace._reset_workspace()

        assert self.workspace._initialized is False

    @pytest.mark.asyncio
    async def test_reset_all_singletons(self):
        """Test resetting all singleton instances"""
        with patch('research_analytics_suite.gui.NodeEditorManager.NodeEditorManager') as MockNode, \
             patch('research_analytics_suite.operation_manager.control.OperationControl.OperationControl') as MockOp, \
             patch('research_analytics_suite.commands.registry.CommandRegistry.CommandRegistry') as MockCmd:

            for MockClass in [MockNode, MockOp, MockCmd]:
                mock_instance = MagicMock()
                mock_instance.reset_for_workspace = AsyncMock()
                MockClass.return_value = mock_instance

            await self.workspace._reset_all_singletons()

            self.mock_memory_manager.reset.assert_called_once()
            self.mock_memory_manager.initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_workspace(self):
        """Test closing workspace"""
        await self.workspace.initialize()
        self.workspace._active_workspace_path = Path("/test/path")
        self.workspace._universal_engine.cleanup = AsyncMock()

        await self.workspace.close()

        assert self.workspace._active_workspace_path is None
        assert self.workspace._initialized is False
        self.mock_logger.clear_file_handlers.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_workspace_cleanup_failure(self):
        """Test closing workspace when cleanup fails"""
        await self.workspace.initialize()
        self.workspace._active_workspace_path = Path("/test/path")
        self.workspace._universal_engine.cleanup = AsyncMock(
            side_effect=Exception("Cleanup failed")
        )

        await self.workspace.close()

        # Should still mark as closed despite cleanup failure
        assert self.workspace._active_workspace_path is None
        assert self.workspace._initialized is False

    # ========================
    # Convenience Methods Tests
    # ========================

    @pytest.mark.asyncio
    async def test_quick_load(self):
        """Test quick load convenience method"""
        await self.workspace.initialize()

        test_data = {"column1": [1, 2, 3], "column2": ["a", "b", "c"]}

        mock_profile = MagicMock(spec=DataProfile)
        mock_profile.data_type = "csv"
        mock_profile.size_mb = 5.0

        mock_context = MagicMock(spec=DataContext)
        mock_context.profile = mock_profile
        mock_context.data = test_data

        async def mock_load_data(*args, **kwargs):
            return mock_context

        with patch.object(self.workspace, 'load_data', side_effect=mock_load_data):
            result = await self.workspace.quick_load("test.csv")

            assert result == test_data
            assert result is mock_context.data

    @pytest.mark.asyncio
    async def test_quick_save(self):
        """Test quick save convenience method"""
        await self.workspace.initialize()

        with patch.object(self.workspace, 'save_data', new_callable=AsyncMock) as mock_save:
            mock_save.return_value = True

            result = await self.workspace.quick_save({"data": "value"}, "output.json")

            assert result is True
            mock_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_workspace_health_check_healthy(self):
        """Test workspace health check when healthy"""
        await self.workspace.initialize()
        self.workspace._active_workspace_path = Path("/test/path")
        self.workspace._universal_engine.health_check = AsyncMock(
            return_value={'status': 'healthy'}
        )

        health = await self.workspace.workspace_health_check()

        assert health['workspace_status'] == 'healthy'
        assert health['initialized'] is True
        assert len(health['issues']) == 0

    @pytest.mark.asyncio
    async def test_workspace_health_check_degraded(self):
        """Test workspace health check when degraded"""
        # Don't initialize - engine will be None
        health = await self.workspace.workspace_health_check()

        assert health['workspace_status'] == 'degraded'
        assert 'Universal Data Engine not initialized' in health['issues']

    @pytest.mark.asyncio
    async def test_workspace_health_check_unhealthy(self):
        """Test workspace health check when unhealthy"""
        await self.workspace.initialize()
        self.workspace._universal_engine.health_check = AsyncMock(
            side_effect=Exception("Health check failed")
        )

        health = await self.workspace.workspace_health_check()

        assert health['workspace_status'] == 'unhealthy'
        assert len(health['issues']) > 0

    # ========================
    # String Representation Tests
    # ========================

    @pytest.mark.asyncio
    async def test_str_representation(self):
        """Test string representation"""
        await self.workspace.initialize()

        str_repr = str(self.workspace)

        assert "Workspace" in str_repr
        assert "TestWorkspace" in str_repr
        assert "Ready" in str_repr

    @pytest.mark.asyncio
    async def test_str_representation_not_initialized(self):
        """Test string representation when not initialized"""
        str_repr = str(self.workspace)

        assert "Workspace" in str_repr
        assert "Not initialized" in str_repr

    @pytest.mark.asyncio
    async def test_repr_representation(self):
        """Test repr representation"""
        await self.workspace.initialize()

        repr_str = repr(self.workspace)

        assert "Workspace" in repr_str
        assert "TestWorkspace" in repr_str
        assert "universal_engine=True" in repr_str
        assert "initialized=True" in repr_str

    # ========================
    # Edge Cases and Error Handling
    # ========================

    @pytest.mark.asyncio
    async def test_load_data_workspace_profile_none(self):
        """Test loading data when workspace profile is None"""
        await self.workspace.initialize()
        self.workspace._workspace_profile = None

        mock_profile = MagicMock(spec=DataProfile)
        mock_profile.data_type = "csv"
        mock_profile.size_mb = 10.5

        mock_context = MagicMock(spec=DataContext)
        mock_context.profile = mock_profile

        self.workspace._universal_engine.load_data = AsyncMock(return_value=mock_context)

        # Should not raise exception
        result = await self.workspace.load_data("test.csv")
        assert result == mock_context

    @pytest.mark.asyncio
    async def test_create_workspace_engine_config_failure(self):
        """Test workspace creation when engine config save fails"""
        workspace_dir = self.test_dir / "workspaces" / "ConfigFailWorkspace"

        with patch.object(self.workspace, 'switch_to_workspace', new_callable=AsyncMock) as mock_switch, \
             patch('builtins.open', side_effect=Exception("Write failed")):
            mock_switch.return_value = self.workspace

            # Should log warning but still complete
            result = await self.workspace.create_workspace(
                workspace_directory=str(workspace_dir),
                workspace_name="ConfigFailWorkspace"
            )

            self.mock_logger.warning.assert_called()

    @pytest.mark.asyncio
    async def test_save_current_workspace_failure(self):
        """Test save current workspace when it fails"""
        self.mock_config.BASE_DIR = None  # Cause AttributeError

        result = await self.workspace.save_current_workspace()

        assert result == ""
        self.mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_reset_all_singletons_with_error(self):
        """Test singleton reset when error occurs"""
        self.workspace._logger = None  # Remove logger to trigger exception path

        with patch('research_analytics_suite.gui.NodeEditorManager.NodeEditorManager',
                   side_effect=Exception("Reset failed")):
            # Should not raise exception, just log/print warning
            await self.workspace._reset_all_singletons()

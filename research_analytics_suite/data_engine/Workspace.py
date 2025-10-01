"""
Workspace Module

Workspace management using the Universal Data Engine.
The workspace now provides unified data operations, automatic optimization,
and infinite scalability through a single, intelligent engine.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Production
"""
from __future__ import annotations
import asyncio
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List, Union

from research_analytics_suite.commands import link_class_commands, command
from research_analytics_suite.utils.Config import Config
from research_analytics_suite.utils.CustomLogger import CustomLogger
from research_analytics_suite.data_engine.memory import MemoryManager

# Universal Data Engine
from research_analytics_suite.data_engine.UniversalDataEngine import UniversalDataEngine
from research_analytics_suite.data_engine.core.DataProfile import DataProfile
from research_analytics_suite.data_engine.core.DataContext import DataContext


@link_class_commands
class Workspace:
    """
    Workspace management using the Universal Data Engine.

    The Workspace provides:
    - Universal data processing for ANY data type of ANY size
    - Automatic optimization and intelligent backend selection
    - Seamless scaling from local to distributed processing
    - Unified storage abstraction across any backend
    - Zero-configuration optimal performance

    Key Features:
    - Single Universal Data Engine handles everything
    - Intelligent data profiling and optimization
    - Automatic resource management
    - Infinite scalability with streaming support
    - Built-in performance monitoring and optimization
    """
    _instance: Workspace = None
    _lock: asyncio.Lock = asyncio.Lock()
    _active_workspace_path: Optional[Path] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initializes the Workspace with Universal Data Engine.
        """
        if not hasattr(self, '_initialized'):
            self._logger = CustomLogger()
            self._config = Config()
            from research_analytics_suite.library_manifest.LibraryManifest import LibraryManifest
            self._library_manifest = LibraryManifest()
            self._memory_manager = MemoryManager()

            # Universal Data Engine instance
            self._universal_engine: Optional[UniversalDataEngine] = None

            # Workspace intelligence
            self._workspace_profile: Optional[Dict[str, Any]] = None
            self._optimization_settings: Dict[str, Any] = {}
            self._performance_metrics: Dict[str, Any] = {}

            self._initialized = False

    async def initialize(self, config: Config = None) -> None:
        """
        Initializes the workspace with Universal Data Engine.

        Args:
            config (Config): The configuration to use for the workspace
        """
        if not self._initialized:
            async with Workspace._lock:
                if not self._initialized:
                    if config:
                        self._config = config

                    # Initialize the One True Engine
                    self._universal_engine = UniversalDataEngine(
                        name=f"Workspace_Engine_{self._config.WORKSPACE_NAME or 'Default'}"
                    )

                    # Initialize workspace intelligence
                    self._workspace_profile = {
                        'created_at': asyncio.get_event_loop().time(),
                        'engine_type': 'Universal',
                        'optimization_level': 'automatic',
                        'data_types_processed': set(),
                        'performance_history': []
                    }

                    # Intelligent optimization settings
                    self._optimization_settings = {
                        'auto_optimize': True,
                        'prefer_speed': True,
                        'enable_caching': True,
                        'streaming_threshold_mb': 100,
                        'distributed_threshold_gb': 10
                    }

                    self._logger.debug("Workspace initialized with Universal Data Engine")
                    self._initialized = True

    @property
    def engine(self) -> UniversalDataEngine:
        """
        Get the Universal Data Engine.

        Returns:
            UniversalDataEngine: The workspace's data engine
        """
        return self._universal_engine

    @command
    def get_engine(self) -> UniversalDataEngine:
        """
        Retrieves the Universal Data Engine.

        Returns:
            UniversalDataEngine: The workspace's data engine
        """
        return self._universal_engine

    # ===============================
    # Universal Data Engine Operations
    # ===============================

    @command
    async def load_data(self, source: Union[str, Path, Any],
                       data_type: Optional[str] = None,
                       **kwargs) -> DataContext:
        """
        Load data using the Universal Data Engine with automatic optimization.

        Args:
            source: Data source (path, URL, or data object)
            data_type: Optional data type hint
            **kwargs: Additional loading parameters

        Returns:
            DataContext containing loaded data with profile and schema
        """
        if not self._universal_engine:
            raise RuntimeError("Workspace not initialized. Call initialize() first.")

        context = await self._universal_engine.load_data(source, data_type, **kwargs)

        # Update workspace profile
        if self._workspace_profile:
            # Ensure data_types_processed is a set
            if not isinstance(self._workspace_profile.get('data_types_processed'), set):
                self._workspace_profile['data_types_processed'] = set()
            self._workspace_profile['data_types_processed'].add(context.profile.data_type)

        self._logger.info(f"Loaded {context.profile.data_type} data ({context.profile.size_mb:.2f} MB) with auto-optimization")
        return context

    @command
    async def save_data(self, data: Any, destination: Union[str, Path],
                       data_profile: Optional[DataProfile] = None,
                       **kwargs) -> bool:
        """
        Save data using the Universal Data Engine with automatic format optimization.

        Args:
            data: Data to save
            destination: Where to save the data
            data_profile: Optional data profile
            **kwargs: Additional saving parameters

        Returns:
            True if successful
        """
        if not self._universal_engine:
            raise RuntimeError("Workspace not initialized. Call initialize() first.")

        success = await self._universal_engine.save_data(data, destination, data_profile, **kwargs)
        if success:
            self._logger.info(f"Saved data to {destination} with auto-optimization")
        return success

    @command
    async def transform_data(self, data: Any, operation: str,
                           data_profile: Optional[DataProfile] = None,
                           **kwargs) -> Any:
        """
        Transform data using optimal backend selection.

        Args:
            data: Data to transform
            operation: Transformation operation
            data_profile: Optional data profile
            **kwargs: Operation parameters

        Returns:
            Transformed data
        """
        if not self._universal_engine:
            raise RuntimeError("Workspace not initialized. Call initialize() first.")

        result = await self._universal_engine.transform_data(data, operation, data_profile, **kwargs)
        self._logger.debug(f"Transformed data using operation: {operation}")
        return result

    @command
    async def analyze_workspace_data(self, source: Union[str, Path, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of data in the workspace.

        Args:
            source: Data source to analyze

        Returns:
            Comprehensive analysis results
        """
        if not self._universal_engine:
            raise RuntimeError("Workspace not initialized. Call initialize() first.")

        analysis = await self._universal_engine.analyze_data(source)

        # Add workspace-specific insights
        analysis['workspace_context'] = {
            'workspace_name': self._config.WORKSPACE_NAME,
            'optimization_settings': self._optimization_settings,
            'previous_data_types': list(self._workspace_profile.get('data_types_processed', set())),
            'performance_recommendations': self._get_performance_recommendations(analysis)
        }

        return analysis

    @command
    async def auto_optimize_workspace(self) -> Dict[str, Any]:
        """
        Automatically optimize workspace settings and performance.

        Returns:
            Optimization results and recommendations
        """
        if not self._universal_engine:
            raise RuntimeError("Workspace not initialized. Call initialize() first.")

        # Get engine performance stats
        engine_stats = self._universal_engine.get_performance_stats()

        # Get workspace data patterns
        data_patterns = self._analyze_workspace_patterns()

        # Generate optimization recommendations
        recommendations = {
            'current_performance': engine_stats,
            'workspace_patterns': data_patterns,
            'optimization_opportunities': [],
            'recommended_settings': {}
        }

        # Analyze and recommend optimizations
        if data_patterns.get('large_datasets_frequent', False):
            recommendations['optimization_opportunities'].append(
                "Enable automatic distributed processing for large datasets"
            )
            recommendations['recommended_settings']['distributed_threshold_gb'] = 5

        if data_patterns.get('streaming_data_detected', False):
            recommendations['optimization_opportunities'].append(
                "Optimize for streaming data processing"
            )
            recommendations['recommended_settings']['streaming_threshold_mb'] = 50

        # Apply automatic optimizations if enabled
        if self._optimization_settings.get('auto_optimize', True):
            self._optimization_settings.update(recommendations['recommended_settings'])
            self._logger.info("Applied automatic workspace optimizations")

        return recommendations

    @command
    async def stream_process_workspace_data(self, source: Union[str, Path],
                                          operation: str, chunk_size: Optional[int] = None,
                                          **kwargs) -> List[Any]:
        """
        Process large datasets in streaming fashion.

        Args:
            source: Data source
            operation: Operation to perform on each chunk
            chunk_size: Size of each chunk
            **kwargs: Operation parameters

        Returns:
            List of processed results
        """
        if not self._universal_engine:
            raise RuntimeError("Workspace not initialized. Call initialize() first.")

        results = []
        async for result in self._universal_engine.stream_process(source, operation, chunk_size, **kwargs):
            results.append(result)

        self._logger.info(f"Stream processed {len(results)} chunks from {source}")
        return results

    @command
    def get_workspace_performance_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive workspace performance statistics.

        Returns:
            Workspace performance metrics
        """
        stats = {
            'workspace_info': {
                'name': self._config.WORKSPACE_NAME,
                'profile': self._workspace_profile,
                'optimization_settings': self._optimization_settings
            },
            'engine': {
                'universal_engine': self._universal_engine.get_performance_stats() if self._universal_engine else None,
                'engine_id': self._universal_engine.runtime_id if self._universal_engine else None,
                'engine_name': self._universal_engine.name if self._universal_engine else None
            }
        }

        return stats

    def _get_performance_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate performance recommendations based on data analysis."""
        recommendations = []

        profile = analysis.get('profile', {})

        if profile.get('size_mb', 0) > 1000:
            recommendations.append("Consider using distributed processing for this large dataset")

        if profile.get('data_type') == 'time_series':
            recommendations.append("Enable time-series optimizations for better performance")

        if not profile.get('fits_in_memory', True):
            recommendations.append("Use streaming processing to handle this out-of-memory dataset")

        return recommendations

    def _analyze_workspace_patterns(self) -> Dict[str, Any]:
        """Analyze workspace data usage patterns."""
        patterns = {
            'data_types_used': list(self._workspace_profile.get('data_types_processed', set())),
            'large_datasets_frequent': False,
            'streaming_data_detected': False,
            'optimization_opportunities': []
        }

        # Analyze based on workspace profile
        if self._workspace_profile:
            data_types = self._workspace_profile.get('data_types_processed', set())
            if 'time_series' in data_types:
                patterns['streaming_data_detected'] = True
            if len(data_types) > 3:
                patterns['optimization_opportunities'].append("Multi-format optimization")

        return patterns

    @command
    async def create_workspace(self, workspace_directory: str, workspace_name: str, overwrite: bool = False) -> "Workspace":
        """
        Create a workspace on disk, then 'switches' to it.

        Args:
            workspace_directory (str): The directory where Workspace files will be located.
            workspace_name (str): The name of the Workspace.
            overwrite (bool): Whether to overwrite an existing workspace. Defaults to False.

        Returns:
            Workspace: The newly created workspace
        """
        base_dir = Path(workspace_directory).resolve().parent
        # Build a prospective config dict based on the current Config snapshot
        cfg_dict = self._config.copy_with(
            BASE_DIR=str(base_dir),
            WORKSPACE_NAME=workspace_name,
        )

        work_root = Path(cfg_dict["BASE_DIR"]) / "workspaces" / cfg_dict["WORKSPACE_NAME"]
        if work_root.exists() and not overwrite:
            raise FileExistsError(f"Workspace '{workspace_name}' already exists at {work_root}")

        # Create directory layout from the staged dict
        for folder in (
                cfg_dict.get("DATA_DIR", "data"),
                cfg_dict.get("LOG_DIR", "logs"),
                cfg_dict.get("WORKSPACE_DIR", "workspace"),
                os.path.normpath(os.path.join(cfg_dict.get("WORKSPACE_DIR", "workspace"), "operations")),
                cfg_dict.get("BACKUP_DIR", "backup"),
                cfg_dict.get("EXPORT_DIR", "export"),
                cfg_dict.get("ENGINE_DIR", "engine"),
        ):
            (work_root / folder).mkdir(parents=True, exist_ok=True)

        # Persist the staged config to disk
        config_path = work_root / "config.json"
        await Config.save_dict_to_file(str(config_path), cfg_dict)

        try:
            # Save Universal Data Engine configuration
            engine_config = {
                'engine_type': 'Universal',
                'created_at': asyncio.get_event_loop().time(),
                'workspace_name': workspace_name,
                'optimization_settings': {
                    'auto_optimize': True,
                    'prefer_speed': True,
                    'enable_caching': True,
                    'streaming_threshold_mb': 100,
                    'distributed_threshold_gb': 10
                }
            }
            engine_config_path = work_root / cfg_dict.get("DATA_DIR", "data") / "universal_engine.json"
            with open(engine_config_path, 'w') as f:
                json.dump(engine_config, f, indent=2, default=str)

            self._logger.info(f"Workspace created at {work_root}")

        except Exception as e:
            self._logger.warning(f"Failed to create engine configuration for new workspace: {e}")

        # Switch workspaces
        await self.switch_to_workspace(str(config_path))
        return self

    @command
    async def save_current_workspace(self) -> str:
        """
        Save current workspace to disk using self._config. Assumes an active workspace.
        """
        try:
            base_dir = Path(self._config.BASE_DIR)
            work_root = base_dir / "workspaces" / self._config.WORKSPACE_NAME

            # Ensure expected directories exist
            for d in (
                self._config.DATA_DIR, self._config.LOG_DIR, self._config.WORKSPACE_DIR,
                self._config.WORKSPACE_OPERATIONS_DIR, self._config.BACKUP_DIR,
                self._config.EXPORT_DIR, self._config.ENGINE_DIR
            ):
                (work_root / d).mkdir(parents=True, exist_ok=True)

            # Persist Universal Data Engine configuration
            if self._universal_engine:
                engine_config = {
                    'engine_type': 'Universal',
                    'engine_id': self._universal_engine.engine_id,
                    'name': self._universal_engine.name,
                    'workspace_profile': self._workspace_profile,
                    'optimization_settings': self._optimization_settings,
                    'saved_at': asyncio.get_event_loop().time()
                }
                engine_config_path = work_root / self._config.DATA_DIR / "universal_engine.json"
                with open(engine_config_path, 'w') as f:
                    json.dump(engine_config, f, indent=2, default=str)

                self._logger.debug("Universal Data Engine configuration saved")

            # Persist config
            await self._config.save_to_file(str(work_root / 'config.json'))
            return str(work_root)

        except Exception as e:
            self._logger.error(Exception(f"Failed to save current workspace: {e}"), self.__class__.__name__)
            return ""

    @command
    async def load_workspace(self, workspace_path: str) -> Optional["Workspace"]:
        """
        Load an existing workspace from disk.

        Args:
            workspace_path (str): Path to the workspace directory or its config.json file.

        Returns:
            Workspace: The loaded workspace instance, or None if loading failed.
        """
        try:
            wp = Path(workspace_path)
            if not wp.exists():
                self._logger.error(FileNotFoundError(f"Workspace path not found: {workspace_path}"),
                                   self.__class__.__name__)
                return None

            # Allow passing either .../config.json or the workspace dir
            if wp.name == 'config.json':
                work_root = wp.parent
            else:
                work_root = wp

            # Reset in-memory state safely
            self._reset_workspace()

            # Load a *fresh* Config from disk
            cfg_path = work_root / 'config.json'
            if not cfg_path.exists():
                self._logger.error(ValueError(f"Missing config.json in {work_root}"),
                                   self.__class__.__name__)
                return None

            self._config = await self._config.reload_from_file(str(cfg_path))
            if not self._config:
                self._logger.error(ValueError(f"Failed to load configuration from {cfg_path}"),
                                   self.__class__.__name__)
                return None

            # Reconfigure logger for the new workspace
            if not hasattr(self, '_logger'):
                self._logger = CustomLogger()
            await self._logger.initialize()
            self._logger.reconfigure_for_workspace(self._config)

            # Reset all singleton instances for workspace loading
            await self._reset_all_singletons()

            self._logger.debug(f"Loading memory manager for workspace at {work_root}")

            mm_db_path = str(work_root / self._config.DATA_DIR / "memory_manager.db")
            await self._memory_manager.rebind_to_db(mm_db_path)

            await self.initialize(config=self._config)

            # Load Universal Data Engine configuration
            universal_config_path = work_root / self._config.DATA_DIR / "universal_engine.json"
            if universal_config_path.exists():
                try:
                    with open(universal_config_path, 'r') as f:
                        engine_config = json.load(f)

                    # Restore Universal Data Engine with previous settings
                    self._universal_engine = UniversalDataEngine(
                        engine_id=engine_config.get('engine_id'),
                        name=engine_config.get('name')
                    )

                    # Restore workspace profile and optimization settings
                    self._workspace_profile = engine_config.get('workspace_profile', self._workspace_profile)
                    self._optimization_settings = engine_config.get('optimization_settings', self._optimization_settings)

                    # Convert data_types_processed back to set if it was serialized as list/string
                    if self._workspace_profile and 'data_types_processed' in self._workspace_profile:
                        data_types = self._workspace_profile['data_types_processed']
                        if isinstance(data_types, list):
                            self._workspace_profile['data_types_processed'] = set(data_types)
                        elif isinstance(data_types, str):
                            # Handle single string or comma-separated strings
                            self._workspace_profile['data_types_processed'] = set([data_types]) if data_types else set()
                        elif not isinstance(data_types, set):
                            # Fallback: ensure it's always a set
                            self._workspace_profile['data_types_processed'] = set()

                    self._logger.debug("Loaded Universal Data Engine configuration")

                except Exception as e:
                    self._logger.warning(f"Failed to load Universal Data Engine config: {e}")
                    # Create new Universal Data Engine if loading fails
                    self._universal_engine = UniversalDataEngine(
                        name=f"Workspace_Engine_{self._config.WORKSPACE_NAME}"
                    )
            else:
                # Create new Universal Data Engine for workspaces without config
                self._universal_engine = UniversalDataEngine(
                    name=f"Workspace_Engine_{self._config.WORKSPACE_NAME}"
                )
                self._logger.info("Created new Universal Data Engine for workspace")

            await self._library_manifest.load_user_library()

            self._active_workspace_path = work_root
            self._logger.info(f"Workspace loaded from \'{work_root}\'. You can now interact with the GUI or enter "
                              f"commands in this console. Type \'_help\' for a table of available commands.")
            return self

        except Exception as e:
            self._logger.error(Exception(f"Failed to load workspace: {e}"), self.__class__.__name__)
            return None

    @command
    async def switch_to_workspace(self, config_or_dir: str) -> "Workspace":
        """
        Close the current workspace (if any) and then load the target workspace.
        """
        await self.close()
        return await self.load_workspace(config_or_dir)

    def _reset_workspace(self) -> None:
        """
        Clears existing data in the workspace to ensure a clean load.
        """
        self._initialized = False

    async def _reset_all_singletons(self) -> None:
        """
        Reset all singleton instances for workspace loading.
        """
        try:
            # Reset and configure MemoryManager
            if not hasattr(self, '_memory_manager') or not self._memory_manager:
                self._memory_manager = MemoryManager()
            await self._memory_manager.reset()
            await self._memory_manager.initialize()
            self._memory_manager.set_config(self._config)

            # Reset NodeEditorManager
            from research_analytics_suite.gui.NodeEditorManager import NodeEditorManager
            node_manager = NodeEditorManager()
            await node_manager.reset_for_workspace(self._config)

            # Reset OperationControl
            from research_analytics_suite.operation_manager.control.OperationControl import OperationControl
            operation_control = OperationControl()
            await operation_control.reset_for_workspace(self._config)

            # Reset CommandRegistry
            from research_analytics_suite.commands.registry.CommandRegistry import CommandRegistry
            command_registry = CommandRegistry()
            await command_registry.reset_for_workspace(self._config)

            # Reset and get fresh LibraryManifest
            if not hasattr(self, '_library_manifest') or not self._library_manifest:
                from research_analytics_suite.library_manifest.LibraryManifest import LibraryManifest
                self._library_manifest = LibraryManifest()
            await self._library_manifest.reset_for_workspace(self._config)

            self._logger.debug("All singleton instances reset for workspace loading")

        except Exception as e:
            if self._logger:
                self._logger.error(e, self.__class__.__name__)
            else:
                print(f"Warning: Error during singleton reset: {e}")

    async def close(self) -> None:
        """
        Gracefully close the current workspace: stop engines, flush state, and
        release resources. After this, the Workspace is 'inactive' until initialize/load is called.
        """
        try:
            # Clean up Universal Data Engine
            if self._universal_engine and self._active_workspace_path:
                try:
                    await self._universal_engine.cleanup()
                    self._logger.debug("Universal Data Engine cleaned up")
                except Exception as e:
                    self._logger.warning(f"Failed to cleanup Universal Data Engine: {e}")

            self._active_workspace_path = None
            self._initialized = False
            self._logger.info("Workspace closed gracefully")

            # Detach file handlers for the old workspace so they don't keep writing
            if hasattr(self, "_logger") and self._logger:
                self._logger.clear_file_handlers()

        except Exception as e:
            self._logger.error(Exception(f"Failed during workspace close: {e}"), self.__class__.__name__)

    # ===============================
    # CONVENIENCE METHODS
    # ===============================

    @command
    async def quick_load(self, source: Union[str, Path, Any], **kwargs) -> Any:
        """
        Quickly load data using the Universal Data Engine.

        Args:
            source: Data source
            **kwargs: Additional parameters

        Returns:
            Loaded data (without profile)
        """
        data, _ = await self.load_data(source, **kwargs)
        return data

    @command
    async def quick_save(self, data: Any, destination: Union[str, Path], **kwargs) -> bool:
        """
        Quickly save data using the Universal Data Engine.

        Args:
            data: Data to save
            destination: Where to save
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        return await self.save_data(data, destination, **kwargs)

    @command
    async def workspace_health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive workspace health check.

        Returns:
            Health check results
        """
        health = {
            'workspace_status': 'healthy',
            'initialized': self._initialized,
            'engine': {},
            'issues': []
        }

        try:
            # Check Universal Data Engine
            if self._universal_engine:
                engine_health = await self._universal_engine.health_check()
                health['engine'] = engine_health
            else:
                health['issues'].append("Universal Data Engine not initialized")
                health['workspace_status'] = 'degraded'

            # Check workspace configuration
            if not self._active_workspace_path:
                health['issues'].append("No active workspace path")

            if not self._config:
                health['issues'].append("No workspace configuration")

        except Exception as e:
            health['workspace_status'] = 'unhealthy'
            health['issues'].append(f"Health check failed: {e}")

        return health

    def __str__(self) -> str:
        engine_status = "Ready" if self._universal_engine else "Not initialized"
        return f"Workspace(name={self._config.WORKSPACE_NAME}, engine={engine_status})"

    def __repr__(self) -> str:
        return (f"Workspace(workspace_name='{self._config.WORKSPACE_NAME}', "
                f"universal_engine={bool(self._universal_engine)}, "
                f"initialized={self._initialized})")

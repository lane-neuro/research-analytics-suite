"""
UniversalDataEngine Module

Data engine that can handle ANY data type of ANY size with optimal performance.
Automatically selects the best adapter and execution backend for each operation.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Development
"""
from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any, Dict, List, Optional, Union, AsyncIterator, Tuple
from pathlib import Path

from research_analytics_suite.utils.CustomLogger import CustomLogger
from research_analytics_suite.utils.Config import Config
from research_analytics_suite.commands import command, link_class_commands

from research_analytics_suite.data_engine.core.DataProfile import DataProfile
from research_analytics_suite.data_engine.core.DataContext import DataContext
from research_analytics_suite.data_engine.adapters.AdapterRegistry import AdapterRegistry
from research_analytics_suite.data_engine.execution.ExecutionEngine import (
    ExecutionEngine, ExecutionResult, ExecutionContext
)
from research_analytics_suite.data_engine.storage.StorageLayer import StorageLayer


@link_class_commands
class UniversalDataEngine:
    """
    Data engine that handles ANY data type of ANY size.

    The Universal Data Engine automatically:
    - Profiles data to understand its characteristics
    - Selects optimal adapters for the data type
    - Chooses the best execution backend for performance
    - Manages storage across any backend
    - Scales automatically from bytes to petabytes
    - Optimizes for available system resources
    """

    def __init__(self, engine_id: Optional[str] = None, name: Optional[str] = None):
        """
        Initialize the Universal Data Engine.

        Args:
            engine_id: Optional engine identifier
            name: Optional engine name
        """
        self.engine_id = engine_id or str(uuid.uuid4())
        self.name = name or f"UniversalEngine_{self.engine_id[:8]}"

        self._logger = CustomLogger()
        self._config = Config()

        # Initialize core components
        self._adapter_registry = AdapterRegistry()
        self._execution_engine = ExecutionEngine(self._adapter_registry)
        self._storage_layer = StorageLayer()

        # Auto-register built-in adapters
        self._adapter_registry.auto_register_builtin_adapters()

        # Engine state
        self._active_operations: Dict[str, Any] = {}
        self._data_cache: Dict[str, Any] = {}
        self._performance_metrics: Dict[str, Any] = {}

        self._logger.debug(f"Initialized Universal Data Engine: {self.name}")

    @property
    def runtime_id(self) -> str:
        """Get the runtime identifier."""
        return f"ude-{self.engine_id[:8]}"

    @property
    def short_id(self) -> str:
        """Get the short identifier."""
        return f"{self.name}_{self.engine_id[:4]}"

    @command
    async def load_data(self, source: Union[str, Path, Any],
                       data_type: Optional[str] = None,
                       **kwargs) -> DataContext:
        """
        Load data from any source with automatic optimization.

        Args:
            source: Data source (path, URL, or data object)
            data_type: Optional data type hint
            **kwargs: Additional loading parameters

        Returns:
            DataContext containing loaded data with profile and schema
        """
        start_time = time.time()
        operation_id = f"load_{start_time}"

        try:
            if isinstance(source, (str, Path)):
                data_profile = DataProfile.from_file(source)
            else:
                data_profile = DataProfile.from_data(source, data_type)

            if data_type:
                data_profile.data_type = data_type

            self._logger.info(f"Loading {data_profile.data_type} data ({data_profile.size_mb:.2f} MB)")

            adapter = self._adapter_registry.select_best_adapter(data_profile, 'load')
            if not adapter:
                raise ValueError(f"No suitable adapter found for {data_profile.data_type} data")

            result = await self._execution_engine.execute(
                data_profile, 'load', source, adapter=adapter, **kwargs
            )

            if not result.success:
                raise RuntimeError(f"Load failed: {result.error_message}")

            context = DataContext.create(result.result, self._adapter_registry, data_type)

            cache_key = f"data_{hash(str(source))}"
            self._data_cache[cache_key] = {'context': context, 'loaded_at': time.time()}

            execution_time = time.time() - start_time
            self._logger.info(f"Loaded data in {execution_time:.2f}s using {result.adapter_used}")

            return context

        except Exception as e:
            self._logger.error(f"Failed to load data from {source}: {e}")
            raise

    @command
    async def save_data(self, data: Any, destination: Union[str, Path],
                       data_profile: Optional[DataProfile] = None,
                       **kwargs) -> bool:
        """
        Save data to any destination with automatic optimization.

        Args:
            data: Data to save
            destination: Where to save the data
            data_profile: Optional data profile (will be created if not provided)
            **kwargs: Additional saving parameters

        Returns:
            True if successful
        """
        try:
            # Create data profile if not provided
            if data_profile is None:
                data_profile = DataProfile.from_data(data)

            self._logger.info(f"Saving {data_profile.data_type} data to {destination}")

            # Select optimal adapter
            adapter = self._adapter_registry.select_best_adapter(data_profile, 'save')
            if not adapter:
                raise ValueError(f"No suitable adapter found for {data_profile.data_type} data")

            # Execute save operation
            result = await self._execution_engine.execute(
                data_profile, 'save', data, destination=destination, adapter=adapter, **kwargs
            )

            if not result.success:
                raise RuntimeError(f"Save failed: {result.error_message}")

            self._logger.info(f"Saved data using {result.adapter_used}")
            return True

        except Exception as e:
            self._logger.error(f"Failed to save data to {destination}: {e}")
            return False

    @command
    async def transform_data(self, data: Any, operation: str,
                           data_profile: Optional[DataProfile] = None,
                           **kwargs) -> Any:
        """
        Transform data using optimal backend and adapter.

        Args:
            data: Data to transform
            operation: Transformation operation
            data_profile: Optional data profile
            **kwargs: Operation parameters

        Returns:
            Transformed data
        """
        try:
            # Create data profile if not provided
            if data_profile is None:
                data_profile = DataProfile.from_data(data)

            self._logger.debug(f"Transforming {data_profile.data_type} data: {operation}")

            # Execute transformation
            result = await self._execution_engine.execute(
                data_profile, operation, data, **kwargs
            )

            if not result.success:
                raise RuntimeError(f"Transform failed: {result.error_message}")

            return result.result

        except Exception as e:
            self._logger.error(f"Failed to transform data: {e}")
            raise

    @command
    async def analyze_data(self, source: Union[str, Path, Any]) -> Dict[str, Any]:
        """
        Analyze data and provide comprehensive insights.

        Args:
            source: Data source to analyze

        Returns:
            Analysis results
        """
        try:
            context = await self.load_data(source)

            adapter = self._adapter_registry.select_best_adapter(context.profile, 'schema')
            sample = adapter.get_sample(context.data) if adapter else None
            size_info = adapter.get_size_info(context.data) if adapter else {}

            analysis = {
                'profile': {
                    'data_type': context.profile.data_type,
                    'format': context.profile.format,
                    'size_mb': context.profile.size_mb,
                    'fits_in_memory': context.profile.fits_in_memory,
                    'requires_distributed': context.profile.requires_distributed_processing,
                    'suggested_backend': context.profile.suggest_backend(),
                    'optimal_chunk_size': context.profile.optimal_chunk_size
                },
                'schema': context.schema,
                'size_info': size_info,
                'sample_available': sample is not None,
                'recommended_operations': adapter.get_recommended_operations(context.profile) if adapter else [],
                'optimization_hints': context.profile.processing_hints
            }

            return analysis

        except Exception as e:
            self._logger.error(f"Failed to analyze data: {e}")
            raise

    @command
    async def stream_process(self, source: Union[str, Path],
                           operation: str, chunk_size: Optional[int] = None,
                           **kwargs) -> AsyncIterator[Any]:
        """
        Process data in streaming fashion for infinite scalability.

        Args:
            source: Data source
            operation: Operation to perform on each chunk
            chunk_size: Size of each chunk
            **kwargs: Operation parameters

        Yields:
            Processed chunks
        """
        try:
            # Profile the data
            data_profile = DataProfile.from_file(source)
            data_profile.is_streaming = True

            # Use optimal chunk size if not specified
            if chunk_size is None:
                chunk_size = data_profile.optimal_chunk_size

            # Load data with streaming adapter
            adapter = self._adapter_registry.select_best_adapter(data_profile, 'load')
            data = await adapter.load(source)

            # Process in chunks
            async for chunk in adapter.iterate_chunks(data, chunk_size):
                try:
                    # Transform each chunk
                    result = await self.transform_data(chunk, operation, **kwargs)
                    yield result
                except Exception as e:
                    self._logger.warning(f"Failed to process chunk: {e}")
                    continue

        except Exception as e:
            self._logger.error(f"Failed to stream process {source}: {e}")
            raise

    @command
    async def auto_optimize(self, data: Any, operations: List[str],
                          data_profile: Optional[DataProfile] = None) -> Dict[str, Any]:
        """
        Automatically optimize data and operations for best performance.

        Args:
            data: Data to optimize
            operations: List of operations to optimize for
            data_profile: Optional data profile

        Returns:
            Optimization results and suggestions
        """
        try:
            if data_profile is None:
                data_profile = DataProfile.from_data(data)

            # Get optimization suggestions from adapter
            adapter = self._adapter_registry.select_best_adapter(data_profile, operations[0])
            optimizations = adapter.optimize_for_profile(data_profile) if adapter else {}

            # Benchmark different approaches
            benchmark_results = await self._adapter_registry.benchmark_adapters(
                data_profile, operations
            )

            suggestions = {
                'current_profile': {
                    'data_type': data_profile.data_type,
                    'size_mb': data_profile.size_mb,
                    'backend': data_profile.suggest_backend()
                },
                'optimizations': optimizations,
                'benchmark_results': benchmark_results,
                'recommendations': []
            }

            # Generate specific recommendations
            if not data_profile.fits_in_memory:
                suggestions['recommendations'].append("Use streaming or chunked processing")

            if data_profile.is_large_dataset:
                suggestions['recommendations'].append("Consider distributed processing")

            if data_profile.requires_gpu:
                suggestions['recommendations'].append("Use GPU-accelerated backends")

            return suggestions

        except Exception as e:
            self._logger.error(f"Failed to auto-optimize: {e}")
            raise

    @command
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """
        Get all supported data formats and types.

        Returns:
            Dictionary of supported formats by data type
        """
        adapters_info = self._adapter_registry.list_adapters()
        formats_by_type = {}

        for adapter_name, info in adapters_info.items():
            for data_type in info['supported_data_types']:
                if data_type not in formats_by_type:
                    formats_by_type[data_type] = []
                formats_by_type[data_type].extend(info['supported_formats'])

        # Remove duplicates
        for data_type in formats_by_type:
            formats_by_type[data_type] = list(set(formats_by_type[data_type]))

        return formats_by_type

    @command
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive performance statistics.

        Returns:
            Performance statistics
        """
        return {
            'engine_info': {
                'engine_id': self.engine_id,
                'name': self.name,
                'runtime_id': self.runtime_id
            },
            'execution_engine': self._execution_engine.get_performance_stats(),
            'adapter_registry': self._adapter_registry.get_statistics(),
            'storage_layer': self._storage_layer.get_backend_stats(),
            'active_operations': len(self._active_operations),
            'cached_datasets': len(self._data_cache)
        }

    @command
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check of the engine.

        Returns:
            Health check results
        """
        health = {
            'status': 'healthy',
            'components': {},
            'issues': []
        }

        try:
            # Test adapter registry
            adapters = self._adapter_registry.list_adapters()
            health['components']['adapter_registry'] = {
                'status': 'ok',
                'total_adapters': len(adapters)
            }

            # Test storage backends
            storage_stats = self._storage_layer.get_backend_stats()
            health['components']['storage_layer'] = {
                'status': 'ok',
                'backends': storage_stats['total_backends']
            }

            # Test execution engine
            exec_stats = self._execution_engine.get_performance_stats()
            health['components']['execution_engine'] = {
                'status': 'ok',
                'backend_availability': exec_stats['backend_availability']
            }

            # Check for issues
            unavailable_backends = [k for k, v in exec_stats['backend_availability'].items() if not v]
            if unavailable_backends:
                health['issues'].append(f"Unavailable backends: {unavailable_backends}")

            if len(adapters) == 0:
                health['issues'].append("No adapters registered")
                health['status'] = 'unhealthy'

        except Exception as e:
            health['status'] = 'unhealthy'
            health['issues'].append(f"Health check failed: {e}")

        return health

    @command
    async def cleanup(self) -> None:
        """Clean up engine resources."""
        try:
            # Clear caches
            self._data_cache.clear()
            self._active_operations.clear()

            # Clear performance caches
            self._adapter_registry.clear_performance_cache()
            self._execution_engine.clear_performance_history()

            # Cleanup storage
            await self._storage_layer.cleanup_temp_storage()

            self._logger.info("Engine cleanup completed")

        except Exception as e:
            self._logger.error(f"Cleanup failed: {e}")

    @command
    async def filter_rows(self, context: DataContext, condition: str) -> DataContext:
        """
        Filter rows from data based on a condition.

        Args:
            context: DataContext containing data and metadata
            condition: Filter condition (e.g., "price > 100", "name == 'Alice'")

        Returns:
            New DataContext with filtered data
        """
        try:
            self._logger.debug(f"Filtering rows with condition: {condition}")

            # Execute filter operation with schema available in kwargs
            result = await self._execution_engine.execute(
                context.profile, 'filter_rows', context.data,
                condition=condition,
                column_names=context.columns  # Pass column names for numpy arrays
            )

            if not result.success:
                raise RuntimeError(f"Row filtering failed: {result.error_message}")

            # Return new context with updated data
            return context.update_after_transform(result.result, self._adapter_registry, preserve_type=True)

        except Exception as e:
            self._logger.error(f"Failed to filter rows: {e}")
            raise

    @command
    async def select_columns(self, context: DataContext, columns: Union[List[str], str]) -> DataContext:
        """
        Select specific columns from data.

        Args:
            context: DataContext containing data and metadata
            columns: Column names to select (string or list of strings)

        Returns:
            New DataContext with selected columns only
        """
        try:
            # Ensure columns is a list
            if isinstance(columns, str):
                columns = [columns]

            self._logger.debug(f"Selecting columns: {columns}")

            # Execute column selection using optimal adapter
            result = await self._execution_engine.execute(
                context.profile, 'select_columns', context.data, columns=columns
            )

            if not result.success:
                raise RuntimeError(f"Column selection failed: {result.error_message}")

            # Return new context with updated data
            return context.update_after_transform(result.result, self._adapter_registry, preserve_type=True)

        except Exception as e:
            self._logger.error(f"Failed to select columns: {e}")
            raise

    @command
    async def subset_data(self, context: DataContext,
                         rows: Optional[str] = None,
                         columns: Optional[Union[List[str], str]] = None,
                         start_row: Optional[int] = None,
                         end_row: Optional[int] = None) -> DataContext:
        """
        Create a subset of data with row and/or column filtering.

        Args:
            context: DataContext containing data and metadata
            rows: Row filter condition (e.g., "price > 100", "name == 'Alice'")
            columns: Column names to select
            start_row: Starting row index for range selection
            end_row: Ending row index for range selection

        Returns:
            New DataContext with subset data
        """
        try:
            self._logger.debug(f"Creating data subset - rows: {rows}, columns: {columns}, "
                             f"range: {start_row}-{end_row}")

            current_context = context

            if start_row is not None or end_row is not None:
                result = await self._execution_engine.execute(
                    current_context.profile, 'slice_rows', current_context.data,
                    start_row=start_row, end_row=end_row
                )
                if not result.success:
                    raise RuntimeError(f"Row slicing failed: {result.error_message}")

                current_context = current_context.update_after_transform(
                    result.result, self._adapter_registry, preserve_type=True
                )

            if rows:
                current_context = await self.filter_rows(current_context, rows)

            if columns:
                current_context = await self.select_columns(current_context, columns)

            self._logger.info(f"Created data subset successfully")
            return current_context

        except Exception as e:
            self._logger.error(f"Failed to create data subset: {e}")
            raise

    @command
    async def get_data_info(self, data: Any,
                           data_profile: Optional[DataProfile] = None) -> Dict[str, Any]:
        """
        Get comprehensive information about data structure.

        Args:
            data: Data to analyze
            data_profile: Optional data profile

        Returns:
            Dictionary with data information (columns, types, shape, etc.)
        """
        try:
            if data_profile is None:
                data_profile = DataProfile.from_data(data)

            # Get adapter for data inspection
            adapter = self._adapter_registry.select_best_adapter(data_profile, 'info')
            if not adapter:
                raise ValueError(f"No suitable adapter found for data info")

            info = {
                'data_type': data_profile.data_type,
                'size_mb': data_profile.size_mb,
                'columns': [],
                'shape': None,
                'dtypes': {},
                'sample_values': {}
            }

            # Get detailed info using adapter
            if hasattr(adapter, 'get_info'):
                detailed_info = adapter.get_info(data)
                info.update(detailed_info)

            return info

        except Exception as e:
            self._logger.error(f"Failed to get data info: {e}")
            raise

    def register_adapter(self, adapter) -> None:
        """
        Register a custom adapter.

        Args:
            adapter: Custom adapter to register
        """
        self._adapter_registry.register_adapter(adapter)

    def register_storage_backend(self, backend) -> None:
        """
        Register a custom storage backend.

        Args:
            backend: Custom storage backend to register
        """
        self._storage_layer.register_backend(backend)

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()

    def __str__(self) -> str:
        return f"UniversalDataEngine(id={self.runtime_id}, name={self.name})"

    def __repr__(self) -> str:
        return (f"UniversalDataEngine(engine_id='{self.engine_id}', "
                f"name='{self.name}', adapters={len(self._adapter_registry.list_adapters())})")


# Convenience functions for quick usage
@command
async def quick_load(source: Union[str, Path, Any], **kwargs) -> DataContext:
    """
    Quickly load data using a temporary Universal Data Engine.

    Args:
        source: Data source
        **kwargs: Additional parameters

    Returns:
        DataContext containing loaded data
    """
    async with UniversalDataEngine() as engine:
        return await engine.load_data(source, **kwargs)


@command
async def quick_save(data: Any, destination: Union[str, Path], **kwargs) -> bool:
    """
    Quickly save data using a temporary Universal Data Engine.

    Args:
        data: Data to save
        destination: Where to save
        **kwargs: Additional parameters

    Returns:
        True if successful
    """
    async with UniversalDataEngine() as engine:
        return await engine.save_data(data, destination, **kwargs)


@command
async def quick_analyze(source: Union[str, Path, Any]) -> Dict[str, Any]:
    """
    Quickly analyze data using a temporary Universal Data Engine.

    Args:
        source: Data source to analyze

    Returns:
        Analysis results
    """
    async with UniversalDataEngine() as engine:
        return await engine.analyze_data(source)

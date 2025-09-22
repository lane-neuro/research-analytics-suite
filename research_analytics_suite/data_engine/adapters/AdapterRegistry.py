"""
AdapterRegistry Module

Manages registration and selection of data adapters for universal data processing.

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

import importlib
from typing import Dict, List, Optional, Type, Any, Tuple
from collections import defaultdict

from research_analytics_suite.utils.CustomLogger import CustomLogger
from research_analytics_suite.data_engine.core.DataProfile import DataProfile
from research_analytics_suite.data_engine.adapters.BaseAdapter import BaseAdapter


class AdapterRegistry:
    """
    Registry for managing and selecting optimal data adapters.

    The registry maintains a collection of adapters and provides intelligent
    selection based on data profiles and performance characteristics.
    """

    def __init__(self):
        """Initialize the adapter registry."""
        self._logger = CustomLogger()
        self._adapters: Dict[str, BaseAdapter] = {}
        self._adapters_by_format: Dict[str, List[BaseAdapter]] = defaultdict(list)
        self._adapters_by_type: Dict[str, List[BaseAdapter]] = defaultdict(list)
        self._performance_cache: Dict[str, Dict[str, float]] = {}
        self._fallback_adapters: List[BaseAdapter] = []

    def register_adapter(self, adapter: BaseAdapter, is_fallback: bool = False) -> None:
        """
        Register a new adapter.

        Args:
            adapter: Adapter instance to register
            is_fallback: Whether this adapter can handle any data type as fallback
        """
        self._adapters[adapter.name] = adapter

        # Index by supported formats
        for format_ext in adapter.supported_formats:
            self._adapters_by_format[format_ext].append(adapter)

        # Index by supported data types
        for data_type in adapter.supported_data_types:
            self._adapters_by_type[data_type].append(adapter)

        # Add to fallback list if specified
        if is_fallback:
            self._fallback_adapters.append(adapter)

        self._logger.debug(f"Registered adapter: {adapter.name}")

    def unregister_adapter(self, adapter_name: str) -> bool:
        """
        Unregister an adapter.

        Args:
            adapter_name: Name of adapter to remove

        Returns:
            True if adapter was found and removed
        """
        if adapter_name not in self._adapters:
            return False

        adapter = self._adapters.pop(adapter_name)

        # Remove from format indices
        for format_ext in adapter.supported_formats:
            if adapter in self._adapters_by_format[format_ext]:
                self._adapters_by_format[format_ext].remove(adapter)

        # Remove from type indices
        for data_type in adapter.supported_data_types:
            if adapter in self._adapters_by_type[data_type]:
                self._adapters_by_type[data_type].remove(adapter)

        # Remove from fallback list
        if adapter in self._fallback_adapters:
            self._fallback_adapters.remove(adapter)

        self._logger.debug(f"Unregistered adapter: {adapter_name}")
        return True

    def get_adapter(self, adapter_name: str) -> Optional[BaseAdapter]:
        """
        Get adapter by name.

        Args:
            adapter_name: Name of the adapter

        Returns:
            Adapter instance or None if not found
        """
        return self._adapters.get(adapter_name)

    def find_adapters(self, data_profile: DataProfile) -> List[BaseAdapter]:
        """
        Find all adapters that can handle the given data profile.

        Args:
            data_profile: Profile of the data

        Returns:
            List of compatible adapters
        """
        compatible_adapters = []

        # Try format-specific adapters first
        if data_profile.format in self._adapters_by_format:
            for adapter in self._adapters_by_format[data_profile.format]:
                if adapter.can_handle(data_profile):
                    compatible_adapters.append(adapter)

        # Try type-specific adapters
        if data_profile.data_type in self._adapters_by_type:
            for adapter in self._adapters_by_type[data_profile.data_type]:
                if adapter.can_handle(data_profile) and adapter not in compatible_adapters:
                    compatible_adapters.append(adapter)

        # Try all adapters if no specific matches
        if not compatible_adapters:
            for adapter in self._adapters.values():
                if adapter.can_handle(data_profile):
                    compatible_adapters.append(adapter)

        # Add fallback adapters if still no matches
        if not compatible_adapters:
            for adapter in self._fallback_adapters:
                if adapter.can_handle(data_profile):
                    compatible_adapters.append(adapter)

        return compatible_adapters

    def select_best_adapter(self, data_profile: DataProfile,
                           operation: str = 'load') -> Optional[BaseAdapter]:
        """
        Select the best adapter for a given data profile and operation.

        Args:
            data_profile: Profile of the data
            operation: Operation to be performed

        Returns:
            Best adapter or None if no compatible adapter found
        """
        compatible_adapters = self.find_adapters(data_profile)

        if not compatible_adapters:
            self._logger.warning(f"No compatible adapters found for {data_profile}")
            return None

        if len(compatible_adapters) == 1:
            return compatible_adapters[0]

        # Score adapters based on multiple criteria
        scored_adapters = []
        for adapter in compatible_adapters:
            score = self._score_adapter(adapter, data_profile, operation)
            scored_adapters.append((adapter, score))

        # Sort by score (higher is better)
        scored_adapters.sort(key=lambda x: x[1], reverse=True)

        best_adapter = scored_adapters[0][0]
        self._logger.debug(f"Selected adapter: {best_adapter.name} for {data_profile.data_type}")

        return best_adapter

    def _score_adapter(self, adapter: BaseAdapter, data_profile: DataProfile,
                      operation: str) -> float:
        """
        Score an adapter for a given data profile and operation.

        Args:
            adapter: Adapter to score
            data_profile: Profile of the data
            operation: Operation to be performed

        Returns:
            Score (higher is better)
        """
        score = 0.0

        # Base score for format compatibility
        if data_profile.format in adapter.supported_formats:
            score += 10.0

        # Score for data type compatibility
        if data_profile.data_type in adapter.supported_data_types:
            score += 5.0

        # Performance-based scoring
        perf_key = f"{adapter.name}_{data_profile.data_type}_{operation}"
        if perf_key in self._performance_cache:
            perf_metrics = self._performance_cache[perf_key]
            # Higher score for better performance (lower execution time)
            score += max(0, 10 - perf_metrics.get('execution_time', 10))

        # Size-based scoring
        if data_profile.is_large_dataset:
            # Prefer adapters that handle large data well
            if 'distributed' in adapter.name.lower() or 'dask' in adapter.name.lower():
                score += 5.0
            if 'polars' in adapter.name.lower():
                score += 3.0

        # Memory efficiency scoring
        estimated_memory = adapter.estimate_memory_usage(operation, data_profile)
        available_memory = data_profile.estimated_memory_usage
        if estimated_memory <= available_memory:
            score += 3.0

        # Operation-specific scoring
        recommended_ops = adapter.get_recommended_operations(data_profile)
        if operation in recommended_ops:
            score += 2.0

        return score

    def update_performance_metrics(self, adapter_name: str, data_type: str,
                                  operation: str, metrics: Dict[str, float]) -> None:
        """
        Update performance metrics for an adapter.

        Args:
            adapter_name: Name of the adapter
            data_type: Data type that was processed
            operation: Operation that was performed
            metrics: Performance metrics (execution_time, memory_usage, etc.)
        """
        key = f"{adapter_name}_{data_type}_{operation}"
        if key not in self._performance_cache:
            self._performance_cache[key] = {}

        self._performance_cache[key].update(metrics)
        self._logger.debug(f"Updated performance metrics for {key}: {metrics}")

    def get_adapter_info(self, adapter_name: str) -> Dict[str, Any]:
        """
        Get detailed information about an adapter.

        Args:
            adapter_name: Name of the adapter

        Returns:
            Adapter information
        """
        adapter = self._adapters.get(adapter_name)
        if not adapter:
            return {}

        return {
            'name': adapter.name,
            'supported_formats': adapter.supported_formats,
            'supported_data_types': adapter.supported_data_types,
            'class': adapter.__class__.__name__,
            'module': adapter.__class__.__module__
        }

    def list_adapters(self) -> Dict[str, Dict[str, Any]]:
        """
        List all registered adapters.

        Returns:
            Dictionary of adapter information
        """
        return {name: self.get_adapter_info(name) for name in self._adapters.keys()}

    def auto_register_builtin_adapters(self) -> None:
        """
        Automatically register built-in adapters using existing dependencies only.
        """
        # Essential adapters using only existing dependencies
        builtin_adapters = [
            ('research_analytics_suite.data_engine.adapters.tabular.PandasAdapter', 'PandasAdapter'),
            ('research_analytics_suite.data_engine.adapters.tabular.DaskAdapter', 'DaskAdapter'),
            ('research_analytics_suite.data_engine.adapters.ml.TorchAdapter', 'TorchAdapter'),
            ('research_analytics_suite.data_engine.adapters.ml.NumpyAdapter', 'NumpyAdapter'),
        ]

        for module_path, class_name in builtin_adapters:
            try:
                module = importlib.import_module(module_path)
                adapter_class = getattr(module, class_name)
                adapter = adapter_class()

                # Mark some adapters as fallback
                is_fallback = class_name in ['PandasAdapter', 'NumpyAdapter']
                self.register_adapter(adapter, is_fallback=is_fallback)

            except ImportError as e:
                self._logger.debug(f"Could not import {module_path}: {e}")
            except Exception as e:
                self._logger.warning(f"Failed to register {class_name}: {e}")

    def benchmark_adapters(self, data_profile: DataProfile,
                          operations: List[str] = None) -> Dict[str, Dict[str, float]]:
        """
        Benchmark compatible adapters for a data profile.

        Args:
            data_profile: Profile of test data
            operations: Operations to benchmark (default: ['load', 'transform'])

        Returns:
            Benchmark results
        """
        if operations is None:
            operations = ['load', 'transform']

        compatible_adapters = self.find_adapters(data_profile)
        results = {}

        for adapter in compatible_adapters:
            adapter_results = {}
            for operation in operations:
                # This would include actual benchmarking logic
                # For now, return estimated values
                memory_usage = adapter.estimate_memory_usage(operation, data_profile)
                adapter_results[operation] = {
                    'estimated_memory_mb': memory_usage / (1024 * 1024),
                    'estimated_time_seconds': 1.0  # Placeholder
                }
            results[adapter.name] = adapter_results

        return results

    def clear_performance_cache(self) -> None:
        """Clear all cached performance metrics."""
        self._performance_cache.clear()
        self._logger.debug("Cleared performance cache")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get registry statistics.

        Returns:
            Statistics about registered adapters
        """
        format_counts = defaultdict(int)
        type_counts = defaultdict(int)

        for adapter in self._adapters.values():
            for fmt in adapter.supported_formats:
                format_counts[fmt] += 1
            for data_type in adapter.supported_data_types:
                type_counts[data_type] += 1

        return {
            'total_adapters': len(self._adapters),
            'fallback_adapters': len(self._fallback_adapters),
            'supported_formats': dict(format_counts),
            'supported_data_types': dict(type_counts),
            'performance_cache_size': len(self._performance_cache)
        }
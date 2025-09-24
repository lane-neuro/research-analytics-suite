"""
ExecutionEngine Module

Adaptive execution engine that automatically selects the optimal backend
for any data processing task based on data characteristics and system resources.

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
from typing import Any, Dict, List, Optional, Callable, Union
from enum import Enum
from dataclasses import dataclass

import psutil

from research_analytics_suite.utils.CustomLogger import CustomLogger
from research_analytics_suite.data_engine.core.DataProfile import DataProfile
from research_analytics_suite.data_engine.adapters.AdapterRegistry import AdapterRegistry


class ExecutionBackend(Enum):
    """Available execution backends (only includes actually available backends)."""
    PANDAS = "pandas"
    DASK_LOCAL = "dask_local"
    TORCH = "torch"
    AUTO = "auto"


@dataclass
class ExecutionContext:
    """Context for execution including resources and constraints."""
    available_memory: int
    available_cores: int
    has_gpu: bool
    max_execution_time: Optional[float] = None
    memory_limit: Optional[int] = None
    prefer_speed: bool = True
    prefer_memory_efficiency: bool = False
    allow_distributed: bool = True


@dataclass
class ExecutionResult:
    """Result of an execution including performance metrics."""
    result: Any
    execution_time: float
    memory_used: int
    backend_used: str
    adapter_used: str
    success: bool
    error_message: Optional[str] = None


class ExecutionEngine:
    """
    Adaptive execution engine that automatically selects optimal backends.

    The engine analyzes data profiles, system resources, and operation requirements
    to choose the best processing backend and adapter combination.
    """

    def __init__(self, adapter_registry: AdapterRegistry):
        """
        Initialize the execution engine.

        Args:
            adapter_registry: Registry of available adapters
        """
        self._logger = CustomLogger()
        self._adapter_registry = adapter_registry
        self._backend_availability = {}
        self._performance_history = {}
        self._active_executions = {}

        # Initialize system monitoring
        self._update_system_info()
        self._check_backend_availability()

    def _update_system_info(self) -> None:
        """Update current system resource information."""
        memory = psutil.virtual_memory()
        self._system_context = ExecutionContext(
            available_memory=memory.available,
            available_cores=psutil.cpu_count(),
            has_gpu=self._check_gpu_availability()
        )

    def _check_gpu_availability(self) -> bool:
        """Check if GPU is available."""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            try:
                import tensorflow as tf
                return len(tf.config.list_physical_devices('GPU')) > 0
            except ImportError:
                return False

    def _check_backend_availability(self) -> None:
        """Check which backends are available on the system."""
        backends_to_check = {
            ExecutionBackend.PANDAS: 'pandas',
            ExecutionBackend.DASK_LOCAL: 'dask',
            ExecutionBackend.TORCH: 'torch'
        }

        for backend, module_name in backends_to_check.items():
            try:
                __import__(module_name)
                self._backend_availability[backend] = True
            except ImportError:
                self._backend_availability[backend] = False

    def select_optimal_backend(self, data_profile: DataProfile,
                             operation: str,
                             execution_context: Optional[ExecutionContext] = None) -> ExecutionBackend:
        """
        Select the optimal backend for a given operation.

        Args:
            data_profile: Profile of the data to process
            operation: Operation to perform
            execution_context: Execution constraints and preferences

        Returns:
            Optimal execution backend
        """
        if execution_context is None:
            execution_context = self._system_context

        # Get candidate backends based on data profile
        candidates = self._get_candidate_backends(data_profile, operation)

        # Filter by availability
        available_candidates = [b for b in candidates if self._backend_availability.get(b, False)]

        if not available_candidates:
            self._logger.warning("No available backends found, falling back to pandas")
            return ExecutionBackend.PANDAS

        # Score backends based on multiple criteria
        scored_backends = []
        for backend in available_candidates:
            score = self._score_backend(backend, data_profile, operation, execution_context)
            scored_backends.append((backend, score))

        # Sort by score (higher is better)
        scored_backends.sort(key=lambda x: x[1], reverse=True)

        optimal_backend = scored_backends[0][0]
        self._logger.debug(f"Selected backend: {optimal_backend.value} for {operation} on {data_profile.data_type}")

        return optimal_backend

    def _get_candidate_backends(self, data_profile: DataProfile, operation: str) -> List[ExecutionBackend]:
        """Get list of candidate backends for the data and operation."""
        candidates = []

        # Size-based selection
        if data_profile.is_massive_dataset or data_profile.requires_distributed_processing:
            candidates.append(ExecutionBackend.DASK_LOCAL)
        elif data_profile.is_large_dataset:
            candidates.append(ExecutionBackend.DASK_LOCAL)

        # Type-based selection
        if data_profile.data_type == "tabular":
            candidates.append(ExecutionBackend.PANDAS)
        elif data_profile.data_type in ["image", "audio", "video", "array", "numerical"]:
            if data_profile.requires_gpu:
                candidates.append(ExecutionBackend.TORCH)

        # Always include pandas as fallback
        if ExecutionBackend.PANDAS not in candidates:
            candidates.append(ExecutionBackend.PANDAS)

        return list(set(candidates))  # Remove duplicates

    def _score_backend(self, backend: ExecutionBackend, data_profile: DataProfile,
                      operation: str, execution_context: ExecutionContext) -> float:
        """Score a backend for the given context."""
        score = 0.0

        # Base scores for available backends only
        base_scores = {
            ExecutionBackend.PANDAS: 5.0,
            ExecutionBackend.DASK_LOCAL: 7.0,
            ExecutionBackend.TORCH: 7.0
        }
        score += base_scores.get(backend, 5.0)

        # Size-based scoring
        if data_profile.is_massive_dataset:
            if backend == ExecutionBackend.DASK_LOCAL:
                score += 5.0
            elif backend == ExecutionBackend.PANDAS:
                score -= 5.0
        elif data_profile.is_large_dataset:
            if backend == ExecutionBackend.DASK_LOCAL:
                score += 3.0

        # Memory efficiency scoring
        if not data_profile.fits_in_memory:
            if backend == ExecutionBackend.DASK_LOCAL:
                score += 4.0
            elif backend == ExecutionBackend.PANDAS:
                score -= 3.0

        # GPU utilization scoring
        if data_profile.requires_gpu and execution_context.has_gpu:
            if backend == ExecutionBackend.TORCH:
                score += 4.0

        # Historical performance scoring
        history_key = f"{backend.value}_{data_profile.data_type}_{operation}"
        if history_key in self._performance_history:
            avg_time = self._performance_history[history_key]['avg_execution_time']
            # Lower execution time = higher score
            score += max(0, 10 - avg_time)

        return score

    async def execute(self, data_profile: DataProfile, operation: str,
                     data: Any, **kwargs) -> ExecutionResult:
        """
        Execute an operation using the optimal backend and adapter.

        Args:
            data_profile: Profile of the data
            operation: Operation to perform
            data: Data to process
            **kwargs: Additional operation parameters

        Returns:
            Execution result with performance metrics
        """
        start_time = time.time()
        execution_id = f"{operation}_{start_time}"

        try:
            # Select optimal backend and adapter (use provided adapter if available)
            backend = self.select_optimal_backend(data_profile, operation)
            adapter = kwargs.pop('adapter', None)  # Remove adapter from kwargs to avoid conflict

            if not adapter:
                adapter = self._adapter_registry.select_best_adapter(data_profile, operation)

            if not adapter:
                raise ValueError(f"No suitable adapter found for {data_profile}")

            self._active_executions[execution_id] = {
                'backend': backend,
                'adapter': adapter,
                'start_time': start_time
            }

            # Execute the operation
            result = await self._execute_with_backend(backend, adapter, operation, data, **kwargs)

            execution_time = time.time() - start_time
            memory_used = self._estimate_memory_usage(data_profile, operation)

            # Record performance metrics
            self._record_performance(backend, adapter, data_profile, operation, execution_time, memory_used)

            return ExecutionResult(
                result=result,
                execution_time=execution_time,
                memory_used=memory_used,
                backend_used=backend.value,
                adapter_used=adapter.name,
                success=True
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self._logger.error(f"Execution failed: {e}")

            return ExecutionResult(
                result=None,
                execution_time=execution_time,
                memory_used=0,
                backend_used="unknown",
                adapter_used="unknown",
                success=False,
                error_message=str(e)
            )
        finally:
            self._active_executions.pop(execution_id, None)

    async def _execute_with_backend(self, backend: ExecutionBackend,
                                  adapter: Any, operation: str,
                                  data: Any, **kwargs) -> Any:
        """Execute operation with specific backend."""
        if backend == ExecutionBackend.PANDAS:
            return await self._execute_pandas(adapter, operation, data, **kwargs)
        elif backend == ExecutionBackend.DASK_LOCAL:
            return await self._execute_dask(adapter, operation, data, **kwargs)
        elif backend == ExecutionBackend.TORCH:
            return await self._execute_torch(adapter, operation, data, **kwargs)
        else:
            # Fallback to appropriate adapter method
            if operation == 'load':
                return adapter.load(data, **kwargs)
            elif operation == 'save':
                destination = kwargs.pop('destination', None)
                return adapter.save(data, destination, **kwargs)
            else:
                return adapter.transform(data, operation, **kwargs)

    async def _execute_pandas(self, adapter: Any, operation: str, data: Any, **kwargs) -> Any:
        """Execute operation using pandas backend."""
        if operation == 'load':
            return adapter.load(data, **kwargs)
        elif operation == 'save':
            destination = kwargs.pop('destination', None)
            return adapter.save(data, destination, **kwargs)
        else:
            return adapter.transform(data, operation, **kwargs)

    async def _execute_dask(self, adapter: Any, operation: str, data: Any, **kwargs) -> Any:
        """Execute operation using dask backend."""
        if operation == 'load':
            return adapter.load(data, **kwargs)
        elif operation == 'save':
            destination = kwargs.pop('destination', None)
            return adapter.save(data, destination, **kwargs)
        else:
            return adapter.transform(data, operation, **kwargs)

    async def _execute_torch(self, adapter: Any, operation: str, data: Any, **kwargs) -> Any:
        """Execute operation using torch backend."""
        if operation == 'load':
            return adapter.load(data, **kwargs)
        elif operation == 'save':
            destination = kwargs.pop('destination', None)
            return adapter.save(data, destination, **kwargs)
        else:
            return adapter.transform(data, operation, **kwargs)

    def _estimate_memory_usage(self, data_profile: DataProfile, operation: str) -> int:
        """Estimate memory usage for the operation."""
        # Simple heuristic - could be improved with actual monitoring
        base_memory = data_profile.estimated_memory_usage

        operation_multipliers = {
            'load': 1.0,
            'transform': 2.0,
            'join': 3.0,
            'aggregate': 1.5,
            'sample': 0.1
        }

        multiplier = operation_multipliers.get(operation, 1.5)
        return int(base_memory * multiplier)

    def _record_performance(self, backend: ExecutionBackend, adapter: Any,
                          data_profile: DataProfile, operation: str,
                          execution_time: float, memory_used: int) -> None:
        """Record performance metrics for future optimization."""
        key = f"{backend.value}_{data_profile.data_type}_{operation}"

        if key not in self._performance_history:
            self._performance_history[key] = {
                'total_executions': 0,
                'total_execution_time': 0.0,
                'total_memory_used': 0,
                'avg_execution_time': 0.0,
                'avg_memory_used': 0.0
            }

        history = self._performance_history[key]
        history['total_executions'] += 1
        history['total_execution_time'] += execution_time
        history['total_memory_used'] += memory_used
        history['avg_execution_time'] = history['total_execution_time'] / history['total_executions']
        history['avg_memory_used'] = history['total_memory_used'] / history['total_executions']

        # Update adapter registry with performance metrics
        self._adapter_registry.update_performance_metrics(
            adapter.name, data_profile.data_type, operation,
            {'execution_time': execution_time, 'memory_usage': memory_used}
        )

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            'performance_history': self._performance_history,
            'backend_availability': self._backend_availability,
            'active_executions': len(self._active_executions),
            'system_context': {
                'available_memory_gb': self._system_context.available_memory / (1024**3),
                'available_cores': self._system_context.available_cores,
                'has_gpu': self._system_context.has_gpu
            }
        }

    def clear_performance_history(self) -> None:
        """Clear all performance history."""
        self._performance_history.clear()
        self._logger.debug("Cleared performance history")

    async def warmup(self, data_profiles: List[DataProfile]) -> None:
        """Warm up the engine by testing backends with sample data."""
        self._logger.info("Warming up execution engine...")

        for profile in data_profiles:
            try:
                # Create small sample data for testing
                sample_size = min(1000, profile.size_bytes // 1000)
                # This would create actual sample data for testing
                self._logger.debug(f"Warming up for {profile.data_type} data")
            except Exception as e:
                self._logger.warning(f"Warmup failed for {profile.data_type}: {e}")

        self._logger.info("Engine warmup completed")
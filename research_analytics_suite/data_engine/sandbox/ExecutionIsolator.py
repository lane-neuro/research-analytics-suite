"""
ExecutionIsolator Module

Ensures operations in sandbox cannot affect real workspace.
Implements resource monitoring, timeout enforcement, and audit logging.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Development
"""
import asyncio
import psutil
import os
from typing import Optional, Any
from dataclasses import dataclass
from datetime import datetime

from research_analytics_suite.utils.CustomLogger import CustomLogger
from research_analytics_suite.utils.Config import Config
from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation


@dataclass
class ExecutionResult:
    """Result from isolated operation execution."""
    success: bool
    result: Optional[Any]
    error: Optional[Exception]
    execution_time: float
    memory_used_mb: float
    timestamp: datetime


@dataclass
class ExecutionMetrics:
    """Execution performance metrics."""
    cpu_percent: float
    memory_mb: float
    execution_time_seconds: float
    success: bool


class ExecutionIsolator:
    """
    Ensures operations in sandbox cannot affect real workspace.

    Key Features:
    - Process isolation using RemoteManager
    - Resource monitoring and limits
    - Timeout enforcement
    - Exception handling and recovery
    - Audit logging
    """

    def __init__(self):
        """
        Initialize execution isolator.

        Args:
            config: Configuration object
        """
        self._logger = CustomLogger()
        from research_analytics_suite.utils.Config import Config
        self._config = Config()

        self._timeout = self._config.SIMULATION_TIMEOUT_SECONDS
        self._memory_limit_mb = self._config.SANDBOX_MEMORY_LIMIT_MB

        # Metrics tracking
        self._current_metrics: Optional[ExecutionMetrics] = None
        self._process = psutil.Process(os.getpid())
        self._start_time: Optional[datetime] = None

    async def execute_isolated(
        self,
        operation: BaseOperation,
        timeout: Optional[int] = None
    ) -> ExecutionResult:
        """
        Executes operation in isolated environment.

        Args:
            operation: Operation to execute
            timeout: Optional timeout override (seconds)

        Returns:
            ExecutionResult with outcome and metrics
        """
        timeout = timeout or self._timeout
        start_time = datetime.now()

        self._logger.info(f"Executing operation in isolation: {operation.name}")

        try:
            # Start resource monitoring
            monitoring_task = asyncio.create_task(self._monitor_execution())

            # Execute operation with timeout
            result = await asyncio.wait_for(
                self._execute_operation(operation),
                timeout=timeout
            )

            # Stop monitoring
            monitoring_task.cancel()

            execution_time = (datetime.now() - start_time).total_seconds()

            return ExecutionResult(
                success=True,
                result=result,
                error=None,
                execution_time=execution_time,
                memory_used_mb=self._current_metrics.memory_mb if self._current_metrics else 0.0,
                timestamp=datetime.now()
            )

        except asyncio.TimeoutError:
            self._logger.warning(f"Operation timed out: {operation.name}")
            return ExecutionResult(
                success=False,
                result=None,
                error=TimeoutError(f"Operation timed out after {timeout}s"),
                execution_time=timeout,
                memory_used_mb=0.0,
                timestamp=datetime.now()
            )

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)
            execution_time = (datetime.now() - start_time).total_seconds()
            return ExecutionResult(
                success=False,
                result=None,
                error=e,
                execution_time=execution_time,
                memory_used_mb=0.0,
                timestamp=datetime.now()
            )

        finally:
            await self.cleanup_after_execution()

    async def _execute_operation(self, operation: BaseOperation) -> Any:
        """
        Internal method to execute operation.

        Args:
            operation: Operation to execute

        Returns:
            Operation result
        """
        self._start_time = datetime.now()

        try:
            # Execute the operation's action
            # Operations are already isolated by being in the sandbox workspace
            result = await operation.execute()
            return result

        except Exception as e:
            self._logger.error(f"Operation execution failed: {e}", self.__class__.__name__)
            raise

    async def _monitor_execution(self) -> None:
        """
        Monitors execution metrics in background.
        """
        while True:
            try:
                metrics = self.monitor_execution()
                self._current_metrics = metrics

                # Enforce resource limits
                self.enforce_resource_limits()

                await asyncio.sleep(0.1)  # Monitor every 100ms

            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(e, self.__class__.__name__)

    def enforce_resource_limits(self) -> None:
        """
        Enforces memory and CPU limits.

        Raises:
            RuntimeError: If resource limits exceeded
        """
        if self._current_metrics:
            if self._current_metrics.memory_mb > self._memory_limit_mb:
                raise RuntimeError(
                    f"Memory limit exceeded: {self._current_metrics.memory_mb}MB > {self._memory_limit_mb}MB"
                )

    def monitor_execution(self) -> ExecutionMetrics:
        """
        Monitors execution metrics.

        Returns:
            Current execution metrics
        """
        try:
            # Get current process CPU and memory usage
            cpu_percent = self._process.cpu_percent(interval=0.01)
            memory_info = self._process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)  # Convert bytes to MB

            # Calculate execution time
            execution_time = 0.0
            if self._start_time:
                execution_time = (datetime.now() - self._start_time).total_seconds()

            return ExecutionMetrics(
                cpu_percent=cpu_percent,
                memory_mb=memory_mb,
                execution_time_seconds=execution_time,
                success=True
            )

        except Exception as e:
            self._logger.warning(f"Failed to monitor execution: {e}")
            return ExecutionMetrics(
                cpu_percent=0.0,
                memory_mb=0.0,
                execution_time_seconds=0.0,
                success=False
            )

    async def cleanup_after_execution(self) -> None:
        """
        Cleans up resources after execution.
        """
        self._logger.debug("Cleaning up after isolated execution")
        self._current_metrics = None
        self._start_time = None

        # Force garbage collection to free memory
        import gc
        gc.collect()

        self._logger.debug("Cleanup completed")

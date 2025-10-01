"""
BaseAdapter Module

Defines the universal adapter interface for handling any data type.
All specific adapters must implement this interface.

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

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Iterator, Tuple
from pathlib import Path

from research_analytics_suite.data_engine.core.DataProfile import DataProfile


class BaseAdapter(ABC):
    """
    Universal adapter interface for any data type.

    This base class defines the contract that all adapters must implement
    to enable universal data processing capabilities.
    """

    def __init__(self, name: str, supported_formats: List[str],
                 supported_data_types: List[str]):
        """
        Initialize the adapter.

        Args:
            name: Adapter name
            supported_formats: List of file formats this adapter handles
            supported_data_types: List of data types this adapter handles
        """
        self.name = name
        self.supported_formats = supported_formats
        self.supported_data_types = supported_data_types

    @abstractmethod
    def can_handle(self, data_profile: DataProfile) -> bool:
        """
        Check if this adapter can handle the given data profile.

        Args:
            data_profile: Profile of the data to check

        Returns:
            True if this adapter can handle the data
        """
        pass

    @abstractmethod
    def load(self, source: Union[str, Path, Any], **kwargs) -> Any:
        """
        Load data from source.

        Args:
            source: Data source (file path, URL, or data object)
            **kwargs: Additional loading parameters

        Returns:
            Loaded data in adapter's native format
        """
        pass

    @abstractmethod
    def save(self, data: Any, destination: Union[str, Path], **kwargs) -> bool:
        """
        Save data to destination.

        Args:
            data: Data to save
            destination: Where to save the data
            **kwargs: Additional saving parameters

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def transform(self, data: Any, operation: str, **kwargs) -> Any:
        """
        Apply transformation to data.

        Args:
            data: Data to transform
            operation: Name of the operation
            **kwargs: Operation parameters

        Returns:
            Transformed data
        """
        pass

    @abstractmethod
    def get_schema(self, data: Any) -> Dict[str, Any]:
        """
        Get schema information for the data.

        Args:
            data: Data to analyze

        Returns:
            Schema information
        """
        pass

    @abstractmethod
    def get_sample(self, data: Any, size: int = 1000) -> Any:
        """
        Get a sample of the data.

        Args:
            data: Data to sample
            size: Sample size

        Returns:
            Data sample
        """
        pass

    @abstractmethod
    def iterate_chunks(self, data: Any, chunk_size: int) -> Iterator[Any]:
        """
        Iterate over data in chunks.

        Args:
            data: Data to iterate
            chunk_size: Size of each chunk

        Yields:
            Data chunks
        """
        pass

    @abstractmethod
    def get_size_info(self, data: Any) -> Dict[str, Any]:
        """
        Get size information about the data.

        Args:
            data: Data to analyze

        Returns:
            Size information (rows, columns, bytes, etc.)
        """
        pass

    @abstractmethod
    def to_arrow(self, data: Any) -> Any:
        """
        Convert data to Apache Arrow format for zero-copy sharing.

        Args:
            data: Data to convert

        Returns:
            Arrow table/array
        """
        pass

    @abstractmethod
    def from_arrow(self, arrow_data: Any) -> Any:
        """
        Convert from Apache Arrow format to adapter's native format.

        Args:
            arrow_data: Arrow table/array

        Returns:
            Data in adapter's native format
        """
        pass

    def validate_data(self, data: Any) -> bool:
        """
        Validate that the data is in expected format.

        Args:
            data: Data to validate

        Returns:
            True if valid
        """
        try:
            self.get_schema(data)
            return True
        except Exception:
            return False

    def _detect_header_rows(self, file_path: Union[str, Path], max_rows: int = 10,
                           delimiter: str = ',') -> Optional[List[int]]:
        """
        Detect multi-level headers in tabular files (e.g., DeepLabCut datasets).

        Args:
            file_path: Path to the file
            max_rows: Maximum rows to analyze (default: 10)
            delimiter: Column delimiter (default: ',')

        Returns:
            List of header row indices (e.g., [0, 1, 2]) or None if single-level
        """
        try:
            import csv
            from collections import Counter

            file_path = Path(file_path)
            if not file_path.exists():
                return None

            # Read first max_rows without parsing
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.reader(f, delimiter=delimiter)
                rows = []
                for i, row in enumerate(reader):
                    if i >= max_rows:
                        break
                    rows.append(row)

            if len(rows) < 2:
                return None

            def is_numeric(cell):
                try:
                    float(cell.replace(',', ''))
                    return True
                except (ValueError, AttributeError):
                    return False

            def is_data_row(row):
                if len(row) < 2:
                    return False
                non_empty = [cell.strip() for cell in row if cell.strip()]
                if not non_empty:
                    return False
                numeric_count = sum(1 for cell in non_empty if is_numeric(cell))
                return numeric_count >= max(2, len(non_empty) * 0.3)

            header_candidates = 0
            for row in rows:
                if not is_data_row(row):
                    header_candidates += 1
                else:
                    break

            if header_candidates <= 1 or header_candidates > 5:
                return None

            header_rows = rows[:header_candidates]

            non_numeric_counts = []
            for row in header_rows:
                non_empty = [cell.strip() for cell in row if cell.strip()]
                non_numeric_count = sum(1 for cell in non_empty if not is_numeric(cell))
                non_numeric_counts.append(non_numeric_count)

            avg_non_numeric = sum(non_numeric_counts) / len(non_numeric_counts) if non_numeric_counts else 0
            if avg_non_numeric < 2:
                return None

            repetition_scores = []

            for row in header_rows:
                non_empty = [cell.strip() for cell in row if cell.strip()]
                if not non_empty:
                    continue
                counts = Counter(non_empty)
                # Score based on ratio of repeated values
                repeated = sum(count for count in counts.values() if count > 1)
                score = repeated / len(non_empty) if non_empty else 0
                repetition_scores.append(score)

            if len(repetition_scores) >= 2 and any(score > 0.2 for score in repetition_scores[:2]):
                return list(range(header_candidates))

            empty_pattern = False
            for row in header_rows[1:]:
                empty_count = sum(1 for cell in row if not cell.strip())
                if empty_count > len(row) * 0.3:
                    empty_pattern = True
                    break

            if empty_pattern and header_candidates >= 2:
                return list(range(header_candidates))

            return None

        except Exception:
            return None

    def optimize_for_profile(self, data_profile: DataProfile) -> Dict[str, Any]:
        """
        Get optimization settings for the given data profile.

        Args:
            data_profile: Profile of the data

        Returns:
            Optimization settings
        """
        optimizations = {}

        if data_profile.is_large_dataset:
            optimizations['use_chunking'] = True
            # Calculate optimal chunk size based on available memory
            optimizations['chunk_size'] = min(1000000, data_profile.size_bytes // (100 * 1024 * 1024))

        if not data_profile.fits_in_memory:
            optimizations['use_lazy_loading'] = True
            optimizations['memory_map'] = True

        if data_profile.requires_distributed_processing:
            optimizations['use_distributed'] = True

        return optimizations

    def get_recommended_operations(self, data_profile: DataProfile) -> List[str]:
        """
        Get list of recommended operations for this data type and profile.

        Args:
            data_profile: Profile of the data

        Returns:
            List of operation names
        """
        operations = ['load', 'save', 'sample', 'schema']

        if data_profile.data_type == "tabular":
            operations.extend(['filter', 'group_by', 'aggregate', 'join'])
        elif data_profile.data_type == "time_series":
            operations.extend(['resample', 'interpolate', 'forecast'])
        elif data_profile.data_type == "image":
            operations.extend(['resize', 'crop', 'enhance', 'detect'])
        elif data_profile.data_type == "text":
            operations.extend(['tokenize', 'embed', 'classify', 'summarize'])

        return operations

    def estimate_memory_usage(self, operation: str, data_profile: DataProfile) -> int:
        """
        Estimate memory usage for an operation.

        Args:
            operation: Operation name
            data_profile: Profile of the data

        Returns:
            Estimated memory usage in bytes
        """
        base_memory = data_profile.estimated_memory_usage

        # Operation-specific multipliers
        memory_multipliers = {
            'load': 1.0,
            'transform': 2.0,
            'join': 3.0,
            'aggregate': 1.5,
            'sample': 0.1
        }

        multiplier = memory_multipliers.get(operation, 1.5)
        return int(base_memory * multiplier)

    def __str__(self) -> str:
        return f"{self.name}Adapter(formats={self.supported_formats})"

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}(name='{self.name}', "
                f"formats={self.supported_formats}, "
                f"data_types={self.supported_data_types})")


class StreamingAdapter(BaseAdapter):
    """
    Specialized adapter for streaming data sources.
    """

    @abstractmethod
    def connect_stream(self, source: str, **kwargs) -> Any:
        """
        Connect to a streaming data source.

        Args:
            source: Stream source identifier
            **kwargs: Connection parameters

        Returns:
            Stream connection object
        """
        pass

    @abstractmethod
    def read_stream(self, stream: Any, timeout: Optional[float] = None) -> Any:
        """
        Read from stream.

        Args:
            stream: Stream connection
            timeout: Read timeout in seconds

        Returns:
            Stream data
        """
        pass

    @abstractmethod
    def write_stream(self, stream: Any, data: Any) -> bool:
        """
        Write to stream.

        Args:
            stream: Stream connection
            data: Data to write

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def close_stream(self, stream: Any) -> None:
        """
        Close stream connection.

        Args:
            stream: Stream connection to close
        """
        pass


class MLAdapter(BaseAdapter):
    """
    Specialized adapter for machine learning data and models.
    """

    @abstractmethod
    def to_tensor(self, data: Any, device: str = 'cpu') -> Any:
        """
        Convert data to tensor format.

        Args:
            data: Data to convert
            device: Target device ('cpu', 'cuda', etc.)

        Returns:
            Tensor data
        """
        pass

    @abstractmethod
    def create_dataloader(self, data: Any, batch_size: int,
                         shuffle: bool = True, **kwargs) -> Any:
        """
        Create a data loader for training/inference.

        Args:
            data: Training data
            batch_size: Batch size
            shuffle: Whether to shuffle data
            **kwargs: Additional parameters

        Returns:
            Data loader object
        """
        pass

    @abstractmethod
    def preprocess(self, data: Any, preprocessing_config: Dict[str, Any]) -> Any:
        """
        Apply preprocessing to data.

        Args:
            data: Raw data
            preprocessing_config: Preprocessing configuration

        Returns:
            Preprocessed data
        """
        pass
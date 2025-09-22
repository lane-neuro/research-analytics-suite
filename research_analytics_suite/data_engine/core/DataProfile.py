"""
DataProfile Module

Defines the DataProfile class that analyzes and describes data characteristics
to enable intelligent processing decisions.

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

import os
import sys
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from pathlib import Path

import psutil


@dataclass
class DataProfile:
    """
    Comprehensive data profile for intelligent processing decisions.

    Attributes:
        size_bytes: Data size in bytes
        estimated_memory_usage: Estimated memory usage for processing
        data_type: Primary data type classification
        format: Specific format (csv, json, parquet, etc.)
        schema: Data schema information
        characteristics: Additional data characteristics
        processing_hints: Suggested processing optimizations
        storage_location: Where the data is stored
        is_streaming: Whether data is a stream
        requires_gpu: Whether GPU processing would be beneficial
    """
    size_bytes: int = 0
    estimated_memory_usage: int = 0
    data_type: str = "unknown"
    format: str = "unknown"
    schema: Optional[Dict[str, Any]] = None
    characteristics: Dict[str, Any] = None
    processing_hints: List[str] = None
    storage_location: str = "local"
    is_streaming: bool = False
    requires_gpu: bool = False

    def __post_init__(self):
        if self.characteristics is None:
            self.characteristics = {}
        if self.processing_hints is None:
            self.processing_hints = []
        if self.schema is None:
            self.schema = {}

    @property
    def size_mb(self) -> float:
        """Size in megabytes."""
        return self.size_bytes / (1024 * 1024)

    @property
    def size_gb(self) -> float:
        """Size in gigabytes."""
        return self.size_bytes / (1024 * 1024 * 1024)

    @property
    def size_tb(self) -> float:
        """Size in terabytes."""
        return self.size_bytes / (1024 * 1024 * 1024 * 1024)

    @property
    def fits_in_memory(self) -> bool:
        """Check if data can fit in available memory."""
        available_memory = psutil.virtual_memory().available
        return self.estimated_memory_usage < available_memory * 0.8

    @property
    def is_large_dataset(self) -> bool:
        """Check if this is considered a large dataset (>1GB)."""
        return self.size_gb > 1.0

    @property
    def is_massive_dataset(self) -> bool:
        """Check if this is considered massive (>100GB)."""
        return self.size_gb > 100.0

    @property
    def requires_distributed_processing(self) -> bool:
        """Check if distributed processing would be beneficial."""
        return (self.is_massive_dataset or
                not self.fits_in_memory or
                'distributed' in self.processing_hints)

    @property
    def optimal_chunk_size(self) -> int:
        """Calculate optimal chunk size for processing."""
        if self.is_streaming:
            return 1024 * 1024  # 1MB for streams
        elif self.size_mb < 10:
            return self.size_bytes  # Process all at once
        elif self.size_mb < 100:
            return 10 * 1024 * 1024  # 10MB chunks
        elif self.size_gb < 1:
            return 100 * 1024 * 1024  # 100MB chunks
        else:
            return 1024 * 1024 * 1024  # 1GB chunks

    def has_sql_queries(self) -> bool:
        """Check if data would benefit from SQL-style queries."""
        return (self.data_type == "tabular" and
                (self.is_large_dataset or 'sql' in self.processing_hints))

    def suggest_backend(self) -> str:
        """Suggest optimal processing backend based on available backends."""
        if self.requires_gpu:
            return "torch"
        elif self.requires_distributed_processing:
            return "dask_local"
        elif self.is_large_dataset:
            return "dask_local"
        elif self.has_sql_queries():
            return "pandas"
        elif self.data_type == "time_series":
            return "pandas"
        else:
            return "pandas"

    def suggest_storage_strategy(self) -> str:
        """Suggest optimal storage strategy."""
        if self.is_streaming:
            return "streaming"
        elif not self.fits_in_memory:
            return "memory_mapped"
        elif self.size_mb > 100:
            return "chunked"
        else:
            return "in_memory"

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "DataProfile":
        """Create profile from file path."""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        size_bytes = file_path.stat().st_size
        format_ext = file_path.suffix.lower().lstrip('.')

        # Estimate memory usage (rough heuristic)
        estimated_memory = size_bytes * 3  # Conservative estimate

        # Determine data type from extension
        data_type = cls._classify_data_type(format_ext)

        # Determine storage location
        storage_location = "local"
        if str(file_path).startswith(('s3://', 'gs://', 'azure://', 'hdfs://')):
            storage_location = "cloud"

        profile = cls(
            size_bytes=size_bytes,
            estimated_memory_usage=estimated_memory,
            data_type=data_type,
            format=format_ext,
            storage_location=storage_location
        )

        # Add processing hints based on size and type
        profile._add_processing_hints()

        return profile

    @classmethod
    def from_data(cls, data: Any, data_type: str = None) -> "DataProfile":
        """Create profile from in-memory data."""
        size_bytes = sys.getsizeof(data)
        estimated_memory = size_bytes * 2  # Less overhead for in-memory data

        if data_type is None:
            data_type = cls._infer_data_type(data)

        profile = cls(
            size_bytes=size_bytes,
            estimated_memory_usage=estimated_memory,
            data_type=data_type,
            format="in_memory",
            storage_location="memory"
        )

        profile._add_processing_hints()
        return profile

    @staticmethod
    def _classify_data_type(format_ext: str) -> str:
        """Classify data type from file extension."""
        tabular_formats = {'csv', 'tsv', 'parquet', 'xlsx', 'xls', 'orc', 'feather'}
        time_series_formats = {'h5', 'hdf5', 'nc', 'netcdf'}
        image_formats = {'jpg', 'jpeg', 'png', 'tiff', 'bmp', 'gif'}
        audio_formats = {'wav', 'mp3', 'flac', 'aac', 'm4a'}
        video_formats = {'mp4', 'avi', 'mkv', 'mov', 'wmv'}
        text_formats = {'txt', 'md', 'json', 'xml', 'html'}

        if format_ext in tabular_formats:
            return "tabular"
        elif format_ext in time_series_formats:
            return "time_series"
        elif format_ext in image_formats:
            return "image"
        elif format_ext in audio_formats:
            return "audio"
        elif format_ext in video_formats:
            return "video"
        elif format_ext in text_formats:
            return "text"
        else:
            return "unknown"

    @staticmethod
    def _infer_data_type(data: Any) -> str:
        """Infer data type from data object."""
        import pandas as pd
        import numpy as np

        # Check specific types first
        if isinstance(data, dict):
            return "structured"
        elif isinstance(data, str):
            return "text"
        elif hasattr(data, 'columns'):  # DataFrame-like
            return "tabular"
        elif isinstance(data, (list, tuple, np.ndarray)):
            return "array"
        elif hasattr(data, '__iter__') and not isinstance(data, (str, bytes)):
            # Other iterable types (sets, etc.)
            return "array"
        else:
            return "scalar"

    def _add_processing_hints(self):
        """Add processing hints based on profile characteristics."""
        if self.is_massive_dataset:
            self.processing_hints.append("distributed")

        if self.data_type == "tabular" and self.is_large_dataset:
            self.processing_hints.append("sql")

        if self.data_type in ["image", "audio", "video"]:
            self.requires_gpu = True
            self.processing_hints.append("gpu_accelerated")

        if not self.fits_in_memory:
            self.processing_hints.append("memory_mapped")
            self.processing_hints.append("chunked_processing")

        if self.size_gb > 10:
            self.processing_hints.append("parallel_io")
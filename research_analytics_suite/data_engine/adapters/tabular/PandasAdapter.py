"""
PandasAdapter Module

Standard adapter for tabular data using pandas library.
Provides comprehensive functionality for most tabular data operations.

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
from typing import Any, Dict, List, Iterator, Union, Optional
from pathlib import Path

try:
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

from research_analytics_suite.data_engine.adapters.BaseAdapter import BaseAdapter
from research_analytics_suite.data_engine.core.DataProfile import DataProfile
from research_analytics_suite.utils.CustomLogger import CustomLogger


class PandasAdapter(BaseAdapter):
    """
    Standard adapter for tabular data using pandas.

    Pandas provides comprehensive functionality for data manipulation
    and is the most widely used data processing library in Python.
    """

    def __init__(self):
        """Initialize the Pandas adapter."""
        if not PANDAS_AVAILABLE:
            raise ImportError("Pandas not available. Install with: pip install pandas pyarrow")

        super().__init__(
            name="pandas",
            supported_formats=['csv', 'tsv', 'xlsx', 'xls', 'json', 'parquet', 'pickle', 'feather', 'html', 'in_memory'],
            supported_data_types=['tabular']
        )
        self._logger = CustomLogger()

    def can_handle(self, data_profile: DataProfile) -> bool:
        """
        Check if this adapter can handle the given data profile.

        Args:
            data_profile: Profile of the data to check

        Returns:
            True if this adapter can handle the data
        """
        # Pandas can handle most tabular data, but may not be optimal for very large datasets
        if data_profile.data_type != "tabular":
            return False

        # Check format support
        if data_profile.format not in self.supported_formats:
            return False

        # Pandas is not ideal for very large datasets (>2GB)
        if data_profile.size_bytes > 2 * 1024 * 1024 * 1024:  # 2GB
            return False

        return True

    def load(self, source: Union[str, Path, Any], **kwargs) -> pd.DataFrame:
        """
        Load data from source.

        Args:
            source: Data source (file path, URL, or data object)
            **kwargs: Additional loading parameters

        Returns:
            Loaded data as pandas DataFrame
        """
        if isinstance(source, (str, Path)):
            source_path = Path(source)
            file_ext = source_path.suffix.lower().lstrip('.')

            # Auto-detect multi-level headers if not explicitly provided
            if file_ext in ['csv', 'tsv'] and 'header' not in kwargs:
                delimiter = '\t' if file_ext == 'tsv' else ','
                detected_headers = self._detect_header_rows(source_path, delimiter=delimiter)
                if detected_headers:
                    kwargs['header'] = detected_headers
                    self._logger.info(f"Detected multi-level headers: {detected_headers}")

            if file_ext == 'csv':
                return pd.read_csv(source, **kwargs)
            elif file_ext == 'tsv':
                return pd.read_csv(source, sep='\t', **kwargs)
            elif file_ext in ['xlsx', 'xls']:
                return pd.read_excel(source, **kwargs)
            elif file_ext == 'json':
                return pd.read_json(source, **kwargs)
            elif file_ext == 'parquet':
                return pd.read_parquet(source, **kwargs)
            elif file_ext == 'pickle':
                return pd.read_pickle(source, **kwargs)
            elif file_ext == 'feather':
                return pd.read_feather(source, **kwargs)
            elif file_ext == 'html':
                tables = pd.read_html(source, **kwargs)
                return tables[0] if tables else pd.DataFrame()
            else:
                # Try CSV as default
                return pd.read_csv(source, **kwargs)
        elif isinstance(source, pd.DataFrame):
            return source.copy()
        else:
            raise ValueError(f"Unsupported source type: {type(source)}")

    def save(self, data: pd.DataFrame, destination: Union[str, Path], **kwargs) -> bool:
        """
        Save data to destination.

        Args:
            data: Data to save
            destination: Where to save the data
            **kwargs: Additional saving parameters

        Returns:
            True if successful
        """
        try:
            dest_path = Path(destination)
            file_ext = dest_path.suffix.lower().lstrip('.')

            # Create directory if it doesn't exist
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            if file_ext == 'csv':
                data.to_csv(destination, index=False, **kwargs)
            elif file_ext == 'tsv':
                data.to_csv(destination, sep='\t', index=False, **kwargs)
            elif file_ext in ['xlsx', 'xls']:
                data.to_excel(destination, index=False, **kwargs)
            elif file_ext == 'json':
                data.to_json(destination, **kwargs)
            elif file_ext == 'parquet':
                data.to_parquet(destination, **kwargs)
            elif file_ext == 'pickle':
                data.to_pickle(destination, **kwargs)
            elif file_ext == 'feather':
                data.to_feather(destination, **kwargs)
            else:
                # Default to CSV
                data.to_csv(destination, index=False, **kwargs)

            return True
        except Exception as e:
            self._logger.error(f"Failed to save data: {e}")
            return False

    def transform(self, data: pd.DataFrame, operation: str, **kwargs) -> pd.DataFrame:
        """
        Apply transformation to data.

        Args:
            data: Data to transform
            operation: Name of the operation
            **kwargs: Operation parameters

        Returns:
            Transformed data
        """
        if operation == 'load':
            # For load operation, data is actually the source path
            return self.load(data, **kwargs)
        elif operation == 'filter':
            condition = kwargs.get('condition')
            if condition:
                return data.query(condition)
            return data

        elif operation == 'group_by':
            columns = kwargs.get('columns', [])
            agg_func = kwargs.get('agg_func', 'mean')
            if columns:
                return data.groupby(columns).agg(agg_func)
            return data

        elif operation == 'sort':
            columns = kwargs.get('columns', [])
            ascending = kwargs.get('ascending', True)
            if columns:
                return data.sort_values(columns, ascending=ascending)
            return data

        elif operation == 'sample':
            n = kwargs.get('n', 1000)
            frac = kwargs.get('frac')
            if frac:
                return data.sample(frac=frac)
            return data.sample(n=min(n, len(data)))

        elif operation == 'drop_duplicates':
            return data.drop_duplicates()

        elif operation == 'fillna':
            value = kwargs.get('value', 0)
            method = kwargs.get('method')
            if method:
                return data.fillna(method=method)
            return data.fillna(value)

        elif operation == 'select_columns':
            columns = kwargs.get('columns', [])
            if columns:
                available_cols = [col for col in columns if col in data.columns]
                return data[available_cols]
            return data

        elif operation == 'filter_rows':
            condition = kwargs.get('condition')
            if condition:
                try:
                    return data.query(condition)
                except Exception as e:
                    self._logger.warning(f"Failed to apply filter condition '{condition}': {e}")
                    return data
            return data

        elif operation == 'slice_rows':
            start_row = kwargs.get('start_row', 0)
            end_row = kwargs.get('end_row')
            if end_row is not None:
                return data.iloc[start_row:end_row]
            elif start_row > 0:
                return data.iloc[start_row:]
            return data

        else:
            self._logger.warning(f"Unknown operation: {operation}")
            return data

    def get_schema(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Get schema information for the data.

        Args:
            data: Data to analyze

        Returns:
            Schema information
        """
        return {
            'columns': list(data.columns),
            'dtypes': data.dtypes.to_dict(),
            'shape': data.shape,
            'memory_usage': data.memory_usage(deep=True).sum(),
            'null_counts': data.isnull().sum().to_dict(),
            'numeric_columns': list(data.select_dtypes(include=['number']).columns),
            'categorical_columns': list(data.select_dtypes(include=['category']).columns),
            'datetime_columns': list(data.select_dtypes(include=['datetime']).columns),
        }

    def get_sample(self, data: pd.DataFrame, size: int = 1000) -> pd.DataFrame:
        """
        Get a sample of the data.

        Args:
            data: Data to sample
            size: Sample size

        Returns:
            Data sample
        """
        if len(data) <= size:
            return data.copy()
        return data.sample(n=size)

    def iterate_chunks(self, data: pd.DataFrame, chunk_size: int) -> Iterator[pd.DataFrame]:
        """
        Iterate over data in chunks.

        Args:
            data: Data to iterate
            chunk_size: Size of each chunk

        Yields:
            Data chunks
        """
        total_rows = len(data)
        for start in range(0, total_rows, chunk_size):
            end = min(start + chunk_size, total_rows)
            yield data.iloc[start:end]

    def get_size_info(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Get size information about the data.

        Args:
            data: Data to analyze

        Returns:
            Size information
        """
        memory_usage = data.memory_usage(deep=True)
        return {
            'rows': len(data),
            'columns': len(data.columns),
            'total_memory_bytes': memory_usage.sum(),
            'memory_per_column': memory_usage.to_dict(),
            'estimated_disk_size_csv': len(data) * len(data.columns) * 10,  # Rough estimate
        }

    def to_arrow(self, data: pd.DataFrame) -> pa.Table:
        """
        Convert data to Apache Arrow format.

        Args:
            data: Data to convert

        Returns:
            Arrow table
        """
        return pa.Table.from_pandas(data)

    def from_arrow(self, arrow_data: pa.Table) -> pd.DataFrame:
        """
        Convert from Apache Arrow format to pandas DataFrame.

        Args:
            arrow_data: Arrow table

        Returns:
            pandas DataFrame
        """
        return arrow_data.to_pandas()

    def optimize_for_profile(self, data_profile: DataProfile) -> Dict[str, Any]:
        """
        Get optimization settings for pandas operations.

        Args:
            data_profile: Profile of the data

        Returns:
            Optimization settings
        """
        optimizations = super().optimize_for_profile(data_profile)

        # Pandas-specific optimizations
        if data_profile.size_bytes > 100 * 1024 * 1024:  # 100MB
            optimizations['use_categorical'] = True
            optimizations['use_sparse'] = True

        # Check for duplicates hint in characteristics
        if data_profile.characteristics.get('has_many_duplicates', False):
            optimizations['drop_duplicates_early'] = True

        return optimizations
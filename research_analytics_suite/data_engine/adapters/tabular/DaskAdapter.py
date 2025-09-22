"""
DaskAdapter Module

Distributed processing adapter for large tabular data using Dask.
Essential for scalability with datasets that don't fit in memory.

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
    import dask
    import dask.dataframe as dd
    import pyarrow as pa
    import pandas as pd
    DASK_AVAILABLE = True
except ImportError:
    DASK_AVAILABLE = False

from research_analytics_suite.data_engine.adapters.BaseAdapter import BaseAdapter
from research_analytics_suite.data_engine.core.DataProfile import DataProfile
from research_analytics_suite.utils.CustomLogger import CustomLogger


class DaskAdapter(BaseAdapter):
    """
    Distributed processing adapter for large tabular data using Dask.

    Dask enables out-of-core processing and distributed computing,
    making it essential for datasets larger than memory.
    """

    def __init__(self):
        """Initialize the Dask adapter."""
        if not DASK_AVAILABLE:
            raise ImportError("Dask not available but is required for scalability")

        super().__init__(
            name="dask",
            supported_formats=['csv', 'tsv', 'parquet', 'json'],
            supported_data_types=['tabular', 'large_tabular']
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
        if data_profile.data_type not in ["tabular", "large_tabular"]:
            return False

        if data_profile.format not in self.supported_formats:
            return False

        # Dask is preferred for large datasets (>100MB) or when distributed processing is needed
        return (data_profile.size_bytes > 100 * 1024 * 1024 or
                data_profile.requires_distributed_processing or
                not data_profile.fits_in_memory)

    def load(self, source: Union[str, Path, Any], **kwargs) -> dd.DataFrame:
        """
        Load data from source as Dask DataFrame.

        Args:
            source: Data source (file path, URL, or data object)
            **kwargs: Additional loading parameters

        Returns:
            Loaded data as Dask DataFrame
        """
        if isinstance(source, (str, Path)):
            source_path = Path(source)
            file_ext = source_path.suffix.lower().lstrip('.')

            if file_ext == 'csv':
                return dd.read_csv(source, **kwargs)
            elif file_ext == 'tsv':
                return dd.read_csv(source, sep='\t', **kwargs)
            elif file_ext == 'parquet':
                return dd.read_parquet(source, **kwargs)
            elif file_ext == 'json':
                return dd.read_json(source, **kwargs)
            else:
                # Default to CSV
                return dd.read_csv(source, **kwargs)
        elif isinstance(source, dd.DataFrame):
            return source
        elif isinstance(source, pd.DataFrame):
            return dd.from_pandas(source, npartitions=4)
        else:
            raise ValueError(f"Unsupported source type: {type(source)}")

    def save(self, data: dd.DataFrame, destination: Union[str, Path], **kwargs) -> bool:
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
                data.to_csv(str(dest_path).replace('.csv', '*.csv'), **kwargs)
            elif file_ext == 'tsv':
                data.to_csv(str(dest_path).replace('.tsv', '*.tsv'), sep='\t', **kwargs)
            elif file_ext == 'parquet':
                data.to_parquet(destination, **kwargs)
            elif file_ext == 'json':
                data.to_json(str(dest_path).replace('.json', '*.json'), **kwargs)
            else:
                # Default to parquet for efficiency
                data.to_parquet(destination, **kwargs)

            return True
        except Exception as e:
            self._logger.error(f"Failed to save data: {e}")
            return False

    def transform(self, data: dd.DataFrame, operation: str, **kwargs) -> dd.DataFrame:
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
            if columns:
                return data.set_index(columns[0]).sort_index()
            return data

        elif operation == 'sample':
            frac = kwargs.get('frac', 0.1)
            return data.sample(frac=frac)

        elif operation == 'drop_duplicates':
            return data.drop_duplicates()

        elif operation == 'fillna':
            value = kwargs.get('value', 0)
            return data.fillna(value)

        elif operation == 'select_columns':
            columns = kwargs.get('columns', [])
            if columns:
                return data[columns]
            return data

        elif operation == 'repartition':
            npartitions = kwargs.get('npartitions', 4)
            return data.repartition(npartitions=npartitions)

        else:
            self._logger.warning(f"Unknown operation: {operation}")
            return data

    def get_schema(self, data: dd.DataFrame) -> Dict[str, Any]:
        """
        Get schema information for the data.

        Args:
            data: Data to analyze

        Returns:
            Schema information
        """
        # Use a small sample to get schema info
        sample = data.head(1000)

        return {
            'columns': list(data.columns),
            'dtypes': data.dtypes.to_dict(),
            'npartitions': data.npartitions,
            'estimated_rows': len(data),
            'sample_null_counts': sample.isnull().sum().to_dict(),
            'numeric_columns': list(data.select_dtypes(include=['number']).columns),
        }

    def get_sample(self, data: dd.DataFrame, size: int = 1000) -> pd.DataFrame:
        """
        Get a sample of the data.

        Args:
            data: Data to sample
            size: Sample size

        Returns:
            Data sample as pandas DataFrame
        """
        return data.head(size)

    def iterate_chunks(self, data: dd.DataFrame, chunk_size: int) -> Iterator[pd.DataFrame]:
        """
        Iterate over data in chunks.

        Args:
            data: Data to iterate
            chunk_size: Size of each chunk (repartitions if needed)

        Yields:
            Data chunks as pandas DataFrames
        """
        # Repartition to desired chunk size if needed
        estimated_partition_size = len(data) // data.npartitions
        if estimated_partition_size > chunk_size * 2:
            new_partitions = max(1, len(data) // chunk_size)
            data = data.repartition(npartitions=new_partitions)

        for partition in data.to_delayed():
            yield partition.compute()

    def get_size_info(self, data: dd.DataFrame) -> Dict[str, Any]:
        """
        Get size information about the data.

        Args:
            data: Data to analyze

        Returns:
            Size information
        """
        # Get memory usage from a sample
        sample = data.head(1000)
        sample_memory = sample.memory_usage(deep=True).sum()
        estimated_total_memory = sample_memory * (len(data) / len(sample)) if len(sample) > 0 else 0

        return {
            'estimated_rows': len(data),
            'columns': len(data.columns),
            'npartitions': data.npartitions,
            'estimated_memory_bytes': estimated_total_memory,
            'distributed': True,
        }

    def to_arrow(self, data: dd.DataFrame) -> pa.Table:
        """
        Convert data to Apache Arrow format.

        Args:
            data: Data to convert

        Returns:
            Arrow table
        """
        # Convert to pandas first, then to Arrow
        pandas_df = data.compute()
        return pa.Table.from_pandas(pandas_df)

    def from_arrow(self, arrow_data: pa.Table) -> dd.DataFrame:
        """
        Convert from Apache Arrow format to Dask DataFrame.

        Args:
            arrow_data: Arrow table

        Returns:
            Dask DataFrame
        """
        pandas_df = arrow_data.to_pandas()
        return dd.from_pandas(pandas_df, npartitions=4)

    def compute_result(self, data: dd.DataFrame) -> pd.DataFrame:
        """
        Compute the final result from lazy Dask DataFrame.

        Args:
            data: Dask DataFrame to compute

        Returns:
            Computed pandas DataFrame
        """
        return data.compute()

    def optimize_for_profile(self, data_profile: DataProfile) -> Dict[str, Any]:
        """
        Get optimization settings for Dask operations.

        Args:
            data_profile: Profile of the data

        Returns:
            Optimization settings
        """
        optimizations = super().optimize_for_profile(data_profile)

        # Dask-specific optimizations
        estimated_partitions = max(1, data_profile.size_bytes // (100 * 1024 * 1024))  # 100MB per partition
        optimizations['npartitions'] = min(estimated_partitions, 100)  # Cap at 100 partitions

        if data_profile.requires_distributed_processing:
            optimizations['use_distributed_client'] = True

        return optimizations
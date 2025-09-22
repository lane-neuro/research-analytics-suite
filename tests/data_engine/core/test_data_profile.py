# test_data_profile.py

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import os

from research_analytics_suite.data_engine import DataProfile


class TestDataProfile:

    def test_from_data_basic_types(self):
        """Test DataProfile creation from basic data types."""
        # Test with different data types
        data_types = [
            ([1, 2, 3, 4], "array"),
            ("test string", "text"),
            ({"a": 1, "b": 2}, "structured"),
            (42, "scalar")
        ]

        for data, expected_type in data_types:
            profile = DataProfile.from_data(data)
            assert profile.data_type == expected_type
            assert profile.storage_location == "memory"
            assert profile.format == "in_memory"
            assert profile.size_bytes > 0

    def test_from_data_pandas_dataframe(self):
        """Test DataProfile creation from pandas DataFrame."""
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        profile = DataProfile.from_data(df)

        assert profile.data_type == "tabular"
        assert profile.storage_location == "memory"
        assert profile.format == "in_memory"
        assert profile.size_bytes > 0

    def test_from_file_csv(self):
        """Test DataProfile creation from CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("col1,col2\n1,2\n3,4")
            temp_path = f.name

        try:
            profile = DataProfile.from_file(temp_path)
            assert profile.data_type == "tabular"
            assert profile.format == "csv"
            assert profile.storage_location == "local"
            assert profile.size_bytes > 0
        finally:
            os.unlink(temp_path)

    def test_size_properties(self):
        """Test size conversion properties."""
        # Create profile with known size
        profile = DataProfile(size_bytes=1024 * 1024 * 1024)  # 1GB

        assert profile.size_mb == 1024
        assert profile.size_gb == 1
        assert profile.size_tb == 1/1024

    def test_dataset_size_classification(self):
        """Test dataset size classification."""
        # Small dataset
        small_profile = DataProfile(size_bytes=100 * 1024 * 1024)  # 100MB
        assert not small_profile.is_large_dataset
        assert not small_profile.is_massive_dataset

        # Large dataset
        large_profile = DataProfile(size_bytes=2 * 1024 * 1024 * 1024)  # 2GB
        assert large_profile.is_large_dataset
        assert not large_profile.is_massive_dataset

        # Massive dataset
        massive_profile = DataProfile(size_bytes=200 * 1024 * 1024 * 1024)  # 200GB
        assert massive_profile.is_large_dataset
        assert massive_profile.is_massive_dataset

    def test_backend_suggestions(self):
        """Test backend suggestion logic."""
        # Small tabular data should suggest pandas
        small_tabular = DataProfile(
            size_bytes=10 * 1024 * 1024,
            data_type="tabular"
        )
        assert small_tabular.suggest_backend() == "pandas"

        # Large tabular data should suggest dask_local
        large_tabular = DataProfile(
            size_bytes=2 * 1024 * 1024 * 1024,
            data_type="tabular"
        )
        assert large_tabular.suggest_backend() == "dask_local"

        # GPU-required data should suggest torch
        gpu_data = DataProfile(
            size_bytes=100 * 1024 * 1024,
            data_type="image",
            requires_gpu=True
        )
        assert gpu_data.suggest_backend() == "torch"

    def test_optimal_chunk_size(self):
        """Test optimal chunk size calculation."""
        # Small data - process all at once
        small_profile = DataProfile(size_bytes=1024 * 1024)  # 1MB
        assert small_profile.optimal_chunk_size == small_profile.size_bytes

        # Medium data - 10MB chunks
        medium_profile = DataProfile(size_bytes=50 * 1024 * 1024)  # 50MB
        assert medium_profile.optimal_chunk_size == 10 * 1024 * 1024

        # Large data - 1GB chunks
        large_profile = DataProfile(size_bytes=10 * 1024 * 1024 * 1024)  # 10GB
        assert large_profile.optimal_chunk_size == 1024 * 1024 * 1024

        # Streaming data - 1MB chunks
        streaming_profile = DataProfile(size_bytes=100 * 1024 * 1024, is_streaming=True)
        assert streaming_profile.optimal_chunk_size == 1024 * 1024

    def test_file_not_found(self):
        """Test error handling for non-existent files."""
        with pytest.raises(FileNotFoundError):
            DataProfile.from_file("/nonexistent/file.csv")
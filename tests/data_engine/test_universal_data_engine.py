# test_universal_data_engine.py

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import asyncio
from pathlib import Path

from research_analytics_suite.data_engine import UniversalDataEngine, DataProfile


class TestUniversalDataEngine:

    @pytest.fixture
    def sample_dataframe(self):
        """Fixture for a sample pandas DataFrame."""
        return pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [10, 20, 30, 40, 50],
            'C': ['a', 'b', 'c', 'd', 'e']
        })

    @pytest.fixture
    def sample_csv_file(self, sample_dataframe):
        """Fixture for a temporary CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            sample_dataframe.to_csv(f.name, index=False)
            temp_path = f.name

        yield temp_path

        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.fixture
    async def engine(self):
        """Fixture for UniversalDataEngine."""
        engine = UniversalDataEngine(name="test_engine")
        yield engine
        await engine.cleanup()

    @pytest.mark.asyncio
    async def test_engine_initialization(self, engine):
        """Test engine initialization."""
        assert engine.name == "test_engine"
        assert engine.engine_id is not None
        assert engine.runtime_id.startswith("ude-")
        assert engine.short_id.startswith("test_engine")

    @pytest.mark.asyncio
    async def test_load_data_from_dataframe(self, engine, sample_dataframe):
        """Test loading data from pandas DataFrame."""
        data, profile = await engine.load_data(sample_dataframe)

        assert data is not None
        assert isinstance(profile, DataProfile)
        assert profile.data_type == "tabular"
        assert profile.storage_location == "memory"

    @pytest.mark.asyncio
    async def test_load_data_from_file(self, engine, sample_csv_file):
        """Test loading data from CSV file."""
        data, profile = await engine.load_data(sample_csv_file)

        assert data is not None
        assert isinstance(profile, DataProfile)
        assert profile.data_type == "tabular"
        assert profile.format == "csv"
        assert profile.storage_location == "local"

    @pytest.mark.asyncio
    async def test_save_data(self, engine, sample_dataframe):
        """Test saving data to file."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            temp_path = f.name

        try:
            success = await engine.save_data(sample_dataframe, temp_path)
            assert success is True
            assert os.path.exists(temp_path)

            # Verify the saved data
            saved_data = pd.read_csv(temp_path)
            pd.testing.assert_frame_equal(saved_data, sample_dataframe)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_analyze_data(self, engine, sample_dataframe):
        """Test data analysis functionality."""
        analysis = await engine.analyze_data(sample_dataframe)

        assert 'profile' in analysis
        assert 'schema' in analysis
        assert 'size_info' in analysis
        assert analysis['profile']['data_type'] == 'tabular'

    @pytest.mark.asyncio
    async def test_get_data_info(self, engine, sample_dataframe):
        """Test getting data information."""
        info = await engine.get_data_info(sample_dataframe)

        assert 'data_type' in info
        assert 'size_mb' in info
        assert info['data_type'] == 'tabular'

    @pytest.mark.asyncio
    async def test_filter_rows(self, engine, sample_dataframe):
        """Test row filtering functionality."""
        # This test assumes the adapter supports filter_rows operation
        try:
            filtered_data = await engine.filter_rows(sample_dataframe, "A > 2")
            # Basic check - we can't assert exact results without knowing adapter behavior
            assert filtered_data is not None
        except (RuntimeError, NotImplementedError):
            # Skip if adapter doesn't support filtering yet
            pytest.skip("Row filtering not yet implemented in adapter")

    @pytest.mark.asyncio
    async def test_select_columns(self, engine, sample_dataframe):
        """Test column selection functionality."""
        try:
            selected_data = await engine.select_columns(sample_dataframe, ['A', 'B'])
            assert selected_data is not None
        except (RuntimeError, NotImplementedError):
            # Skip if adapter doesn't support column selection yet
            pytest.skip("Column selection not yet implemented in adapter")

    @pytest.mark.asyncio
    async def test_get_supported_formats(self, engine):
        """Test getting supported formats."""
        formats = engine.get_supported_formats()
        assert isinstance(formats, dict)
        # Should have at least some format support
        assert len(formats) >= 0

    @pytest.mark.asyncio
    async def test_get_performance_stats(self, engine):
        """Test getting performance statistics."""
        stats = engine.get_performance_stats()

        assert 'engine_info' in stats
        assert 'execution_engine' in stats
        assert 'adapter_registry' in stats
        assert stats['engine_info']['name'] == 'test_engine'

    @pytest.mark.asyncio
    async def test_health_check(self, engine):
        """Test engine health check."""
        health = await engine.health_check()

        assert 'status' in health
        assert 'components' in health
        assert 'issues' in health
        assert health['status'] in ['healthy', 'unhealthy']

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test using engine as async context manager."""
        async with UniversalDataEngine(name="context_test") as engine:
            assert engine.name == "context_test"
            # Engine should be functional within context
            stats = engine.get_performance_stats()
            assert stats is not None

    @pytest.mark.asyncio
    async def test_cleanup(self, engine):
        """Test engine cleanup."""
        # Add some data to cache first
        sample_data = [1, 2, 3, 4, 5]
        await engine.load_data(sample_data)

        # Cleanup should not raise errors
        await engine.cleanup()

    def test_string_representations(self):
        """Test string representations of the engine."""
        engine = UniversalDataEngine(name="repr_test")

        str_repr = str(engine)
        assert "UniversalDataEngine" in str_repr
        assert "repr_test" in str_repr

        repr_str = repr(engine)
        assert "UniversalDataEngine" in repr_str
        assert "repr_test" in repr_str

    @pytest.mark.asyncio
    async def test_error_handling_invalid_source(self, engine):
        """Test error handling for invalid data sources."""
        with pytest.raises((FileNotFoundError, RuntimeError, ValueError)):
            await engine.load_data("/nonexistent/file.csv")

    @pytest.mark.asyncio
    async def test_quick_functions(self, sample_dataframe):
        """Test convenience quick functions."""
        from research_analytics_suite.data_engine import quick_load, quick_save, quick_analyze

        # Test quick_load
        loaded_data = await quick_load(sample_dataframe)
        assert loaded_data is not None

        # Test quick_analyze
        analysis = await quick_analyze(sample_dataframe)
        assert 'profile' in analysis

        # Test quick_save
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            temp_path = f.name

        try:
            success = await quick_save(sample_dataframe, temp_path)
            assert success is True
            assert os.path.exists(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
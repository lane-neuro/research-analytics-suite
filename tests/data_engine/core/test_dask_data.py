import pytest
import pandas as pd
import dask.dataframe as dd
from research_analytics_suite.data_engine import DaskData


class TestDaskData:

    @pytest.fixture
    def sample_pandas_df(self):
        """Fixture for a sample pandas DataFrame."""
        data = {
            'A': [1, 2, 3, 4],
            'B': [5, 6, 7, 8]
        }
        return pd.DataFrame(data)

    @pytest.fixture
    def sample_dask_df(self, sample_pandas_df):
        """Fixture for a sample dask DataFrame."""
        return dd.from_pandas(sample_pandas_df, npartitions=2)

    @pytest.fixture
    def empty_pandas_df(self):
        """Fixture for an empty pandas DataFrame."""
        return pd.DataFrame()

    @pytest.fixture
    def nan_pandas_df(self):
        """Fixture for a pandas DataFrame with NaN values."""
        data = {
            'A': [1, None, 3, 4],
            'B': [5, 6, None, 8]
        }
        return pd.DataFrame(data)

    @pytest.mark.skip(reason="Takes too long to run")
    def test_initialization_with_pandas_df(self, sample_pandas_df):
        """Test initialization with a pandas DataFrame."""
        dask_data = DaskData(sample_pandas_df)
        assert isinstance(dask_data.dask_dataframe, dd.DataFrame)
        assert dask_data.dask_dataframe.compute().equals(sample_pandas_df)

    def test_initialization_with_dask_df(self, sample_dask_df):
        """Test initialization with a dask DataFrame."""
        dask_data = DaskData(sample_dask_df)
        assert isinstance(dask_data.dask_dataframe, dd.DataFrame)
        assert dask_data.dask_dataframe.compute().equals(sample_dask_df.compute())

    def test_apply_function(self, sample_pandas_df):
        """Test applying a function to the dask DataFrame."""

        def add_one(df):
            return df + 1

        dask_data = DaskData(sample_pandas_df)
        dask_data.apply(add_one)
        result = dask_data.compute()

        expected_result = sample_pandas_df + 1
        assert result.equals(expected_result)

    def test_set_dataframe_with_pandas_df(self, sample_pandas_df):
        """Test setting the DataFrame with a pandas DataFrame."""
        dask_data = DaskData(sample_pandas_df)
        dask_data.dask_dataframe = dask_data.set_dataframe(sample_pandas_df)
        assert isinstance(dask_data.dask_dataframe, dd.DataFrame)
        assert dask_data.dask_dataframe.compute().equals(sample_pandas_df)

    def test_set_dataframe_with_dask_df(self, sample_dask_df):
        """Test setting the DataFrame with a dask DataFrame."""
        dask_data = DaskData(sample_dask_df)
        dask_data.dask_dataframe = dask_data.set_dataframe(sample_dask_df)
        assert isinstance(dask_data.dask_dataframe, dd.DataFrame)
        assert dask_data.dask_dataframe.compute().equals(sample_dask_df.compute())

    def test_compute(self, sample_pandas_df):
        """Test computing the dask DataFrame."""
        dask_data = DaskData(sample_pandas_df)
        result = dask_data.compute()
        assert isinstance(result, pd.DataFrame)
        assert result.equals(sample_pandas_df)

    def test_initialization_with_empty_df(self, empty_pandas_df):
        """Test initialization with an empty DataFrame."""
        dask_data = DaskData(empty_pandas_df)
        assert isinstance(dask_data.dask_dataframe, dd.DataFrame)
        assert dask_data.dask_dataframe.compute().empty

    def test_initialization_with_nan_df(self, nan_pandas_df):
        """Test initialization with a DataFrame containing NaN values."""
        dask_data = DaskData(nan_pandas_df)
        assert isinstance(dask_data.dask_dataframe, dd.DataFrame)
        assert dask_data.dask_dataframe.compute().equals(nan_pandas_df)

    def test_apply_function_with_exception(self, sample_pandas_df):
        """Test applying a function that raises an exception."""

        def faulty_function(df):
            raise ValueError("Intentional Error")

        dask_data = DaskData(sample_pandas_df)
        with pytest.raises(ValueError, match="Intentional Error"):
            dask_data.apply(faulty_function).compute()

    def test_chained_apply_functions(self, sample_pandas_df):
        """Test chaining multiple apply functions."""

        def add_one(df):
            return df + 1

        def multiply_by_two(df):
            return df * 2

        dask_data = DaskData(sample_pandas_df)
        dask_data.apply(add_one).apply(multiply_by_two)
        result = dask_data.compute()

        expected_result = (sample_pandas_df + 1) * 2
        assert result.equals(expected_result)

    def test_set_new_dataframe(self, sample_pandas_df, nan_pandas_df):
        """Test setting a new DataFrame."""
        dask_data = DaskData(sample_pandas_df)
        dask_data.set_dataframe(nan_pandas_df)
        assert dask_data.dask_dataframe.compute().equals(nan_pandas_df)

    def test_dataframe_shape_and_columns(self, sample_pandas_df):
        """Test shape and columns of the Dask DataFrame."""
        dask_data = DaskData(sample_pandas_df)
        assert dask_data.dask_dataframe.shape[0].compute() == 4
        assert list(dask_data.dask_dataframe.columns) == ['A', 'B']

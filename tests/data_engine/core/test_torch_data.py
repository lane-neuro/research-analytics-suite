import pytest
import pandas as pd
import numpy as np
import torch
from research_analytics_suite.data_engine import TorchData


class TestTorchData:

    @pytest.fixture
    def sample_pandas_df(self):
        """Fixture for a sample pandas DataFrame."""
        data = {
            'A': [1, 2, 3, 4],
            'B': [5, 6, 7, 8]
        }
        return pd.DataFrame(data)

    @pytest.fixture
    def sample_numpy_array(self):
        """Fixture for a sample numpy array."""
        return np.array([[1, 2], [3, 4], [5, 6]])

    @pytest.fixture
    def sample_tensor(self):
        """Fixture for a sample PyTorch tensor."""
        return torch.tensor([[1, 2], [3, 4], [5, 6]])

    @pytest.fixture
    def sample_list(self):
        """Fixture for a sample list."""
        return [[1, 2], [3, 4], [5, 6]]

    @pytest.fixture
    def sample_dict(self):
        """Fixture for a sample dictionary."""
        return {'a': 1, 'b': 2, 'c': 3}

    @pytest.fixture
    def sample_tuple(self):
        """Fixture for a sample tuple."""
        return (1, 2, 3, 4)

    def test_initialization_with_pandas_df(self, sample_pandas_df):
        """Test initialization with a pandas DataFrame."""
        torch_data = TorchData(sample_pandas_df)
        expected_tensor = torch.tensor(sample_pandas_df.values)
        assert torch.equal(torch_data.torch_tensor, expected_tensor)

    def test_initialization_with_numpy_array(self, sample_numpy_array):
        """Test initialization with a numpy array."""
        torch_data = TorchData(sample_numpy_array)
        expected_tensor = torch.tensor(sample_numpy_array)
        assert torch.equal(torch_data.torch_tensor, expected_tensor)

    def test_initialization_with_tensor(self, sample_tensor):
        """Test initialization with a PyTorch tensor."""
        torch_data = TorchData(sample_tensor)
        assert torch.equal(torch_data.torch_tensor, sample_tensor)

    def test_initialization_with_list(self, sample_list):
        """Test initialization with a list."""
        torch_data = TorchData(sample_list)
        expected_tensor = torch.tensor(sample_list)
        assert torch.equal(torch_data.torch_tensor, expected_tensor)

    def test_initialization_with_dict(self, sample_dict):
        """Test initialization with a dictionary."""
        torch_data = TorchData(sample_dict)
        expected_tensor = torch.tensor(list(sample_dict.values()))
        assert torch.equal(torch_data.torch_tensor, expected_tensor)

    def test_initialization_with_tuple(self, sample_tuple):
        """Test initialization with a tuple."""
        torch_data = TorchData(sample_tuple)
        expected_tensor = torch.tensor(sample_tuple)
        assert torch.equal(torch_data.torch_tensor, expected_tensor)

    def test_len(self, sample_pandas_df):
        """Test the length of the PyTorch tensor."""
        torch_data = TorchData(sample_pandas_df)
        assert len(torch_data) == len(sample_pandas_df)

    def test_getitem(self, sample_pandas_df):
        """Test retrieving an item by index from the PyTorch tensor."""
        torch_data = TorchData(sample_pandas_df)
        for idx in range(len(sample_pandas_df)):
            expected_item = torch.tensor(sample_pandas_df.values[idx])
            assert torch.equal(torch_data[idx], expected_item)

    def test_set_tensor_with_pandas_df(self, sample_pandas_df):
        """Test setting the PyTorch tensor with a pandas DataFrame."""
        torch_data = TorchData(sample_pandas_df)
        new_data = pd.DataFrame({'A': [10, 20], 'B': [30, 40]})
        torch_data.torch_tensor = torch_data.set_tensor(new_data)
        expected_tensor = torch.tensor(new_data.values)
        assert torch.equal(torch_data.torch_tensor, expected_tensor)

    def test_set_tensor_with_numpy_array(self, sample_numpy_array):
        """Test setting the PyTorch tensor with a numpy array."""
        torch_data = TorchData(sample_numpy_array)
        new_data = np.array([[10, 20], [30, 40]])
        torch_data.torch_tensor = torch_data.set_tensor(new_data)
        expected_tensor = torch.tensor(new_data)
        assert torch.equal(torch_data.torch_tensor, expected_tensor)

    def test_set_tensor_with_tensor(self, sample_tensor):
        """Test setting the PyTorch tensor with a tensor."""
        torch_data = TorchData(sample_tensor)
        new_data = torch.tensor([[10, 20], [30, 40]])
        torch_data.torch_tensor = torch_data.set_tensor(new_data)
        assert torch.equal(torch_data.torch_tensor, new_data)

    def test_set_tensor_with_list(self, sample_list):
        """Test setting the PyTorch tensor with a list."""
        torch_data = TorchData(sample_list)
        new_data = [[10, 20], [30, 40]]
        torch_data.torch_tensor = torch_data.set_tensor(new_data)
        expected_tensor = torch.tensor(new_data)
        assert torch.equal(torch_data.torch_tensor, expected_tensor)

    def test_set_tensor_with_dict(self, sample_dict):
        """Test setting the PyTorch tensor with a dictionary."""
        torch_data = TorchData(sample_dict)
        new_data = {'x': 10, 'y': 20}
        torch_data.torch_tensor = torch_data.set_tensor(new_data)
        expected_tensor = torch.tensor(list(new_data.values()))
        assert torch.equal(torch_data.torch_tensor, expected_tensor)

    def test_set_tensor_with_tuple(self, sample_tuple):
        """Test setting the PyTorch tensor with a tuple."""
        torch_data = TorchData(sample_tuple)
        new_data = (10, 20, 30)
        torch_data.torch_tensor = torch_data.set_tensor(new_data)
        expected_tensor = torch.tensor(new_data)
        assert torch.equal(torch_data.torch_tensor, expected_tensor)

"""
TorchData Module

Defines the TorchData class for handling data using PyTorch in the Research Analytics Suite.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset

from research_analytics_suite.commands import command, link_class_commands
from research_analytics_suite.data_engine.core.BaseData import BaseData


@link_class_commands
class TorchData(BaseData, Dataset):
    """
    A class to handle data using PyTorch.

    Attributes:
        data: The data point.
        torch_tensor: PyTorch tensor created from the data point.
    """

    def __init__(self, data):
        """
        Initializes the TorchData instance.

        Args:
            data: The data point.
        """
        BaseData.__init__(self, data)
        self.torch_tensor = self.set_tensor(data)

    def __len__(self):
        """
        Returns the length of the PyTorch tensor.

        Returns:
            int: The length of the PyTorch tensor.
        """
        return len(self.torch_tensor)

    def __getitem__(self, idx):
        """
        Retrieves an item from the PyTorch tensor by index.

        Args:
            idx (int): The index of the item to retrieve.

        Returns:
            The item at the specified index.
        """
        return self.torch_tensor[idx]

    @command
    def set_tensor(self, data) -> torch.Tensor:
        """
        Sets the PyTorch tensor.

        Args:
            data: The data point.
        """
        tensor = None

        if isinstance(data, torch.Tensor):
            tensor = data
        elif isinstance(data, pd.DataFrame):
            tensor = torch.tensor(data.values)
        elif isinstance(data, np.ndarray):
            tensor = torch.tensor(data)
        elif isinstance(data, list):
            tensor = torch.tensor(data)
        elif isinstance(data, dict):
            tensor = torch.tensor(list(data.values()))
        elif isinstance(data, tuple):
            tensor = torch.tensor(data)

        return tensor

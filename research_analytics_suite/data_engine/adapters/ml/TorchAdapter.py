"""
TorchAdapter Module

Machine learning tensor adapter using PyTorch.
Essential for ML workflows and GPU acceleration.

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
    import torch
    import numpy as np
    import pyarrow as pa
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from research_analytics_suite.data_engine.adapters.BaseAdapter import MLAdapter
from research_analytics_suite.data_engine.core.DataProfile import DataProfile
from research_analytics_suite.utils.CustomLogger import CustomLogger


class TorchAdapter(MLAdapter):
    """
    Machine learning tensor adapter using PyTorch.

    Provides tensor operations, GPU acceleration, and ML-specific
    data transformations essential for scalable ML workflows.
    """

    def __init__(self):
        """Initialize the Torch adapter."""
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch not available but is required for ML scalability")

        super().__init__(
            name="torch",
            supported_formats=['pt', 'pth', 'tensor', 'npy', 'npz'],
            supported_data_types=['tensor', 'ml_data', 'numerical']
        )
        self._logger = CustomLogger()
        self._device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def can_handle(self, data_profile: DataProfile) -> bool:
        """
        Check if this adapter can handle the given data profile.

        Args:
            data_profile: Profile of the data to check

        Returns:
            True if this adapter can handle the data
        """
        if data_profile.data_type not in ["tensor", "ml_data", "numerical"]:
            return False

        if data_profile.format not in self.supported_formats:
            return False

        # Prefer for ML operations or when GPU acceleration is beneficial
        return (data_profile.requires_gpu or
                data_profile.data_type in ["tensor", "ml_data"])

    def load(self, source: Union[str, Path, Any], **kwargs) -> torch.Tensor:
        """
        Load data from source as PyTorch tensor.

        Args:
            source: Data source (file path or data object)
            **kwargs: Additional loading parameters

        Returns:
            Loaded data as PyTorch tensor
        """
        device = kwargs.get('device', self._device)

        if isinstance(source, (str, Path)):
            source_path = Path(source)
            file_ext = source_path.suffix.lower().lstrip('.')

            if file_ext in ['pt', 'pth']:
                return torch.load(source, map_location=device)
            elif file_ext == 'npy':
                array = np.load(source)
                return torch.from_numpy(array).to(device)
            elif file_ext == 'npz':
                arrays = np.load(source)
                # Return first array or combine if multiple
                if len(arrays.files) == 1:
                    return torch.from_numpy(arrays[arrays.files[0]]).to(device)
                else:
                    # Stack arrays if multiple
                    combined = np.stack([arrays[f] for f in arrays.files])
                    return torch.from_numpy(combined).to(device)
            else:
                raise ValueError(f"Unsupported format: {file_ext}")

        elif isinstance(source, torch.Tensor):
            return source.to(device)
        elif isinstance(source, np.ndarray):
            return torch.from_numpy(source).to(device)
        elif hasattr(source, '__array__'):
            # Convert array-like objects
            return torch.tensor(np.array(source)).to(device)
        else:
            raise ValueError(f"Unsupported source type: {type(source)}")

    def save(self, data: torch.Tensor, destination: Union[str, Path], **kwargs) -> bool:
        """
        Save tensor data to destination.

        Args:
            data: Tensor to save
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

            if file_ext in ['pt', 'pth']:
                torch.save(data, destination)
            elif file_ext == 'npy':
                np.save(destination, data.cpu().numpy())
            elif file_ext == 'npz':
                np.savez(destination, tensor=data.cpu().numpy())
            else:
                # Default to .pt format
                torch.save(data, str(destination) + '.pt')

            return True
        except Exception as e:
            self._logger.error(f"Failed to save tensor: {e}")
            return False

    def transform(self, data: torch.Tensor, operation: str, **kwargs) -> torch.Tensor:
        """
        Apply transformation to tensor data.

        Args:
            data: Tensor to transform
            operation: Name of the operation
            **kwargs: Operation parameters

        Returns:
            Transformed tensor
        """
        if operation == 'normalize':
            mean = kwargs.get('mean', data.mean())
            std = kwargs.get('std', data.std())
            return (data - mean) / std

        elif operation == 'standardize':
            return (data - data.mean()) / data.std()

        elif operation == 'reshape':
            shape = kwargs.get('shape')
            if shape:
                return data.reshape(shape)
            return data

        elif operation == 'transpose':
            dims = kwargs.get('dims', (0, 1))
            return data.transpose(*dims)

        elif operation == 'flatten':
            start_dim = kwargs.get('start_dim', 1)
            return torch.flatten(data, start_dim=start_dim)

        elif operation == 'squeeze':
            dim = kwargs.get('dim')
            return data.squeeze(dim) if dim is not None else data.squeeze()

        elif operation == 'unsqueeze':
            dim = kwargs.get('dim', 0)
            return data.unsqueeze(dim)

        elif operation == 'slice':
            indices = kwargs.get('indices', slice(None))
            return data[indices]

        elif operation == 'to_device':
            device = kwargs.get('device', self._device)
            return data.to(device)

        else:
            self._logger.warning(f"Unknown operation: {operation}")
            return data

    def get_schema(self, data: torch.Tensor) -> Dict[str, Any]:
        """
        Get schema information for tensor data.

        Args:
            data: Tensor to analyze

        Returns:
            Schema information
        """
        return {
            'shape': list(data.shape),
            'dtype': str(data.dtype),
            'device': str(data.device),
            'requires_grad': data.requires_grad,
            'is_cuda': data.is_cuda,
            'numel': data.numel(),
            'element_size': data.element_size(),
            'storage_size': data.storage().size() if data.storage() else 0,
        }

    def get_sample(self, data: torch.Tensor, size: int = 1000) -> torch.Tensor:
        """
        Get a sample of the tensor data.

        Args:
            data: Tensor to sample
            size: Sample size

        Returns:
            Tensor sample
        """
        if data.numel() <= size:
            return data.clone()

        # Sample from flattened tensor
        flat_data = data.flatten()
        indices = torch.randperm(flat_data.size(0))[:size]
        return flat_data[indices]

    def iterate_chunks(self, data: torch.Tensor, chunk_size: int) -> Iterator[torch.Tensor]:
        """
        Iterate over tensor data in chunks.

        Args:
            data: Tensor to iterate
            chunk_size: Size of each chunk

        Yields:
            Tensor chunks
        """
        total_elements = data.numel()
        flat_data = data.flatten()

        for start in range(0, total_elements, chunk_size):
            end = min(start + chunk_size, total_elements)
            yield flat_data[start:end]

    def get_size_info(self, data: torch.Tensor) -> Dict[str, Any]:
        """
        Get size information about tensor data.

        Args:
            data: Tensor to analyze

        Returns:
            Size information
        """
        element_size = data.element_size()
        total_bytes = data.numel() * element_size

        return {
            'shape': list(data.shape),
            'numel': data.numel(),
            'element_size_bytes': element_size,
            'total_bytes': total_bytes,
            'total_mb': total_bytes / (1024 * 1024),
            'device': str(data.device),
            'dtype': str(data.dtype),
        }

    def to_arrow(self, data: torch.Tensor) -> pa.Array:
        """
        Convert tensor to Apache Arrow format.

        Args:
            data: Tensor to convert

        Returns:
            Arrow array
        """
        # Convert to numpy first, then to Arrow
        numpy_array = data.cpu().numpy()
        return pa.array(numpy_array.flatten())

    def from_arrow(self, arrow_data: pa.Array) -> torch.Tensor:
        """
        Convert from Apache Arrow format to tensor.

        Args:
            arrow_data: Arrow array

        Returns:
            PyTorch tensor
        """
        numpy_array = arrow_data.to_numpy()
        return torch.from_numpy(numpy_array).to(self._device)

    def to_tensor(self, data: Any, device: str = 'cpu') -> torch.Tensor:
        """
        Convert data to tensor format.

        Args:
            data: Data to convert
            device: Target device

        Returns:
            Tensor data
        """
        target_device = torch.device(device)

        if isinstance(data, torch.Tensor):
            return data.to(target_device)
        elif isinstance(data, np.ndarray):
            return torch.from_numpy(data).to(target_device)
        else:
            return torch.tensor(data).to(target_device)

    def create_dataloader(self, data: torch.Tensor, batch_size: int,
                         shuffle: bool = True, **kwargs) -> torch.utils.data.DataLoader:
        """
        Create a data loader for training/inference.

        Args:
            data: Training data tensor
            batch_size: Batch size
            shuffle: Whether to shuffle data
            **kwargs: Additional parameters

        Returns:
            PyTorch DataLoader
        """
        from torch.utils.data import TensorDataset, DataLoader

        # Create dataset
        if 'targets' in kwargs:
            targets = kwargs['targets']
            if not isinstance(targets, torch.Tensor):
                targets = torch.tensor(targets)
            dataset = TensorDataset(data, targets)
        else:
            dataset = TensorDataset(data)

        # Create dataloader
        return DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            **{k: v for k, v in kwargs.items() if k != 'targets'}
        )

    def preprocess(self, data: torch.Tensor, preprocessing_config: Dict[str, Any]) -> torch.Tensor:
        """
        Apply preprocessing to tensor data.

        Args:
            data: Raw tensor data
            preprocessing_config: Preprocessing configuration

        Returns:
            Preprocessed tensor
        """
        processed_data = data

        for operation, params in preprocessing_config.items():
            if isinstance(params, dict):
                processed_data = self.transform(processed_data, operation, **params)
            else:
                processed_data = self.transform(processed_data, operation)

        return processed_data

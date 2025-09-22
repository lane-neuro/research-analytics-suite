"""
NumpyAdapter Module

Numerical data adapter using NumPy.
Core foundation for all numerical operations and interoperability.

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
    import numpy as np
    import pyarrow as pa
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

from research_analytics_suite.data_engine.adapters.BaseAdapter import BaseAdapter
from research_analytics_suite.data_engine.core.DataProfile import DataProfile
from research_analytics_suite.utils.CustomLogger import CustomLogger


class NumpyAdapter(BaseAdapter):
    """
    Numerical data adapter using NumPy.

    NumPy provides the foundation for numerical computing and
    efficient array operations essential for scientific computing.
    """

    def __init__(self):
        """Initialize the NumPy adapter."""
        if not NUMPY_AVAILABLE:
            raise ImportError("NumPy not available but is core dependency")

        super().__init__(
            name="numpy",
            supported_formats=['npy', 'npz', 'txt', 'csv'],
            supported_data_types=['numerical', 'array', 'matrix']
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
        if data_profile.data_type not in ["numerical", "array", "matrix"]:
            return False

        # Allow in-memory format for array/numerical data, check supported formats for files
        if data_profile.format not in self.supported_formats and data_profile.format != "in_memory":
            return False

        # NumPy is good for moderate-sized numerical data
        return data_profile.size_bytes < 1 * 1024 * 1024 * 1024  # 1GB limit

    def load(self, source: Union[str, Path, Any], **kwargs) -> np.ndarray:
        """
        Load data from source as NumPy array.

        Args:
            source: Data source (file path or data object)
            **kwargs: Additional loading parameters

        Returns:
            Loaded data as NumPy array
        """
        if isinstance(source, (str, Path)):
            source_path = Path(source)
            file_ext = source_path.suffix.lower().lstrip('.')

            if file_ext == 'npy':
                return np.load(source, **kwargs)
            elif file_ext == 'npz':
                arrays = np.load(source)
                # Return first array or combine if multiple
                if len(arrays.files) == 1:
                    return arrays[arrays.files[0]]
                else:
                    # Stack arrays if multiple
                    return np.stack([arrays[f] for f in arrays.files])
            elif file_ext in ['txt', 'csv']:
                delimiter = ',' if file_ext == 'csv' else None
                return np.loadtxt(source, delimiter=delimiter, **kwargs)
            else:
                # Try generic load
                return np.loadtxt(source, **kwargs)

        elif isinstance(source, np.ndarray):
            return source.copy()
        elif isinstance(source, (list, tuple)):
            return np.array(source)
        elif hasattr(source, '__array__'):
            return np.array(source)
        else:
            raise ValueError(f"Unsupported source type: {type(source)}")

    def save(self, data: np.ndarray, destination: Union[str, Path], **kwargs) -> bool:
        """
        Save array data to destination.

        Args:
            data: Array to save
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

            if file_ext == 'npy':
                np.save(destination, data, **kwargs)
            elif file_ext == 'npz':
                np.savez(destination, array=data, **kwargs)
            elif file_ext in ['txt', 'csv']:
                delimiter = ',' if file_ext == 'csv' else ' '
                np.savetxt(destination, data, delimiter=delimiter, **kwargs)
            else:
                # Default to .npy
                np.save(str(destination) + '.npy', data)

            return True
        except Exception as e:
            self._logger.error(f"Failed to save array: {e}")
            return False

    def transform(self, data: np.ndarray, operation: str, **kwargs) -> np.ndarray:
        """
        Apply transformation to array data.

        Args:
            data: Array to transform
            operation: Name of the operation
            **kwargs: Operation parameters

        Returns:
            Transformed array
        """
        if operation == 'normalize':
            axis = kwargs.get('axis', None)
            mean = np.mean(data, axis=axis, keepdims=True)
            std = np.std(data, axis=axis, keepdims=True)
            return (data - mean) / std

        elif operation == 'standardize':
            return (data - np.mean(data)) / np.std(data)

        elif operation == 'reshape':
            shape = kwargs.get('shape')
            if shape:
                return data.reshape(shape)
            return data

        elif operation == 'transpose':
            axes = kwargs.get('axes')
            return np.transpose(data, axes)

        elif operation == 'flatten':
            return data.flatten()

        elif operation == 'squeeze':
            axis = kwargs.get('axis')
            return np.squeeze(data, axis)

        elif operation == 'expand_dims':
            axis = kwargs.get('axis', 0)
            return np.expand_dims(data, axis)

        elif operation == 'slice':
            indices = kwargs.get('indices', slice(None))
            return data[indices]

        elif operation == 'clip':
            min_val = kwargs.get('min', None)
            max_val = kwargs.get('max', None)
            return np.clip(data, min_val, max_val)

        elif operation == 'abs':
            return np.abs(data)

        elif operation == 'sum':
            axis = kwargs.get('axis', None)
            return np.sum(data, axis=axis)

        elif operation == 'mean':
            axis = kwargs.get('axis', None)
            return np.mean(data, axis=axis)

        elif operation == 'std':
            axis = kwargs.get('axis', None)
            return np.std(data, axis=axis)

        else:
            self._logger.warning(f"Unknown operation: {operation}")
            return data

    def get_schema(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Get schema information for array data.

        Args:
            data: Array to analyze

        Returns:
            Schema information
        """
        return {
            'shape': data.shape,
            'dtype': str(data.dtype),
            'ndim': data.ndim,
            'size': data.size,
            'itemsize': data.itemsize,
            'nbytes': data.nbytes,
            'is_contiguous': data.flags.c_contiguous,
            'min_value': float(np.min(data)) if data.size > 0 else None,
            'max_value': float(np.max(data)) if data.size > 0 else None,
            'mean_value': float(np.mean(data)) if data.size > 0 else None,
            'std_value': float(np.std(data)) if data.size > 0 else None,
        }

    def get_sample(self, data: np.ndarray, size: int = 1000) -> np.ndarray:
        """
        Get a sample of the array data.

        Args:
            data: Array to sample
            size: Sample size

        Returns:
            Array sample
        """
        if data.size <= size:
            return data.copy()

        # Sample from flattened array
        flat_data = data.flatten()
        indices = np.random.choice(flat_data.size, size=size, replace=False)
        return flat_data[indices]

    def iterate_chunks(self, data: np.ndarray, chunk_size: int) -> Iterator[np.ndarray]:
        """
        Iterate over array data in chunks.

        Args:
            data: Array to iterate
            chunk_size: Size of each chunk

        Yields:
            Array chunks
        """
        flat_data = data.flatten()
        total_elements = flat_data.size

        for start in range(0, total_elements, chunk_size):
            end = min(start + chunk_size, total_elements)
            yield flat_data[start:end]

    def get_size_info(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Get size information about array data.

        Args:
            data: Array to analyze

        Returns:
            Size information
        """
        return {
            'shape': data.shape,
            'size': data.size,
            'ndim': data.ndim,
            'nbytes': data.nbytes,
            'mbytes': data.nbytes / (1024 * 1024),
            'dtype': str(data.dtype),
            'itemsize': data.itemsize,
        }

    def to_arrow(self, data: np.ndarray) -> pa.Array:
        """
        Convert array to Apache Arrow format.

        Args:
            data: Array to convert

        Returns:
            Arrow array
        """
        # Flatten for Arrow compatibility
        return pa.array(data.flatten())

    def from_arrow(self, arrow_data: pa.Array) -> np.ndarray:
        """
        Convert from Apache Arrow format to array.

        Args:
            arrow_data: Arrow array

        Returns:
            NumPy array
        """
        return arrow_data.to_numpy()

    def create_random_array(self, shape: tuple, dtype: str = 'float64', **kwargs) -> np.ndarray:
        """
        Create a random array for testing/initialization.

        Args:
            shape: Shape of the array
            dtype: Data type
            **kwargs: Additional parameters

        Returns:
            Random array
        """
        if dtype.startswith('int'):
            low = kwargs.get('low', 0)
            high = kwargs.get('high', 100)
            return np.random.randint(low, high, size=shape, dtype=dtype)
        else:
            return np.random.random(shape).astype(dtype)

    def mathematical_operations(self, data: np.ndarray, operation: str, **kwargs) -> np.ndarray:
        """
        Apply mathematical operations to array data.

        Args:
            data: Array data
            operation: Mathematical operation
            **kwargs: Operation parameters

        Returns:
            Result array
        """
        operations_map = {
            'sin': np.sin,
            'cos': np.cos,
            'tan': np.tan,
            'exp': np.exp,
            'log': np.log,
            'log10': np.log10,
            'sqrt': np.sqrt,
            'square': np.square,
            'reciprocal': np.reciprocal,
        }

        if operation in operations_map:
            return operations_map[operation](data)
        elif operation == 'power':
            exponent = kwargs.get('exponent', 2)
            return np.power(data, exponent)
        elif operation == 'add':
            value = kwargs.get('value', 0)
            return data + value
        elif operation == 'multiply':
            value = kwargs.get('value', 1)
            return data * value
        else:
            self._logger.warning(f"Unknown mathematical operation: {operation}")
            return data
"""
DataContext Module

Wrapper class that carries data with its metadata through the processing pipeline.
This ensures schema and other metadata stay synchronized with the actual data.

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

from dataclasses import dataclass
from typing import Any, Dict, Optional, TYPE_CHECKING

from research_analytics_suite.data_engine.core.DataProfile import DataProfile

if TYPE_CHECKING:
    from research_analytics_suite.data_engine.adapters.AdapterRegistry import AdapterRegistry


@dataclass
class DataContext:
    """
    Wrapper that carries data with its metadata through the pipeline.

    This class ensures that:
    - Data and its schema stay synchronized
    - Type information is preserved across transformations
    - Column names and structure metadata are always available
    - Additional metadata can be added without changing data structures

    Attributes:
        data: The actual data (DataFrame, ndarray, tensor, etc.)
        profile: DataProfile with type, size, and processing hints
        schema: Schema information (columns, dtypes, shape, etc.)
        metadata: Additional custom metadata
    """
    data: Any
    profile: DataProfile
    schema: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Initialize optional fields."""
        if self.schema is None:
            self.schema = {}
        if self.metadata is None:
            self.metadata = {}

    @classmethod
    def create(cls, data: Any, adapter_registry: AdapterRegistry,
               data_type: Optional[str] = None) -> "DataContext":
        """
        Create a DataContext from raw data.

        Args:
            data: The data to wrap
            adapter_registry: Registry for selecting appropriate adapter
            data_type: Optional hint for data type (overrides inference)

        Returns:
            DataContext with data, profile, and schema
        """
        profile = DataProfile.from_data(data, data_type)
        adapter = adapter_registry.select_best_adapter(profile, 'schema')
        schema = adapter.get_schema(data) if adapter else {}
        return cls(data=data, profile=profile, schema=schema)

    def update_after_transform(self, new_data: Any, adapter_registry: AdapterRegistry,
                               preserve_type: bool = True) -> "DataContext":
        """
        Create a new DataContext after data transformation.

        Args:
            new_data: The transformed data
            adapter_registry: Registry for selecting appropriate adapter
            preserve_type: If True, preserve original data_type (e.g., keep "tabular" if structure maintained)

        Returns:
            New DataContext with updated data, profile, and schema
        """
        old_type = self.profile.data_type
        new_profile = DataProfile.from_data(new_data)

        if preserve_type:
            if old_type == "tabular" and hasattr(new_data, 'columns'):
                new_profile.data_type = "tabular"
            elif old_type == "time_series" and hasattr(new_data, 'index'):
                new_profile.data_type = "time_series"

        adapter = adapter_registry.select_best_adapter(new_profile, 'schema')
        new_schema = adapter.get_schema(new_data) if adapter else {}
        new_metadata = self.metadata.copy()

        return DataContext(
            data=new_data,
            profile=new_profile,
            schema=new_schema,
            metadata=new_metadata
        )

    @property
    def columns(self) -> Optional[list]:
        """
        Get column names if available.

        Returns:
            List of column names or None if not applicable
        """
        return self.schema.get('columns')

    @property
    def shape(self) -> Optional[tuple]:
        """
        Get data shape if available.

        Returns:
            Shape tuple or None if not applicable
        """
        return self.schema.get('shape')

    @property
    def dtypes(self) -> Optional[Dict[str, str]]:
        """
        Get column data types if available.

        Returns:
            Dictionary mapping column names to types, or None
        """
        return self.schema.get('dtypes')

    def get_column_index(self, column_name: str) -> Optional[int]:
        """Get the numeric index for a column name (useful for numpy arrays)."""
        columns = self.columns
        if columns and column_name in columns:
            return columns.index(column_name)
        return None

    def has_column(self, column_name: str) -> bool:
        """Check if a column exists in the data."""
        columns = self.columns
        return columns is not None and column_name in columns

    def __repr__(self) -> str:
        """String representation."""
        data_type_str = type(self.data).__name__
        shape_str = str(self.shape) if self.shape else "unknown"
        cols_str = f"{len(self.columns)} cols" if self.columns else "no cols"
        return f"DataContext(type={self.profile.data_type}, shape={shape_str}, {cols_str}, data={data_type_str})"

    def __getstate__(self):
        """Prepare DataContext for pickling."""
        return {
            'data': self.data,
            'profile': self.profile,
            'schema': self.schema,
            'metadata': self.metadata
        }

    def __setstate__(self, state):
        """Restore DataContext from pickled state."""
        self.data = state['data']
        self.profile = state['profile']
        self.schema = state.get('schema', {})
        self.metadata = state.get('metadata', {})

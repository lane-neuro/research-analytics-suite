"""
VisualizationDetector Module

Detects appropriate visualization types based on data characteristics and structure.
Analyzes data to recommend optimal chart types for visualization.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

from typing import Dict, Any, Optional, List, Tuple
import numpy as np


class VisualizationDetector:

    @staticmethod
    def detect_visualization_type(data: Any) -> Dict[str, Any]:
        """
        Detects appropriate visualization type(s) for the given data.

        Args:
            data: Data to analyze (DataFrame, array, dict, etc.)

        Returns:
            Dict containing:
                - primary_viz: Primary visualization type
                - alternatives: List of alternative visualization types
                - data_info: Metadata about the data structure
        """
        if data is None:
            return {
                'primary_viz': 'none',
                'alternatives': [],
                'data_info': {'error': 'No data available'}
            }

        data_info = VisualizationDetector._analyze_data_structure(data)

        if data_info['is_pandas']:
            return VisualizationDetector._detect_dataframe_viz(data, data_info)
        elif data_info['is_numpy']:
            return VisualizationDetector._detect_array_viz(data, data_info)
        elif data_info['is_dict']:
            return VisualizationDetector._detect_dict_viz(data, data_info)
        elif data_info['is_list']:
            return VisualizationDetector._detect_list_viz(data, data_info)
        else:
            return {
                'primary_viz': 'text',
                'alternatives': [],
                'data_info': data_info
            }

    @staticmethod
    def _analyze_data_structure(data: Any) -> Dict[str, Any]:
        """Analyze the structure and characteristics of data."""
        info = {
            'is_pandas': False,
            'is_numpy': False,
            'is_dict': False,
            'is_list': False,
            'shape': None,
            'columns': None,
            'dtypes': None,
            'size': 0
        }

        try:
            if hasattr(data, 'columns') and hasattr(data, 'index'):
                info['is_pandas'] = True
                info['shape'] = data.shape
                info['columns'] = list(data.columns)
                info['dtypes'] = {col: str(dtype) for col, dtype in data.dtypes.items()}
                info['size'] = data.size
            elif hasattr(data, 'shape') and hasattr(data, 'dtype'):
                info['is_numpy'] = True
                info['shape'] = data.shape
                info['dtype'] = str(data.dtype)
                info['size'] = data.size
            elif isinstance(data, dict):
                info['is_dict'] = True
                info['keys'] = list(data.keys())
                info['size'] = len(data)
            elif isinstance(data, (list, tuple)):
                info['is_list'] = True
                info['length'] = len(data)
                info['size'] = len(data)
        except Exception:
            pass

        return info

    @staticmethod
    def _detect_dataframe_viz(data, data_info: Dict[str, Any]) -> Dict[str, Any]:
        """Detect visualization for pandas DataFrame."""
        num_rows, num_cols = data_info['shape']
        dtypes = data_info['dtypes']

        numeric_cols = [col for col, dtype in dtypes.items() if 'int' in dtype or 'float' in dtype]
        categorical_cols = [col for col, dtype in dtypes.items() if 'object' in dtype or 'category' in dtype]
        datetime_cols = [col for col, dtype in dtypes.items() if 'datetime' in dtype]

        if len(datetime_cols) > 0 and len(numeric_cols) > 0:
            return {
                'primary_viz': 'line',
                'alternatives': ['scatter', 'area'],
                'data_info': data_info,
                'x_column': datetime_cols[0],
                'y_columns': numeric_cols[:3],
                'suggested_title': 'Time Series Analysis'
            }

        elif num_cols == 2 and len(numeric_cols) == 2:
            return {
                'primary_viz': 'scatter',
                'alternatives': ['line', 'hexbin'],
                'data_info': data_info,
                'x_column': numeric_cols[0],
                'y_columns': [numeric_cols[1]],
                'suggested_title': f'{numeric_cols[1]} vs {numeric_cols[0]}'
            }

        elif num_cols == 1 and len(numeric_cols) == 1:
            return {
                'primary_viz': 'histogram',
                'alternatives': ['box', 'violin'],
                'data_info': data_info,
                'column': numeric_cols[0],
                'suggested_title': f'Distribution of {numeric_cols[0]}'
            }

        elif len(categorical_cols) == 1 and len(numeric_cols) >= 1:
            return {
                'primary_viz': 'bar',
                'alternatives': ['box', 'violin'],
                'data_info': data_info,
                'category_column': categorical_cols[0],
                'value_columns': numeric_cols[:3],
                'suggested_title': f'{numeric_cols[0]} by {categorical_cols[0]}'
            }

        elif len(numeric_cols) > 2:
            return {
                'primary_viz': 'correlation_heatmap',
                'alternatives': ['pairplot', 'parallel_coordinates'],
                'data_info': data_info,
                'columns': numeric_cols,
                'suggested_title': 'Correlation Analysis'
            }

        else:
            return {
                'primary_viz': 'table',
                'alternatives': ['heatmap'],
                'data_info': data_info,
                'suggested_title': 'Data Table'
            }

    @staticmethod
    def _detect_array_viz(data, data_info: Dict[str, Any]) -> Dict[str, Any]:
        """Detect visualization for numpy array."""
        shape = data_info['shape']

        if len(shape) == 1:
            return {
                'primary_viz': 'line',
                'alternatives': ['histogram', 'scatter'],
                'data_info': data_info,
                'suggested_title': 'Array Values'
            }

        elif len(shape) == 2:
            rows, cols = shape

            if rows <= 50 and cols <= 50:
                return {
                    'primary_viz': 'heatmap',
                    'alternatives': ['surface', 'contour'],
                    'data_info': data_info,
                    'suggested_title': '2D Array Heatmap'
                }

            elif cols == 1:
                return {
                    'primary_viz': 'line',
                    'alternatives': ['histogram'],
                    'data_info': data_info,
                    'suggested_title': 'Array Values'
                }

            elif cols == 2:
                return {
                    'primary_viz': 'scatter',
                    'alternatives': ['line'],
                    'data_info': data_info,
                    'suggested_title': '2D Scatter Plot'
                }

            else:
                return {
                    'primary_viz': 'line',
                    'alternatives': ['heatmap'],
                    'data_info': data_info,
                    'suggested_title': 'Multi-column Array'
                }

        else:
            return {
                'primary_viz': 'text',
                'alternatives': [],
                'data_info': data_info,
                'suggested_title': f'{len(shape)}D Array (Shape: {shape})'
            }

    @staticmethod
    def _detect_dict_viz(data: dict, data_info: Dict[str, Any]) -> Dict[str, Any]:
        """Detect visualization for dictionary."""
        keys = data_info['keys']

        values = list(data.values())
        if all(isinstance(v, (int, float)) for v in values):
            return {
                'primary_viz': 'bar',
                'alternatives': ['pie'],
                'data_info': data_info,
                'keys': keys,
                'suggested_title': 'Dictionary Values'
            }

        else:
            return {
                'primary_viz': 'text',
                'alternatives': [],
                'data_info': data_info,
                'suggested_title': 'Dictionary Data'
            }

    @staticmethod
    def _detect_list_viz(data: list, data_info: Dict[str, Any]) -> Dict[str, Any]:
        """Detect visualization for list."""
        if len(data) == 0:
            return {
                'primary_viz': 'text',
                'alternatives': [],
                'data_info': data_info,
                'suggested_title': 'Empty List'
            }

        first_elem = data[0]

        if isinstance(first_elem, (int, float)):
            return {
                'primary_viz': 'line',
                'alternatives': ['histogram', 'box'],
                'data_info': data_info,
                'suggested_title': 'List Values'
            }

        elif isinstance(first_elem, (list, tuple)) and len(first_elem) == 2:
            if all(isinstance(x, (int, float)) for x in first_elem):
                return {
                    'primary_viz': 'scatter',
                    'alternatives': ['line'],
                    'data_info': data_info,
                    'suggested_title': 'Point Cloud'
                }

        return {
            'primary_viz': 'text',
            'alternatives': [],
            'data_info': data_info,
            'suggested_title': 'List Data'
        }

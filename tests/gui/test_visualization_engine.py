"""
Test suite for visualization detection and rendering engine.
"""

import pytest
import numpy as np
import pandas as pd
from research_analytics_suite.gui.modules import VisualizationDetector, VisualizationRenderer


class TestVisualizationDetector:

    def test_detect_numpy_1d_array(self):
        data = np.array([1, 2, 3, 4, 5])
        config = VisualizationDetector.detect_visualization_type(data)

        assert config['primary_viz'] == 'line'
        assert 'histogram' in config['alternatives']
        assert config['data_info']['is_numpy'] is True
        assert config['data_info']['shape'] == (5,)

    def test_detect_numpy_2d_array(self):
        data = np.random.rand(10, 10)
        config = VisualizationDetector.detect_visualization_type(data)

        assert config['primary_viz'] == 'heatmap'
        assert config['data_info']['is_numpy'] is True
        assert config['data_info']['shape'] == (10, 10)

    def test_detect_dataframe_numeric(self):
        data = pd.DataFrame({
            'x': [1, 2, 3, 4, 5],
            'y': [2, 4, 6, 8, 10]
        })
        config = VisualizationDetector.detect_visualization_type(data)

        assert config['primary_viz'] == 'scatter'
        assert config['data_info']['is_pandas'] is True
        assert 'x_column' in config
        assert 'y_columns' in config

    def test_detect_dataframe_single_column(self):
        data = pd.DataFrame({'values': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]})
        config = VisualizationDetector.detect_visualization_type(data)

        assert config['primary_viz'] == 'histogram'
        assert 'column' in config

    def test_detect_dict_numeric(self):
        data = {'a': 10, 'b': 20, 'c': 30}
        config = VisualizationDetector.detect_visualization_type(data)

        assert config['primary_viz'] == 'bar'
        assert config['data_info']['is_dict'] is True

    def test_detect_list_numeric(self):
        data = [1, 2, 3, 4, 5]
        config = VisualizationDetector.detect_visualization_type(data)

        assert config['primary_viz'] == 'line'
        assert config['data_info']['is_list'] is True

    def test_detect_none_data(self):
        config = VisualizationDetector.detect_visualization_type(None)

        assert config['primary_viz'] == 'none'
        assert 'error' in config['data_info']


class TestVisualizationRenderer:

    def test_render_line_chart(self):
        data = np.array([1, 2, 3, 4, 5])
        config = VisualizationDetector.detect_visualization_type(data)

        result = VisualizationRenderer.render(data, config, width=800, height=600)

        assert 'image_data' in result
        assert result['format'] == 'png'
        assert result['figure'] is not None
        assert len(result['image_data']) > 0

    def test_render_scatter_plot(self):
        data = pd.DataFrame({
            'x': [1, 2, 3, 4, 5],
            'y': [2, 4, 6, 8, 10]
        })
        config = VisualizationDetector.detect_visualization_type(data)

        result = VisualizationRenderer.render(data, config, width=800, height=600)

        assert 'image_data' in result
        assert result['format'] == 'png'
        assert result['figure'] is not None

    def test_render_bar_chart(self):
        data = {'a': 10, 'b': 20, 'c': 30}
        config = VisualizationDetector.detect_visualization_type(data)

        result = VisualizationRenderer.render(data, config, width=800, height=600)

        assert 'image_data' in result
        assert result['format'] == 'png'

    def test_render_histogram(self):
        data = pd.DataFrame({'values': np.random.randn(100)})
        config = VisualizationDetector.detect_visualization_type(data)

        result = VisualizationRenderer.render(data, config, width=800, height=600)

        assert 'image_data' in result
        assert result['format'] == 'png'

    def test_render_heatmap(self):
        data = np.random.rand(10, 10)
        config = VisualizationDetector.detect_visualization_type(data)

        result = VisualizationRenderer.render(data, config, width=800, height=600)

        assert 'image_data' in result
        assert result['format'] == 'png'

    def test_export_figure_png(self, tmp_path):
        data = np.array([1, 2, 3, 4, 5])
        config = VisualizationDetector.detect_visualization_type(data)
        result = VisualizationRenderer.render(data, config)

        output_file = tmp_path / "test_chart.png"
        VisualizationRenderer.export_figure(result['figure'], str(output_file), format='png', dpi=100)

        assert output_file.exists()
        assert output_file.stat().st_size > 0

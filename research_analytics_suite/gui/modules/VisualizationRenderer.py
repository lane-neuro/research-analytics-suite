"""
VisualizationRenderer Module

Renders visualizations using Matplotlib based on detected visualization types.
Handles different chart types and export functionality.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

import io
import base64
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator


class VisualizationRenderer:

    # Global chart styling constants
    FONT_SIZE_TITLE = 12
    FONT_SIZE_LABEL = 10
    FONT_SIZE_TICK = 8
    FONT_SIZE_LEGEND = 8
    DPI = 120  # Increased from 100 for better quality
    MAX_ROWS_FULL = 500  # Sample data if more rows
    MAX_TICK_LABELS = 20  # Limit axis tick labels

    @staticmethod
    def _prepare_data(data: Any, viz_config: Dict[str, Any]) -> Any:
        """
        Prepare data for visualization by sampling if too large.

        Args:
            data: Input data
            viz_config: Visualization config

        Returns:
            Sampled data if needed, otherwise original
        """
        import pandas as pd

        # Check if data needs sampling
        num_rows = 0
        if isinstance(data, pd.DataFrame):
            num_rows = len(data)
        elif isinstance(data, np.ndarray) and data.ndim >= 1:
            num_rows = data.shape[0]

        # Sample if too many rows - commented out for now
        # if num_rows > VisualizationRenderer.MAX_ROWS_FULL:
        #     step = num_rows // VisualizationRenderer.MAX_ROWS_FULL
        #     viz_config['_sampling_info'] = {
        #         'sampled': True,
        #         'original_rows': num_rows,
        #         'step': step,
        #         'displayed_rows': num_rows // step
        #     }
        #
        #     if isinstance(data, pd.DataFrame):
        #         return data.iloc[::step].copy()
        #     elif isinstance(data, np.ndarray):
        #         return data[::step]

        return data

    @staticmethod
    def render(data: Any, viz_config: Dict[str, Any], width: int = 800, height: int = 600,
               custom_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Render visualization and return image data.

        Args:
            data: Data to visualize
            viz_config: Visualization configuration from detector
            width: Figure width in pixels
            height: Figure height in pixels
            custom_options: User customization options (title, labels, style, etc.)

        Returns:
            Dict containing:
                - image_data: Base64 encoded PNG image
                - format: 'png'
                - figure: Matplotlib figure object (for export)
        """
        # Prepare data
        data = VisualizationRenderer._prepare_data(data, viz_config)

        viz_type = viz_config.get('primary_viz', 'text')

        # Merge custom options into config for easy access in render methods
        if custom_options:
            viz_config['_custom'] = custom_options
        else:
            viz_config['_custom'] = {}

        # Set global font sizes
        plt.rcParams.update({
            'font.size': VisualizationRenderer.FONT_SIZE_TICK,
            'axes.titlesize': VisualizationRenderer.FONT_SIZE_TITLE,
            'axes.labelsize': VisualizationRenderer.FONT_SIZE_LABEL,
            'xtick.labelsize': VisualizationRenderer.FONT_SIZE_TICK,
            'ytick.labelsize': VisualizationRenderer.FONT_SIZE_TICK,
            'legend.fontsize': VisualizationRenderer.FONT_SIZE_LEGEND,
        })

        fig = plt.figure(figsize=(width/100, height/100), dpi=VisualizationRenderer.DPI)

        try:
            if viz_type == 'line':
                VisualizationRenderer._render_line(fig, data, viz_config)
            elif viz_type == 'scatter':
                VisualizationRenderer._render_scatter(fig, data, viz_config)
            elif viz_type == 'bar':
                VisualizationRenderer._render_bar(fig, data, viz_config)
            elif viz_type == 'histogram':
                VisualizationRenderer._render_histogram(fig, data, viz_config)
            elif viz_type == 'box':
                VisualizationRenderer._render_box(fig, data, viz_config)
            elif viz_type == 'heatmap':
                VisualizationRenderer._render_heatmap(fig, data, viz_config)
            elif viz_type == 'correlation_heatmap':
                VisualizationRenderer._render_correlation_heatmap(fig, data, viz_config)
            elif viz_type == 'pie':
                VisualizationRenderer._render_pie(fig, data, viz_config)
            elif viz_type == 'area':
                VisualizationRenderer._render_area(fig, data, viz_config)
            else:
                VisualizationRenderer._render_text(fig, data, viz_config)

            # Add sampling info annotation if data was sampled
            if viz_config.get('_sampling_info', {}).get('sampled'):
                info = viz_config['_sampling_info']
                fig.text(0.99, 0.01,
                        f"Showing {info['displayed_rows']}/{info['original_rows']} rows (every {info['step']}th)",
                        ha='right', va='bottom', fontsize=8, style='italic', color='gray',
                        transform=fig.transFigure)

            # Apply tight layout to prevent label overlap
            plt.tight_layout(rect=[0, 0.02, 1, 1])  # Leave space for sampling note if present

            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight', dpi=VisualizationRenderer.DPI)
            buf.seek(0)
            image_data = base64.b64encode(buf.read()).decode('utf-8')
            buf.close()

            return {
                'image_data': image_data,
                'format': 'png',
                'figure': fig
            }

        except Exception as e:
            plt.close(fig)
            raise Exception(f"Rendering failed: {str(e)}")

    @staticmethod
    def _render_line(fig: Figure, data: Any, config: Dict[str, Any]):
        """Render line chart."""
        ax = fig.add_subplot(111)
        custom = config.get('_custom', {})

        # Get custom options with defaults
        alpha = custom.get('alpha', 0.7)
        line_style = custom.get('line_style', '-')
        show_grid = custom.get('show_grid', True)
        show_legend = custom.get('show_legend', True)

        if config['data_info'].get('is_pandas'):
            # Use custom x_column if provided, otherwise use config
            x_col = custom.get('x_column') or config.get('x_column')
            # Use custom y_columns if provided, otherwise use config
            y_cols = custom.get('y_columns') or config.get('y_columns', [])

            if x_col and x_col in data.columns:
                for y_col in y_cols[:3]:
                    if y_col in data.columns:
                        ax.plot(data[x_col], data[y_col], linestyle=line_style,
                                marker='o', markersize=3, alpha=alpha, label=y_col)
                ax.set_xlabel(custom.get('x_label') or x_col)
            else:
                for y_col in y_cols[:3]:
                    if y_col in data.columns:
                        ax.plot(data[y_col], linestyle=line_style,
                                marker='o', markersize=3, alpha=alpha, label=y_col)
                ax.set_xlabel(custom.get('x_label') or 'Index')

            if len(y_cols) > 1 and show_legend:
                ax.legend()

        elif config['data_info'].get('is_numpy'):
            shape = config['data_info']['shape']
            if len(shape) == 1:
                ax.plot(data, linestyle=line_style, marker='o', markersize=3, alpha=alpha)
            elif len(shape) == 2 and shape[1] <= 10:
                for i in range(shape[1]):
                    ax.plot(data[:, i], linestyle=line_style, marker='o',
                            markersize=3, alpha=alpha, label=f'Column {i}')
                if shape[1] > 1 and show_legend:
                    ax.legend()
            else:
                ax.plot(data[:, 0], linestyle=line_style, marker='o', markersize=3, alpha=alpha)

        elif config['data_info'].get('is_list'):
            ax.plot(data, linestyle=line_style, marker='o', markersize=3, alpha=alpha)

        ax.set_title(custom.get('title') or config.get('suggested_title', 'Line Plot'), fontweight='bold')
        ax.set_ylabel(custom.get('y_label') or 'Value')
        if show_grid:
            ax.grid(True, alpha=0.3)

    @staticmethod
    def _render_scatter(fig: Figure, data: Any, config: Dict[str, Any]):
        """Render scatter plot."""
        ax = fig.add_subplot(111)
        custom = config.get('_custom', {})

        # Get custom options
        alpha = custom.get('alpha', 0.6)
        marker_size = custom.get('marker_size', 20)
        show_grid = custom.get('show_grid', True)

        if config['data_info'].get('is_pandas'):
            x_col = custom.get('x_column') or config.get('x_column')
            y_cols = custom.get('y_columns') or config.get('y_columns', [])

            if x_col and x_col in data.columns and y_cols:
                y_col = y_cols[0] if isinstance(y_cols, list) else y_cols
                if y_col in data.columns:
                    ax.scatter(data[x_col], data[y_col], alpha=alpha, s=marker_size)
                    ax.set_xlabel(custom.get('x_label') or x_col)
                    ax.set_ylabel(custom.get('y_label') or y_col)

        elif config['data_info'].get('is_numpy'):
            shape = config['data_info']['shape']
            if len(shape) == 2 and shape[1] >= 2:
                ax.scatter(data[:, 0], data[:, 1], alpha=alpha, s=marker_size)
                ax.set_xlabel(custom.get('x_label') or 'Column 0')
                ax.set_ylabel(custom.get('y_label') or 'Column 1')

        ax.set_title(custom.get('title') or config.get('suggested_title', 'Scatter Plot'), fontweight='bold')
        if show_grid:
            ax.grid(True, alpha=0.3)

    @staticmethod
    def _render_bar(fig: Figure, data: Any, config: Dict[str, Any]):
        """Render bar chart."""
        ax = fig.add_subplot(111)
        custom = config.get('_custom', {})

        # Get custom options
        alpha = custom.get('alpha', 0.7)
        show_grid = custom.get('show_grid', True)
        aggregation = custom.get('aggregation', 'mean')

        if config['data_info'].get('is_pandas'):
            category_col = custom.get('category_column') or config.get('category_column')
            value_cols = custom.get('value_columns') or config.get('value_columns', [])

            if category_col and category_col in data.columns and value_cols:
                value_col = value_cols[0] if isinstance(value_cols, list) else value_cols
                if value_col in data.columns:
                    # Apply selected aggregation method
                    grouped = data.groupby(category_col)[value_col]
                    if aggregation == 'mean':
                        agg_data = grouped.mean()
                    elif aggregation == 'sum':
                        agg_data = grouped.sum()
                    elif aggregation == 'count':
                        agg_data = grouped.count()
                    elif aggregation == 'median':
                        agg_data = grouped.median()
                    elif aggregation == 'min':
                        agg_data = grouped.min()
                    elif aggregation == 'max':
                        agg_data = grouped.max()
                    elif aggregation == 'std':
                        agg_data = grouped.std()
                    else:
                        agg_data = grouped.mean()

                    agg_data.plot(kind='bar', ax=ax, alpha=alpha)
                    ax.set_xlabel(custom.get('x_label') or category_col)
                    ax.set_ylabel(custom.get('y_label') or f'{aggregation.capitalize()} of {value_col}')

        elif config['data_info'].get('is_dict'):
            keys = config.get('keys', [])
            values = [data[k] for k in keys]
            ax.bar(keys, values, alpha=alpha)
            ax.set_xlabel(custom.get('x_label') or 'Keys')
            ax.set_ylabel(custom.get('y_label') or 'Values')
            plt.xticks(rotation=45, ha='right')

        ax.set_title(custom.get('title') or config.get('suggested_title', 'Bar Chart'), fontweight='bold')
        if show_grid:
            ax.grid(True, alpha=0.3, axis='y')

    @staticmethod
    def _render_histogram(fig: Figure, data: Any, config: Dict[str, Any]):
        """Render histogram."""
        ax = fig.add_subplot(111)
        custom = config.get('_custom', {})

        # Get custom options
        alpha = custom.get('alpha', 0.7)
        bins = custom.get('bins', 30)
        show_grid = custom.get('show_grid', True)

        if config['data_info'].get('is_pandas'):
            column = custom.get('column') or config.get('column')
            if column and column in data.columns:
                data[column].hist(bins=bins, ax=ax, edgecolor='black', alpha=alpha)
                ax.set_xlabel(custom.get('x_label') or column)

        elif config['data_info'].get('is_numpy') or config['data_info'].get('is_list'):
            flat_data = np.array(data).flatten()
            ax.hist(flat_data, bins=bins, edgecolor='black', alpha=alpha)
            ax.set_xlabel(custom.get('x_label') or 'Value')

        ax.set_title(custom.get('title') or config.get('suggested_title', 'Histogram'), fontweight='bold')
        ax.set_ylabel(custom.get('y_label') or 'Frequency')
        if show_grid:
            ax.grid(True, alpha=0.3, axis='y')

    @staticmethod
    def _render_box(fig: Figure, data: Any, config: Dict[str, Any]):
        """Render box plot."""
        ax = fig.add_subplot(111)
        custom = config.get('_custom', {})

        # Get custom options
        show_grid = custom.get('show_grid', True)

        if config['data_info'].get('is_pandas'):
            column = custom.get('column') or config.get('column')
            if column and column in data.columns:
                data.boxplot(column=column, ax=ax)
                ax.set_xlabel(custom.get('x_label') or '')

        elif config['data_info'].get('is_numpy') or config['data_info'].get('is_list'):
            flat_data = np.array(data).flatten()
            ax.boxplot(flat_data)

        ax.set_title(custom.get('title') or config.get('suggested_title', 'Box Plot'), fontweight='bold')
        ax.set_ylabel(custom.get('y_label') or 'Value')
        if show_grid:
            ax.grid(True, alpha=0.3, axis='y')

    @staticmethod
    def _render_heatmap(fig: Figure, data: Any, config: Dict[str, Any]):
        """Render heatmap."""
        ax = fig.add_subplot(111)
        custom = config.get('_custom', {})

        # Get custom options
        color_map = custom.get('color_map', 'viridis')

        if config['data_info'].get('is_pandas'):
            im = ax.imshow(data.values, cmap=color_map, aspect='auto', interpolation='nearest')
            fig.colorbar(im, ax=ax, label='Value')

            # Smart label handling - only show labels if reasonable number
            num_cols = len(data.columns)
            num_rows = len(data)

            if num_cols <= VisualizationRenderer.MAX_TICK_LABELS:
                ax.set_xticks(range(num_cols))
                ax.set_xticklabels(data.columns, rotation=45, ha='right')
            else:
                # Show every Nth label to prevent overlap
                step = max(1, num_cols // VisualizationRenderer.MAX_TICK_LABELS)
                tick_positions = range(0, num_cols, step)
                ax.set_xticks(tick_positions)
                ax.set_xticklabels([data.columns[i] for i in tick_positions], rotation=45, ha='right')

            if num_rows <= VisualizationRenderer.MAX_TICK_LABELS:
                ax.set_yticks(range(num_rows))
                ax.set_yticklabels(data.index)
            else:
                # Show every Nth label
                step = max(1, num_rows // VisualizationRenderer.MAX_TICK_LABELS)
                tick_positions = range(0, num_rows, step)
                ax.set_yticks(tick_positions)
                ax.set_yticklabels([data.index[i] for i in tick_positions])

            ax.set_xlabel(custom.get('x_label') or 'Columns')
            ax.set_ylabel(custom.get('y_label') or 'Rows / Frames')

        elif config['data_info'].get('is_numpy'):
            im = ax.imshow(data, cmap=color_map, aspect='auto', interpolation='nearest')
            fig.colorbar(im, ax=ax, label='Value')

            # Limit tick labels for numpy arrays too
            num_cols = data.shape[1] if data.ndim > 1 else 1
            num_rows = data.shape[0]

            if num_cols > VisualizationRenderer.MAX_TICK_LABELS:
                ax.xaxis.set_major_locator(MaxNLocator(nbins=VisualizationRenderer.MAX_TICK_LABELS))
            if num_rows > VisualizationRenderer.MAX_TICK_LABELS:
                ax.yaxis.set_major_locator(MaxNLocator(nbins=VisualizationRenderer.MAX_TICK_LABELS))

            ax.set_xlabel(custom.get('x_label') or 'Column Index')
            ax.set_ylabel(custom.get('y_label') or 'Row Index')

        ax.set_title(custom.get('title') or config.get('suggested_title', 'Heatmap'), fontweight='bold')

    @staticmethod
    def _render_correlation_heatmap(fig: Figure, data: Any, config: Dict[str, Any]):
        """Render correlation heatmap."""
        ax = fig.add_subplot(111)
        custom = config.get('_custom', {})

        # Get custom options - default to RdBu_r for correlation (diverging colormap)
        color_map = custom.get('color_map', 'RdBu_r')

        if config['data_info'].get('is_pandas'):
            columns = config.get('columns', data.columns)
            # Filter to only include columns that exist in the data
            valid_columns = [c for c in columns if c in data.columns]
            if valid_columns:
                corr = data[valid_columns].corr()
            else:
                corr = data.corr()

            im = ax.imshow(corr, cmap=color_map, aspect='auto', vmin=-1, vmax=1, interpolation='nearest')
            fig.colorbar(im, ax=ax, label='Correlation')

            num_vars = len(corr.columns)

            if num_vars <= VisualizationRenderer.MAX_TICK_LABELS:
                ax.set_xticks(range(num_vars))
                ax.set_yticks(range(num_vars))
                ax.set_xticklabels(corr.columns, rotation=45, ha='right')
                ax.set_yticklabels(corr.columns)

                # Only show correlation values if matrix is small enough
                if num_vars <= 10:
                    for i in range(num_vars):
                        for j in range(num_vars):
                            color = 'white' if abs(corr.iloc[i, j]) > 0.5 else 'black'
                            ax.text(j, i, f'{corr.iloc[i, j]:.2f}',
                                   ha='center', va='center', color=color, fontsize=8)
            else:
                # Too many variables - show every Nth label
                step = max(1, num_vars // VisualizationRenderer.MAX_TICK_LABELS)
                tick_positions = range(0, num_vars, step)
                ax.set_xticks(tick_positions)
                ax.set_yticks(tick_positions)
                ax.set_xticklabels([corr.columns[i] for i in tick_positions], rotation=45, ha='right')
                ax.set_yticklabels([corr.columns[i] for i in tick_positions])

        ax.set_title(custom.get('title') or config.get('suggested_title', 'Correlation Matrix'), fontweight='bold')

    @staticmethod
    def _render_pie(fig: Figure, data: Any, config: Dict[str, Any]):
        """Render pie chart."""
        ax = fig.add_subplot(111)
        custom = config.get('_custom', {})

        if config['data_info'].get('is_dict'):
            keys = config.get('keys', [])
            values = [data[k] for k in keys]
            ax.pie(values, labels=keys, autopct='%1.1f%%', startangle=90)

        ax.set_title(custom.get('title') or config.get('suggested_title', 'Pie Chart'), fontweight='bold')

    @staticmethod
    def _render_area(fig: Figure, data: Any, config: Dict[str, Any]):
        """Render area chart."""
        ax = fig.add_subplot(111)
        custom = config.get('_custom', {})

        # Get custom options
        alpha = custom.get('alpha', 0.5)
        show_grid = custom.get('show_grid', True)
        show_legend = custom.get('show_legend', True)

        if config['data_info'].get('is_pandas'):
            x_col = custom.get('x_column') or config.get('x_column')
            y_cols = custom.get('y_columns') or config.get('y_columns', [])

            if x_col and x_col in data.columns:
                for y_col in y_cols[:3]:
                    if y_col in data.columns:
                        ax.fill_between(data[x_col], data[y_col], alpha=alpha, label=y_col)
                ax.set_xlabel(custom.get('x_label') or x_col)
            else:
                for y_col in y_cols[:3]:
                    if y_col in data.columns:
                        ax.fill_between(range(len(data)), data[y_col], alpha=alpha, label=y_col)
                ax.set_xlabel(custom.get('x_label') or 'Index')

            if len(y_cols) > 1 and show_legend:
                ax.legend()

        ax.set_title(custom.get('title') or config.get('suggested_title', 'Area Chart'), fontweight='bold')
        ax.set_ylabel(custom.get('y_label') or 'Value')
        if show_grid:
            ax.grid(True, alpha=0.3)

    @staticmethod
    def _render_text(fig: Figure, data: Any, config: Dict[str, Any]):
        """Render text representation when no visualization is appropriate."""
        ax = fig.add_subplot(111)
        custom = config.get('_custom', {})
        ax.axis('off')

        data_str = str(data)[:500]
        if len(str(data)) > 500:
            data_str += "\n..."

        ax.text(0.5, 0.5, data_str, transform=ax.transAxes,
               ha='center', va='center', wrap=True, fontfamily='monospace')

        ax.set_title(custom.get('title') or config.get('suggested_title', 'Data Preview'), fontweight='bold')

    @staticmethod
    def export_figure(fig: Figure, file_path: str, format: str = 'png', dpi: int = 300):
        """
        Export figure to file.

        Args:
            fig: Matplotlib figure
            file_path: Output file path
            format: Output format (png, svg, pdf)
            dpi: Dots per inch for raster formats
        """
        fig.savefig(file_path, format=format, bbox_inches='tight', dpi=dpi)

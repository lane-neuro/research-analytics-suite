"""
Operation:      OutlierDetection
Version:        0.0.1
Description:    Detect outliers in a numerical series using IQR or z-score methods.

Author:         Lane
GitHub:         lane-neuro
Email:          justlane@uw.edu

---
Part of the Research Analytics Suite
    https://github.com/lane-neuro/research-analytics-suite
License:        BSD 3-Clause License
Maintainer:     Lane (GitHub: @lane-neuro)
Status:         In Progress
"""
from typing import Optional, Type
from research_analytics_suite.operation_manager import BaseOperation


class OutlierDetection(BaseOperation):
    """
    Detect outliers in a numerical series using IQR fences or z-score thresholding.

    Requires:
        series (list): Numerical values to inspect.
        method (str): "iqr" or "zscore" (default "iqr").
        threshold (float): Z-score threshold when method is "zscore" (default 3.0).

    Returns:
        outlier_indices (list): Zero-based indices of detected outlier values.
        outlier_values (list): Corresponding outlier values.
        n_outliers (int): Total number of outliers detected.
        method (str): Method used.
        bounds (dict): Lower and upper bounds used for detection.
    """
    name = "OutlierDetection"
    version = "0.0.1"
    description = "Detect outliers in a numerical series using IQR or z-score methods."
    category_id = 601
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"series": list, "method": str, "threshold": float}
    parent_operation: Optional[Type[BaseOperation]] = None
    inheritance: Optional[list] = []
    is_loop = False
    is_cpu_bound = False
    parallel = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def initialize_operation(self):
        await super().initialize_operation()

    async def execute(self):
        import numpy as np
        from scipy import stats as scipy_stats

        _inputs = self.get_inputs()
        series = _inputs.get("series", [])
        method = str(_inputs.get("method", "iqr")).lower()
        threshold = float(_inputs.get("threshold", 3.0))

        arr = np.array(series, dtype=float)

        if method == "zscore":
            z_scores = np.abs(scipy_stats.zscore(arr))
            mask = z_scores > threshold
            lower = float(np.mean(arr) - threshold * np.std(arr))
            upper = float(np.mean(arr) + threshold * np.std(arr))
        else:
            q1 = float(np.percentile(arr, 25))
            q3 = float(np.percentile(arr, 75))
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            mask = (arr < lower) | (arr > upper)

        outlier_indices = [int(i) for i in np.where(mask)[0]]
        outlier_values = [float(arr[i]) for i in outlier_indices]

        self.add_log_entry(
            f"[RESULT] method={method}; {len(outlier_indices)} outliers detected; "
            f"bounds=[{lower:.4f}, {upper:.4f}]"
        )
        return {
            "outlier_indices": outlier_indices,
            "outlier_values": outlier_values,
            "n_outliers": len(outlier_indices),
            "method": method,
            "bounds": {"lower": float(lower), "upper": float(upper)},
        }

"""
Operation:      RobustScaling
Version:        0.0.1
Description:    Scale a numerical series using median and IQR, robust to outliers.

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


class RobustScaling(BaseOperation):
    """
    Scale a numerical series using the median and interquartile range.
    More robust to outliers than z-score or min-max scaling.

    Requires:
        series (list): Numerical values to scale.

    Returns:
        scaled (list): Robustly scaled values.
        median (float): Median of the original series.
        iqr (float): Interquartile range of the original series.
    """
    name = "RobustScaling"
    version = "0.0.1"
    description = "Scale a numerical series using median and IQR, robust to outliers."
    category_id = 603
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"series": list}
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

        _inputs = self.get_inputs()
        series = _inputs.get("series", [])

        arr = np.array(series, dtype=float)
        median = float(np.median(arr))
        q1 = float(np.percentile(arr, 25))
        q3 = float(np.percentile(arr, 75))
        iqr = q3 - q1

        if iqr == 0.0:
            scaled = [0.0] * len(arr)
        else:
            scaled = [float((v - median) / iqr) for v in arr]

        self.add_log_entry(
            f"[RESULT] Scaled {len(arr)} values; median={median:.4f}; IQR={iqr:.4f}"
        )
        return {"scaled": scaled, "median": median, "iqr": float(iqr)}

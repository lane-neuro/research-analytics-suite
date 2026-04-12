"""
Operation:      MinMaxScaling
Version:        0.0.1
Description:    Scale a numerical series to a specified feature range using min-max normalization.

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


class MinMaxScaling(BaseOperation):
    """
    Scale a numerical series to a specified feature range using min-max normalization.

    Requires:
        series (list): Numerical values to scale.
        feature_range_min (float): Minimum of the output range (default 0.0).
        feature_range_max (float): Maximum of the output range (default 1.0).

    Returns:
        scaled (list): Scaled values.
        original_min (float): Minimum of the original series.
        original_max (float): Maximum of the original series.
        feature_range (list): [feature_range_min, feature_range_max] used.
    """
    name = "MinMaxScaling"
    version = "0.0.1"
    description = "Scale a numerical series to a specified feature range using min-max normalization."
    category_id = 603
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"series": list, "feature_range_min": float, "feature_range_max": float}
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
        range_min = float(_inputs.get("feature_range_min", 0.0))
        range_max = float(_inputs.get("feature_range_max", 1.0))

        arr = np.array(series, dtype=float)
        orig_min = float(np.min(arr))
        orig_max = float(np.max(arr))

        if orig_max == orig_min:
            scaled = [0.0] * len(arr)
        else:
            scaled = [
                float((v - orig_min) / (orig_max - orig_min) * (range_max - range_min) + range_min)
                for v in arr
            ]

        self.add_log_entry(
            f"[RESULT] Scaled {len(arr)} values from [{orig_min:.4f}, {orig_max:.4f}] "
            f"to [{range_min}, {range_max}]"
        )
        return {
            "scaled": scaled,
            "original_min": orig_min,
            "original_max": orig_max,
            "feature_range": [range_min, range_max],
        }

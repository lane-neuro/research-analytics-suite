"""
Operation:      InterpolationOperation
Version:        0.0.1
Description:    Interpolate missing values in a numerical series using a specified method.

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
from typing import List, Optional, Type
from research_analytics_suite.operation_manager import BaseOperation


class InterpolationOperation(BaseOperation):
    """
    Interpolate missing (NaN) values in a numerical series.

    Requires:
        series (list): A list of numerical values, may contain None/NaN.
        method (str): Interpolation method — 'linear', 'nearest', or 'zero'
                      (default: 'linear').

    Returns:
        interpolated (list): Series with missing values filled.
    """
    name = "InterpolationOperation"
    version = "0.0.1"
    description = "Interpolate missing values in a numerical series."
    category_id = 602
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"series": list, "method": str}
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
        import pandas as pd
        _inputs = self.get_inputs()
        series = _inputs.get("series", [])
        method = str(_inputs.get("method", "linear"))

        s = pd.Series(series, dtype=float)
        interpolated = s.interpolate(method=method).tolist()

        filled = sum(1 for a, b in zip(series, interpolated) if a != b and b == b)
        self.add_log_entry(f"[RESULT] Interpolated {filled} missing value(s) using '{method}' method.")
        return {"interpolated": interpolated}

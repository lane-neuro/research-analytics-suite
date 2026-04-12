"""
Operation:      LogTransformation
Version:        0.0.1
Description:    Apply a logarithmic transformation to reduce skewness in a numerical series.

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


class LogTransformation(BaseOperation):
    """
    Apply a logarithmic transformation to a numerical series.
    Supports log (natural), log2, and log1p. For log and log2, an offset can be added
    before the transformation to handle zeros.

    Requires:
        series (list): Numerical values to transform.
        method (str): "log", "log2", or "log1p" (default "log1p").
        offset (float): Value added to each element before applying log or log2 (default 0.0).

    Returns:
        transformed (list): Transformed values (NaN-replaced with None for invalid inputs).
        method (str): Transformation method used.
        offset (float): Offset used.
        n_invalid (int): Count of values that were non-positive after offset (set to None).
    """
    name = "LogTransformation"
    version = "0.0.1"
    description = "Apply a logarithmic transformation to reduce skewness in a numerical series."
    category_id = 603
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"series": list, "method": str, "offset": float}
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
        method = str(_inputs.get("method", "log1p")).lower()
        offset = float(_inputs.get("offset", 0.0))

        arr = np.array(series, dtype=float)

        if method == "log1p":
            result = np.log1p(arr)
            n_invalid = int(np.sum(arr < -1.0))
        elif method == "log2":
            shifted = arr + offset
            result = np.where(shifted > 0.0, np.log2(shifted), np.nan)
            n_invalid = int(np.sum(shifted <= 0.0))
        else:
            shifted = arr + offset
            result = np.where(shifted > 0.0, np.log(shifted), np.nan)
            n_invalid = int(np.sum(shifted <= 0.0))

        transformed = [None if np.isnan(v) else float(v) for v in result]

        self.add_log_entry(
            f"[RESULT] method={method}; offset={offset}; "
            f"{n_invalid} invalid values (non-positive before log)"
        )
        return {
            "transformed": transformed,
            "method": method,
            "offset": offset,
            "n_invalid": n_invalid,
        }

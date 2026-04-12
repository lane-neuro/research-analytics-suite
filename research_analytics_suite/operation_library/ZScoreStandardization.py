"""
Operation:      ZScoreStandardization
Version:        0.0.1
Description:    Standardize a numerical series to zero mean and unit variance (z-score normalization).

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


class ZScoreStandardization(BaseOperation):
    """
    Standardize a numerical series to zero mean and unit variance.

    Requires:
        series (list): Numerical values to standardize.

    Returns:
        standardized (list): Z-score standardized values.
        mean (float): Mean of the original series.
        std (float): Standard deviation of the original series.
    """
    name = "ZScoreStandardization"
    version = "0.0.1"
    description = "Standardize a numerical series to zero mean and unit variance (z-score normalization)."
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
        mean = float(np.mean(arr))
        std = float(np.std(arr, ddof=0))

        if std == 0.0:
            standardized = [0.0] * len(arr)
        else:
            standardized = [float((v - mean) / std) for v in arr]

        self.add_log_entry(
            f"[RESULT] Standardized {len(arr)} values; mean={mean:.4f}; std={std:.4f}"
        )
        return {"standardized": standardized, "mean": mean, "std": std}

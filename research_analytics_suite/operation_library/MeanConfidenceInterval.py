"""
Operation:      MeanConfidenceInterval
Version:        0.0.1
Description:    Calculate the confidence interval for a sample mean using the t-distribution.

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


class MeanConfidenceInterval(BaseOperation):
    """
    Calculate the confidence interval for a sample mean using the t-distribution.

    Requires:
        sample (list): A list of numerical values.
        alpha (float): Significance level (default 0.05 for 95% CI).

    Returns:
        mean (float): Sample mean.
        ci_lower (float): Lower bound of the confidence interval.
        ci_upper (float): Upper bound of the confidence interval.
        margin_of_error (float): Half-width of the confidence interval.
        method (str): Interval method used.
    """
    name = "MeanConfidenceInterval"
    version = "0.0.1"
    description = "Calculate the confidence interval for a sample mean using the t-distribution."
    category_id = 203
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"sample": list, "alpha": float}
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
        from scipy import stats

        _inputs = self.get_inputs()
        sample = _inputs.get("sample", [])
        alpha = float(_inputs.get("alpha", 0.05))

        arr = np.array(sample, dtype=float)
        n = len(arr)
        mean = float(np.mean(arr))
        sem = float(stats.sem(arr))
        ci_lower, ci_upper = stats.t.interval(1.0 - alpha, df=n - 1, loc=mean, scale=sem)
        margin_of_error = float((ci_upper - ci_lower) / 2.0)

        self.add_log_entry(
            f"[RESULT] Mean: {mean}; CI [{ci_lower:.4f}, {ci_upper:.4f}]; alpha={alpha}"
        )
        return {
            "mean": mean,
            "ci_lower": float(ci_lower),
            "ci_upper": float(ci_upper),
            "margin_of_error": margin_of_error,
            "method": "t-interval",
        }

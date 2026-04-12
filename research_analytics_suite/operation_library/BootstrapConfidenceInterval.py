"""
Operation:      BootstrapConfidenceInterval
Version:        0.0.1
Description:    Calculate a bootstrap confidence interval for a chosen statistic.

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


class BootstrapConfidenceInterval(BaseOperation):
    """
    Calculate a non-parametric bootstrap confidence interval for a chosen statistic.

    Requires:
        sample (list): A list of numerical values.
        statistic (str): One of "mean", "median", or "std" (default "mean").
        n_resamples (int): Number of bootstrap resamples (default 1000).
        alpha (float): Significance level (default 0.05 for 95% CI).

    Returns:
        observed (float): Observed statistic on the original sample.
        ci_lower (float): Lower bound of the bootstrap confidence interval.
        ci_upper (float): Upper bound of the bootstrap confidence interval.
        n_resamples (int): Number of resamples used.
    """
    name = "BootstrapConfidenceInterval"
    version = "0.0.1"
    description = "Calculate a bootstrap confidence interval for a chosen statistic."
    category_id = 203
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"sample": list, "statistic": str, "n_resamples": int, "alpha": float}
    parent_operation: Optional[Type[BaseOperation]] = None
    inheritance: Optional[list] = []
    is_loop = False
    is_cpu_bound = True
    parallel = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def initialize_operation(self):
        await super().initialize_operation()

    async def execute(self):
        import numpy as np

        _inputs = self.get_inputs()
        sample = _inputs.get("sample", [])
        statistic = str(_inputs.get("statistic", "mean"))
        n_resamples = int(_inputs.get("n_resamples", 1000))
        alpha = float(_inputs.get("alpha", 0.05))

        arr = np.array(sample, dtype=float)
        stat_funcs = {"mean": np.mean, "median": np.median, "std": np.std}
        func = stat_funcs.get(statistic, np.mean)
        observed = float(func(arr))

        rng = np.random.default_rng()
        boot_stats = [
            float(func(rng.choice(arr, size=len(arr), replace=True)))
            for _ in range(n_resamples)
        ]
        ci_lower = float(np.percentile(boot_stats, 100.0 * (alpha / 2.0)))
        ci_upper = float(np.percentile(boot_stats, 100.0 * (1.0 - alpha / 2.0)))

        self.add_log_entry(
            f"[RESULT] {statistic}={observed:.4f}; bootstrap CI [{ci_lower:.4f}, {ci_upper:.4f}];"
            f" n_resamples={n_resamples}"
        )
        return {
            "observed": observed,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "n_resamples": n_resamples,
        }

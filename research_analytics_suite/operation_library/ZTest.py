"""
Operation:      ZTest
Version:        0.0.1
Description:    Perform a one-sample z-test against a known population mean and standard deviation.

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


class ZTest(BaseOperation):
    """
    Perform a one-sample z-test against a known population mean and standard deviation.

    Requires:
        sample (list): Sample observations.
        popmean (float): Known population mean under the null hypothesis.
        popstd (float): Known population standard deviation.

    Returns:
        z_stat (float): The z-statistic.
        p_value (float): Two-sided p-value.
        sample_mean (float): Observed sample mean.
        n (int): Sample size.
    """
    name = "ZTest"
    version = "0.0.1"
    description = "Perform a one-sample z-test against a known population mean and standard deviation."
    category_id = 201
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"sample": list, "popmean": float, "popstd": float}
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
        popmean = float(_inputs.get("popmean", 0.0))
        popstd = float(_inputs.get("popstd", 1.0))

        arr = np.array(sample, dtype=float)
        n = len(arr)
        sample_mean = float(np.mean(arr))
        z_stat = float((sample_mean - popmean) / (popstd / np.sqrt(n)))
        p_value = float(2.0 * (1.0 - stats.norm.cdf(abs(z_stat))))

        self.add_log_entry(f"[RESULT] Z-statistic: {z_stat:.4f}; p-value: {p_value:.4f}")
        return {
            "z_stat": z_stat,
            "p_value": p_value,
            "sample_mean": sample_mean,
            "n": int(n),
        }

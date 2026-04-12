"""
Operation:      KolmogorovSmirnovTest
Version:        0.0.1
Description:    Perform a two-sample Kolmogorov-Smirnov test to compare two distributions.

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


class KolmogorovSmirnovTest(BaseOperation):
    """
    Perform a two-sample Kolmogorov-Smirnov test to compare two distributions.

    Requires:
        sample1 (list): First sample of numerical values.
        sample2 (list): Second sample of numerical values.

    Returns:
        ks_stat (float): The KS test statistic.
        p_value (float): The p-value.
    """
    name = "KolmogorovSmirnovTest"
    version = "0.0.1"
    description = "Perform a two-sample Kolmogorov-Smirnov test to compare two distributions."
    category_id = 202
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"sample1": list, "sample2": list}
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
        from scipy import stats

        _inputs = self.get_inputs()
        sample1 = _inputs.get("sample1", [])
        sample2 = _inputs.get("sample2", [])

        ks_stat, p_value = stats.ks_2samp(sample1, sample2)
        self.add_log_entry(f"[RESULT] KS-statistic: {ks_stat:.4f}; p-value: {p_value:.4f}")
        return {"ks_stat": float(ks_stat), "p_value": float(p_value)}

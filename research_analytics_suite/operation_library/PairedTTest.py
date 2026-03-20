"""
Operation:      PairedTTest
Version:        0.0.1
Description:    Perform a paired (dependent) t-test on two related samples.

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


class PairedTTest(BaseOperation):
    """
    Perform a paired (dependent) t-test on two related samples.

    Requires:
        sample1 (list): First set of paired measurements.
        sample2 (list): Second set of paired measurements (same length as sample1).

    Returns:
        t_stat (float): The t-statistic.
        p_value (float): The p-value.
    """
    name = "PairedTTest"
    version = "0.0.1"
    description = "Perform a paired (dependent) t-test on two related samples."
    category_id = 301
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

        t_stat, p_value = stats.ttest_rel(sample1, sample2)
        self.add_log_entry(f"[RESULT] t-Statistic: {t_stat}; p-Value: {p_value}")
        return {"t_stat": float(t_stat), "p_value": float(p_value)}

"""
Operation:      MannWhitneyTest
Version:        0.0.1
Description:    Perform the Mann-Whitney U (Wilcoxon rank-sum) non-parametric test.

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


class MannWhitneyTest(BaseOperation):
    """
    Perform the Mann-Whitney U (Wilcoxon rank-sum) non-parametric test.

    Requires:
        sample1 (list): First independent sample.
        sample2 (list): Second independent sample.

    Returns:
        u_stat (float): The Mann-Whitney U statistic.
        p_value (float): The p-value.
    """
    name = "MannWhitneyTest"
    version = "0.0.1"
    description = "Perform the Mann-Whitney U non-parametric test."
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

        u_stat, p_value = stats.mannwhitneyu(sample1, sample2, alternative="two-sided")
        self.add_log_entry(f"[RESULT] U-Statistic: {u_stat}; p-Value: {p_value}")
        return {"u_stat": float(u_stat), "p_value": float(p_value)}

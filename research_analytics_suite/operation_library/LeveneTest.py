"""
Operation:      LeveneTest
Version:        0.0.1
Description:    Test equality of variances across groups using Levene's test.

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


class LeveneTest(BaseOperation):
    """
    Test equality of variances across two or more groups using Levene's test.

    Requires:
        groups (list): A list of lists, each inner list containing numerical values for one group.

    Returns:
        w_stat (float): Levene's W-statistic.
        p_value (float): The p-value.
    """
    name = "LeveneTest"
    version = "0.0.1"
    description = "Test equality of variances across groups using Levene's test."
    category_id = 201
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"groups": list}
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
        groups = _inputs.get("groups", [])

        w_stat, p_value = stats.levene(*groups)
        self.add_log_entry(f"[RESULT] W-statistic: {w_stat:.4f}; p-value: {p_value:.4f}")
        return {"w_stat": float(w_stat), "p_value": float(p_value)}

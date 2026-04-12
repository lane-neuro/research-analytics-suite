"""
Operation:      KruskalWallisTest
Version:        0.0.1
Description:    Perform the Kruskal-Wallis H-test across two or more independent groups.

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


class KruskalWallisTest(BaseOperation):
    """
    Perform the Kruskal-Wallis H-test across two or more independent groups.
    Non-parametric alternative to one-way ANOVA.

    Requires:
        groups (list): A list of lists, each inner list containing numerical values for one group.

    Returns:
        h_stat (float): The Kruskal-Wallis H-statistic.
        p_value (float): The p-value.
    """
    name = "KruskalWallisTest"
    version = "0.0.1"
    description = "Perform the Kruskal-Wallis H-test across two or more independent groups."
    category_id = 202
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

        h_stat, p_value = stats.kruskal(*groups)
        self.add_log_entry(f"[RESULT] H-statistic: {h_stat:.4f}; p-value: {p_value:.4f}")
        return {"h_stat": float(h_stat), "p_value": float(p_value)}

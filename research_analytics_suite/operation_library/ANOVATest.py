"""
Operation:      ANOVATest
Version:        0.0.1
Description:    Perform a one-way ANOVA test across multiple groups.

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


class ANOVATest(BaseOperation):
    """
    Perform a one-way ANOVA test across multiple groups.

    Requires:
        groups (list): A list of lists, each inner list is a group of numerical values.

    Returns:
        f_stat (float): The F-statistic.
        p_value (float): The p-value.
    """
    name = "ANOVATest"
    version = "0.0.1"
    description = "Perform a one-way ANOVA test across multiple groups."
    category_id = 303
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

        f_stat, p_value = stats.f_oneway(*groups)
        self.add_log_entry(f"[RESULT] F-statistic: {f_stat}; p-Value: {p_value}")
        return {"f_stat": float(f_stat), "p_value": float(p_value)}

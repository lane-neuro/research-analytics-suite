"""
Operation:      FisherExactTest
Version:        0.0.1
Description:    Perform Fisher's exact test on a 2x2 contingency table.

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


class FisherExactTest(BaseOperation):
    """
    Perform Fisher's exact test on a 2x2 contingency table.
    Preferred over chi-square for small sample sizes.

    Requires:
        table (list): A 2x2 contingency table as a list of two lists, e.g. [[a, b], [c, d]].

    Returns:
        odds_ratio (float): The odds ratio.
        p_value (float): Two-sided p-value.
    """
    name = "FisherExactTest"
    version = "0.0.1"
    description = "Perform Fisher's exact test on a 2x2 contingency table."
    category_id = 302
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"table": list}
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
        table = _inputs.get("table", [[1, 1], [1, 1]])

        odds_ratio, p_value = stats.fisher_exact(table, alternative="two-sided")
        self.add_log_entry(
            f"[RESULT] Odds ratio: {odds_ratio:.4f}; p-value: {p_value:.4f}"
        )
        return {"odds_ratio": float(odds_ratio), "p_value": float(p_value)}

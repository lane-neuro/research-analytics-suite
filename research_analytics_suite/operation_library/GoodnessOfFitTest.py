"""
Operation:      GoodnessOfFitTest
Version:        0.0.1
Description:    Perform a chi-square goodness-of-fit test comparing observed to expected frequencies.

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


class GoodnessOfFitTest(BaseOperation):
    """
    Perform a chi-square goodness-of-fit test comparing observed to expected frequencies.
    If expected is empty, assumes a uniform distribution.

    Requires:
        observed (list): Observed frequency counts.
        expected (list): Expected frequency counts. Pass an empty list for uniform distribution.

    Returns:
        chi2_stat (float): The chi-square test statistic.
        p_value (float): The p-value.
        dof (int): Degrees of freedom.
    """
    name = "GoodnessOfFitTest"
    version = "0.0.1"
    description = "Perform a chi-square goodness-of-fit test comparing observed to expected frequencies."
    category_id = 302
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"observed": list, "expected": list}
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
        observed = _inputs.get("observed", [])
        expected = _inputs.get("expected", [])

        f_exp = expected if expected else None
        chi2_stat, p_value = stats.chisquare(observed, f_exp=f_exp)
        dof = len(observed) - 1

        self.add_log_entry(
            f"[RESULT] Chi2-statistic: {chi2_stat:.4f}; p-value: {p_value:.4f}; dof: {dof}"
        )
        return {"chi2_stat": float(chi2_stat), "p_value": float(p_value), "dof": int(dof)}

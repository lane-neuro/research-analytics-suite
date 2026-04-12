"""
Operation:      ProportionConfidenceInterval
Version:        0.0.1
Description:    Calculate the Wilson score confidence interval for a proportion.

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


class ProportionConfidenceInterval(BaseOperation):
    """
    Calculate the Wilson score confidence interval for a proportion.

    Requires:
        successes (int): Number of successes.
        n (int): Total number of trials.
        alpha (float): Significance level (default 0.05 for 95% CI).

    Returns:
        proportion (float): Observed proportion (successes / n).
        ci_lower (float): Lower bound of the confidence interval.
        ci_upper (float): Upper bound of the confidence interval.
        method (str): Interval method used.
    """
    name = "ProportionConfidenceInterval"
    version = "0.0.1"
    description = "Calculate the Wilson score confidence interval for a proportion."
    category_id = 203
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"successes": int, "n": int, "alpha": float}
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
        from statsmodels.stats.proportion import proportion_confint

        _inputs = self.get_inputs()
        successes = int(_inputs.get("successes", 0))
        n = int(_inputs.get("n", 1))
        alpha = float(_inputs.get("alpha", 0.05))

        proportion = float(successes / n) if n > 0 else 0.0
        ci_lower, ci_upper = proportion_confint(successes, n, alpha=alpha, method="wilson")

        self.add_log_entry(
            f"[RESULT] Proportion: {proportion:.4f}; CI [{ci_lower:.4f}, {ci_upper:.4f}]; alpha={alpha}"
        )
        return {
            "proportion": proportion,
            "ci_lower": float(ci_lower),
            "ci_upper": float(ci_upper),
            "method": "wilson",
        }

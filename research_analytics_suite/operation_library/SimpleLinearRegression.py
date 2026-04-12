"""
Operation:      SimpleLinearRegression
Version:        0.0.1
Description:    Perform simple linear regression with residual diagnostics.

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


class SimpleLinearRegression(BaseOperation):
    """
    Perform simple linear regression (one predictor, one response) with diagnostics.

    Requires:
        x (list): Independent variable values.
        y (list): Dependent variable values.

    Returns:
        slope (float): Regression slope.
        intercept (float): Regression intercept.
        r_squared (float): Coefficient of determination.
        p_value (float): p-value for the slope.
        std_err (float): Standard error of the slope.
        r_value (float): Pearson correlation coefficient.
    """
    name = "SimpleLinearRegression"
    version = "0.0.1"
    description = "Perform simple linear regression with residual diagnostics."
    category_id = 401
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"x": list, "y": list}
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
        x = _inputs.get("x", [])
        y = _inputs.get("y", [])

        result = stats.linregress(x, y)
        self.add_log_entry(
            f"[RESULT] slope={result.slope:.4f}; intercept={result.intercept:.4f}; "
            f"R2={result.rvalue ** 2:.4f}; p={result.pvalue:.4f}"
        )
        return {
            "slope": float(result.slope),
            "intercept": float(result.intercept),
            "r_squared": float(result.rvalue ** 2),
            "p_value": float(result.pvalue),
            "std_err": float(result.stderr),
            "r_value": float(result.rvalue),
        }

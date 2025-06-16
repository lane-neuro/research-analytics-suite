"""
Operation:      RegressionAnalysis
Version:        0.0.1
Description:    Perform regression analysis on a dataset.

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
import statsmodels.api as sm
from typing import Optional, Type
from research_analytics_suite.operation_manager import BaseOperation


class RegressionAnalysis(BaseOperation):
    """
    Perform regression analysis on a dataset.

    Requires:
        x (list): The independent variables.
        y (list): The dependent variable.

    Returns:
        params (list): The estimated coefficients for the regression model.
        rsquared (float): The R-squared value of the model.
        pvalues (list): The p-values for the coefficients.
        conf_int (list): The confidence intervals for the coefficients.
        summary (str): A summary of the regression model.
    """
    name = "RegressionAnalysis"
    version = "0.0.1"
    description = "Perform regression analysis on a dataset."
    category_id = 1202
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    unique_id = f"{github}_{name}_{version}"
    required_inputs = {"x": list, "y": list}
    parent_operation: Optional[Type[BaseOperation]] = None
    inheritance: Optional[list] = []
    is_loop = False
    is_cpu_bound = False
    parallel = False

    def __init__(self, *args, **kwargs):
        """
        Initialize the operation.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)

    async def initialize_operation(self):
        """
        Initialize any resources or setup required for the operation before it starts.
        """
        await super().initialize_operation()

    async def execute(self):
        """
        Execute the operation's logic: perform regression analysis on the dataset.
        """
        _inputs = self.get_inputs()
        _x = _inputs.get("x", [])
        _y = _inputs.get("y", [])

        x_with_const = sm.add_constant(_x)
        model = sm.OLS(_y, x_with_const).fit()
        self.add_log_entry(f"[RESULT] Regression Model Summary:\n{model.summary()} \nCoefficients: {model.params} "
                           f"\nR-squared: {model.rsquared} \nP-values: {model.pvalues} "
                           f"\nConfidence Intervals: {model.conf_int()}")
        return {
            "params": model.params.tolist(),
            "rsquared": model.rsquared,
            "pvalues": model.pvalues.tolist(),
            "conf_int": model.conf_int().tolist(),
            "summary": str(model.summary())
        }

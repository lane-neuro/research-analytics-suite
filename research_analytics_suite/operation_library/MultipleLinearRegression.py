"""
Operation:      MultipleLinearRegression
Version:        0.0.1
Description:    Perform multiple linear regression with VIF, AIC, and BIC diagnostics.

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


class MultipleLinearRegression(BaseOperation):
    """
    Perform multiple linear regression using OLS with VIF, AIC, and BIC diagnostics.

    Requires:
        X (list): List of lists -- each inner list is one observation's predictor values.
        y (list): Dependent variable values.

    Returns:
        params (list): Estimated coefficients (including intercept as first element).
        p_values (list): p-values for each coefficient.
        r_squared (float): R-squared.
        adj_r_squared (float): Adjusted R-squared.
        aic (float): Akaike information criterion.
        bic (float): Bayesian information criterion.
        vif (list): Variance inflation factors for each predictor (excluding intercept).
    """
    name = "MultipleLinearRegression"
    version = "0.0.1"
    description = "Perform multiple linear regression with VIF, AIC, and BIC diagnostics."
    category_id = 402
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"X": list, "y": list}
    parent_operation: Optional[Type[BaseOperation]] = None
    inheritance: Optional[list] = []
    is_loop = False
    is_cpu_bound = True
    parallel = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def initialize_operation(self):
        await super().initialize_operation()

    async def execute(self):
        import numpy as np
        import statsmodels.api as sm
        from statsmodels.stats.outliers_influence import variance_inflation_factor

        _inputs = self.get_inputs()
        X = _inputs.get("X", [])
        y = _inputs.get("y", [])

        X_arr = np.array(X, dtype=float)
        y_arr = np.array(y, dtype=float)
        X_with_const = sm.add_constant(X_arr)

        model = sm.OLS(y_arr, X_with_const).fit()

        vif = [
            float(variance_inflation_factor(X_with_const, i + 1))
            for i in range(X_arr.shape[1])
        ]

        self.add_log_entry(
            f"[RESULT] n_predictors={X_arr.shape[1]}; R2={model.rsquared:.4f}; "
            f"adj_R2={model.rsquared_adj:.4f}"
        )
        return {
            "params": [float(p) for p in model.params],
            "p_values": [float(p) for p in model.pvalues],
            "r_squared": float(model.rsquared),
            "adj_r_squared": float(model.rsquared_adj),
            "aic": float(model.aic),
            "bic": float(model.bic),
            "vif": vif,
        }

"""
Operation:      RobustRegression
Version:        0.0.1
Description:    Perform robust linear regression using an M-estimator (HuberT) to reduce outlier influence.

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


class RobustRegression(BaseOperation):
    """
    Perform robust linear regression using statsmodels RLM with a HuberT M-estimator.

    Requires:
        x (list): Independent variable values (one predictor).
        y (list): Dependent variable values.

    Returns:
        params (list): Estimated coefficients [intercept, slope].
        p_values (list): p-values for each coefficient.
        r_squared_approx (float): Approximate R-squared (1 - resid.var() / y.var()).
    """
    name = "RobustRegression"
    version = "0.0.1"
    description = "Perform robust linear regression using an M-estimator (HuberT) to reduce outlier influence."
    category_id = 401
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"x": list, "y": list}
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

        _inputs = self.get_inputs()
        x = _inputs.get("x", [])
        y = _inputs.get("y", [])

        x_arr = sm.add_constant(np.array(x, dtype=float))
        y_arr = np.array(y, dtype=float)

        model = sm.RLM(y_arr, x_arr, M=sm.robust.norms.HuberT()).fit()
        r_squared_approx = float(
            1.0 - model.resid.var() / y_arr.var()
        ) if y_arr.var() != 0.0 else 0.0

        self.add_log_entry(
            f"[RESULT] params={[round(float(p), 6) for p in model.params]}; "
            f"approx R2={r_squared_approx:.4f}"
        )
        return {
            "params": [float(p) for p in model.params],
            "p_values": [float(p) for p in model.pvalues],
            "r_squared_approx": r_squared_approx,
        }

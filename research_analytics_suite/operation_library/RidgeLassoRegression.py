"""
Operation:      RidgeLassoRegression
Version:        0.0.1
Description:    Perform regularized regression using Ridge, Lasso, or ElasticNet.

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


class RidgeLassoRegression(BaseOperation):
    """
    Perform regularized linear regression using Ridge, Lasso, or ElasticNet.

    Requires:
        X (list): List of lists -- each inner list is one observation's predictor values.
        y (list): Dependent variable values.
        method (str): "ridge", "lasso", or "elasticnet" (default "ridge").
        alpha (float): Regularization strength (default 1.0).

    Returns:
        coefficients (list): Fitted coefficients for each predictor.
        intercept (float): Fitted intercept.
        r_squared (float): R-squared on the training data.
        method (str): Method used.
        alpha (float): Regularization strength used.
    """
    name = "RidgeLassoRegression"
    version = "0.0.1"
    description = "Perform regularized regression using Ridge, Lasso, or ElasticNet."
    category_id = 402
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"X": list, "y": list, "method": str, "alpha": float}
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
        from sklearn.linear_model import Ridge, Lasso, ElasticNet

        _inputs = self.get_inputs()
        X = _inputs.get("X", [])
        y = _inputs.get("y", [])
        method = str(_inputs.get("method", "ridge")).lower()
        alpha = float(_inputs.get("alpha", 1.0))

        X_arr = np.array(X, dtype=float)
        y_arr = np.array(y, dtype=float)

        models = {"ridge": Ridge, "lasso": Lasso, "elasticnet": ElasticNet}
        model_cls = models.get(method, Ridge)
        model = model_cls(alpha=alpha, max_iter=10000)
        model.fit(X_arr, y_arr)

        r_squared = float(model.score(X_arr, y_arr))
        n_nonzero = int(np.sum(model.coef_ != 0.0))

        self.add_log_entry(
            f"[RESULT] method={method}; alpha={alpha}; R2={r_squared:.4f}; "
            f"non-zero coefficients={n_nonzero}/{len(model.coef_)}"
        )
        return {
            "coefficients": [float(c) for c in model.coef_],
            "intercept": float(model.intercept_),
            "r_squared": r_squared,
            "method": method,
            "alpha": alpha,
        }

"""
Operation:      PolynomialRegression
Version:        0.0.1
Description:    Fit a polynomial regression of a specified degree to x-y data.

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


class PolynomialRegression(BaseOperation):
    """
    Fit a polynomial regression of a specified degree to x-y data.

    Requires:
        x (list): Independent variable values.
        y (list): Dependent variable values.
        degree (int): Degree of the polynomial (default 2).

    Returns:
        coefficients (list): Polynomial coefficients from highest to lowest degree.
        r_squared (float): Coefficient of determination on the training data.
        degree (int): Degree used.
    """
    name = "PolynomialRegression"
    version = "0.0.1"
    description = "Fit a polynomial regression of a specified degree to x-y data."
    category_id = 401
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"x": list, "y": list, "degree": int}
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

        _inputs = self.get_inputs()
        x = _inputs.get("x", [])
        y = _inputs.get("y", [])
        degree = int(_inputs.get("degree", 2))

        x_arr = np.array(x, dtype=float)
        y_arr = np.array(y, dtype=float)

        coeffs = np.polyfit(x_arr, y_arr, degree)
        y_fit = np.polyval(coeffs, x_arr)

        ss_res = float(np.sum((y_arr - y_fit) ** 2))
        ss_tot = float(np.sum((y_arr - np.mean(y_arr)) ** 2))
        r_squared = float(1.0 - ss_res / ss_tot) if ss_tot != 0.0 else 0.0

        self.add_log_entry(
            f"[RESULT] degree={degree}; R2={r_squared:.4f}; "
            f"coefficients={[round(float(c), 6) for c in coeffs]}"
        )
        return {
            "coefficients": [float(c) for c in coeffs],
            "r_squared": r_squared,
            "degree": degree,
        }

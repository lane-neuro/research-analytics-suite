"""
Operation:      LinearTrendForecast
Version:        0.0.1
Description:    Forecast future values by extrapolating a linear trend with prediction intervals.

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


class LinearTrendForecast(BaseOperation):
    """
    Forecast future values by fitting a linear trend and extrapolating with prediction intervals.
    Prediction intervals are computed via t-distribution accounting for regression SE
    and extrapolation uncertainty.

    Requires:
        series (list): Historical time series values (equally spaced).
        steps (int): Number of steps to forecast beyond the series (default 5).
        alpha (float): Significance level for prediction intervals (default 0.05).

    Returns:
        forecast (list): Forecasted values for the next 'steps' periods.
        lower_ci (list): Lower prediction interval bounds.
        upper_ci (list): Upper prediction interval bounds.
        slope (float): Fitted trend slope.
        intercept (float): Fitted trend intercept.
        r_squared (float): R-squared of the linear fit.
    """
    name = "LinearTrendForecast"
    version = "0.0.1"
    description = "Forecast future values by extrapolating a linear trend with prediction intervals."
    category_id = 503
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"series": list, "steps": int, "alpha": float}
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
        import numpy as np
        from scipy import stats

        _inputs = self.get_inputs()
        series = _inputs.get("series", [])
        steps = int(_inputs.get("steps", 5))
        alpha = float(_inputs.get("alpha", 0.05))

        n = len(series)
        x = np.arange(n, dtype=float)
        y = np.array(series, dtype=float)

        result = stats.linregress(x, y)
        slope = float(result.slope)
        intercept = float(result.intercept)
        r_squared = float(result.rvalue ** 2)

        x_bar = float(np.mean(x))
        ss_xx = float(np.sum((x - x_bar) ** 2))
        residuals = y - (slope * x + intercept)
        mse = float(np.sum(residuals ** 2) / (n - 2))
        t_crit = float(stats.t.ppf(1.0 - alpha / 2.0, df=n - 2))

        forecast = []
        lower_ci = []
        upper_ci = []
        for i in range(1, steps + 1):
            x_new = float(n - 1 + i)
            y_hat = slope * x_new + intercept
            se_pred = float(np.sqrt(mse * (1.0 + 1.0 / n + (x_new - x_bar) ** 2 / ss_xx)))
            margin = t_crit * se_pred
            forecast.append(float(y_hat))
            lower_ci.append(float(y_hat - margin))
            upper_ci.append(float(y_hat + margin))

        self.add_log_entry(
            f"[RESULT] slope={slope:.4f}; intercept={intercept:.4f}; "
            f"R2={r_squared:.4f}; forecasted {steps} steps"
        )
        return {
            "forecast": forecast,
            "lower_ci": lower_ci,
            "upper_ci": upper_ci,
            "slope": slope,
            "intercept": intercept,
            "r_squared": r_squared,
        }

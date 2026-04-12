"""
Operation:      ARIMAForecast
Version:        0.0.1
Description:    Fit an ARIMA model and produce an n-step forecast with confidence intervals.

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


class ARIMAForecast(BaseOperation):
    """
    Fit an ARIMA(p, d, q) model and produce an n-step forecast with 95% confidence intervals.

    Requires:
        series (list): Historical time series values.
        p (int): Autoregressive order (default 1).
        d (int): Differencing order (default 1).
        q (int): Moving average order (default 0).
        steps (int): Number of steps to forecast (default 5).

    Returns:
        forecast (list): Point forecast values.
        lower_ci (list): Lower bounds of the 95% prediction interval.
        upper_ci (list): Upper bounds of the 95% prediction interval.
        aic (float): AIC of the fitted model.
        order (list): ARIMA order [p, d, q].
    """
    name = "ARIMAForecast"
    version = "0.0.1"
    description = "Fit an ARIMA model and produce an n-step forecast with confidence intervals."
    category_id = 503
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"series": list, "p": int, "d": int, "q": int, "steps": int}
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
        import pandas as pd
        from statsmodels.tsa.arima.model import ARIMA

        _inputs = self.get_inputs()
        series = _inputs.get("series", [])
        p = int(_inputs.get("p", 1))
        d = int(_inputs.get("d", 1))
        q = int(_inputs.get("q", 0))
        steps = int(_inputs.get("steps", 5))

        ts = pd.Series(series, dtype=float)
        model = ARIMA(ts, order=(p, d, q)).fit()
        pred = model.get_forecast(steps=steps)
        summary = pred.summary_frame(alpha=0.05)

        forecast = [float(v) for v in summary["mean"].tolist()]
        lower_ci = [float(v) for v in summary["mean_ci_lower"].tolist()]
        upper_ci = [float(v) for v in summary["mean_ci_upper"].tolist()]

        self.add_log_entry(
            f"[RESULT] ARIMA({p},{d},{q}); AIC={model.aic:.4f}; "
            f"forecasted {steps} steps"
        )
        return {
            "forecast": forecast,
            "lower_ci": lower_ci,
            "upper_ci": upper_ci,
            "aic": float(model.aic),
            "order": [p, d, q],
        }

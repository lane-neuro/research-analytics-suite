"""
Operation:      ExponentialSmoothing
Version:        0.0.1
Description:    Forecast a time series using Holt-Winters exponential smoothing.

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


class ExponentialSmoothing(BaseOperation):
    """
    Forecast a time series using Holt-Winters exponential smoothing (ETS model).

    Requires:
        series (list): Historical time series values.
        steps (int): Number of steps to forecast (default 5).
        trend (str): Trend component -- "add", "mul", or "none" (default "add").
        seasonal (str): Seasonal component -- "add", "mul", or "none" (default "none").
        seasonal_periods (int): Seasonal period length (default 1; ignored if seasonal is "none").

    Returns:
        forecast (list): Forecasted values for the next 'steps' periods.
        fitted_values (list): In-sample fitted values.
        aic (float): Akaike information criterion of the fitted model.
        trend_type (str): Trend type used.
        seasonal_type (str): Seasonal type used.
    """
    name = "ExponentialSmoothing"
    version = "0.0.1"
    description = "Forecast a time series using Holt-Winters exponential smoothing."
    category_id = 503
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"series": list, "steps": int, "trend": str, "seasonal": str, "seasonal_periods": int}
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
        from statsmodels.tsa.holtwinters import ExponentialSmoothing as ETSModel

        _inputs = self.get_inputs()
        series = _inputs.get("series", [])
        steps = int(_inputs.get("steps", 5))
        trend_str = str(_inputs.get("trend", "add"))
        seasonal_str = str(_inputs.get("seasonal", "none"))
        seasonal_periods = int(_inputs.get("seasonal_periods", 1))

        trend = None if trend_str.lower() == "none" else trend_str
        seasonal = None if seasonal_str.lower() == "none" else seasonal_str
        sp = seasonal_periods if seasonal is not None and seasonal_periods > 1 else None

        ts = pd.Series(series, dtype=float)
        model = ETSModel(ts, trend=trend, seasonal=seasonal, seasonal_periods=sp).fit(
            optimized=True, disp=False
        )

        forecast = [float(v) for v in model.forecast(steps).tolist()]
        fitted_values = [float(v) for v in model.fittedvalues.tolist()]

        self.add_log_entry(
            f"[RESULT] Forecasted {steps} steps; AIC={model.aic:.4f}; "
            f"trend={trend_str}; seasonal={seasonal_str}"
        )
        return {
            "forecast": forecast,
            "fitted_values": fitted_values,
            "aic": float(model.aic),
            "trend_type": trend_str,
            "seasonal_type": seasonal_str,
        }

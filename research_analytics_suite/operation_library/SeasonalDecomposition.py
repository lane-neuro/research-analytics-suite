"""
Operation:      SeasonalDecomposition
Version:        0.0.1
Description:    Decompose a time series into trend, seasonal, and residual components.

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
from typing import List, Optional, Type
from research_analytics_suite.operation_manager import BaseOperation


class SeasonalDecomposition(BaseOperation):
    """
    Decompose a time series into trend, seasonal, and residual components using
    statsmodels seasonal_decompose (additive model).

    Requires:
        series (list): A list of numerical time series values.
        period (int): The seasonal period (e.g., 12 for monthly data).

    Returns:
        trend (list): Trend component.
        seasonal (list): Seasonal component.
        residual (list): Residual component.
    """
    name = "SeasonalDecomposition"
    version = "0.0.1"
    description = "Decompose a time series into trend, seasonal, and residual components."
    category_id = 502
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"series": list, "period": int}
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
        from statsmodels.tsa.seasonal import seasonal_decompose
        import pandas as pd

        _inputs = self.get_inputs()
        series = _inputs.get("series", [])
        period = int(_inputs.get("period", 12))

        ts = pd.Series(series, dtype=float)
        result = seasonal_decompose(ts, model="additive", period=period, extrapolate_trend="freq")

        trend = result.trend.fillna(0).tolist()
        seasonal = result.seasonal.tolist()
        residual = result.resid.fillna(0).tolist()

        self.add_log_entry(f"[RESULT] Seasonal decomposition complete (period={period}).")
        return {"trend": trend, "seasonal": seasonal, "residual": residual}

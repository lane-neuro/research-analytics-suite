"""
Operation:      AutocorrelationCalculation
Version:        0.0.1
Description:    Calculate the autocorrelation of a time series at specified lags.

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


class AutocorrelationCalculation(BaseOperation):
    """
    Calculate the autocorrelation of a time series at specified lags.

    Requires:
        series (list): A list of numerical time series values.
        nlags (int): Number of lags to compute (default: 40).

    Returns:
        autocorrelation (list): Autocorrelation values for lags 0..nlags.
        lags (list): The corresponding lag indices.
    """
    name = "AutocorrelationCalculation"
    version = "0.0.1"
    description = "Calculate the autocorrelation of a time series."
    category_id = 501
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"series": list, "nlags": int}
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
        _inputs = self.get_inputs()
        series = np.array(_inputs.get("series", []), dtype=float)
        nlags = int(_inputs.get("nlags", 40))

        n = len(series)
        mean = np.mean(series)
        var = np.var(series)
        if var == 0:
            acf = [1.0] + [0.0] * nlags
        else:
            acf = []
            for lag in range(nlags + 1):
                if lag >= n:
                    acf.append(0.0)
                else:
                    cov = np.mean((series[:n - lag] - mean) * (series[lag:] - mean))
                    acf.append(float(cov / var))

        lags = list(range(len(acf)))
        self.add_log_entry(f"[RESULT] Autocorrelation computed for {len(acf)} lags.")
        return {"autocorrelation": acf, "lags": lags}

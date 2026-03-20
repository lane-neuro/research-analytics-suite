"""
Operation:      QuantileCalculation
Version:        0.0.1
Description:    Calculate quantiles (percentiles) of a numerical list.

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


class QuantileCalculation(BaseOperation):
    """
    Calculate quantiles (percentiles) of a numerical list.

    Requires:
        numbers (list): A list of numerical values.
        quantiles (list): Quantile levels to compute, e.g. [0.25, 0.5, 0.75].

    Returns:
        quantile_table (DataFrame): A labeled table with quantile levels as the index and computed values as the column.
    """
    name = "QuantileCalculation"
    version = "0.0.1"
    description = "Calculate quantiles of a numerical list."
    category_id = 103
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"numbers": list, "quantiles": list}
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
        import pandas as pd
        _inputs = self.get_inputs()
        numbers = _inputs.get("numbers", [])
        quantile_levels = _inputs.get("quantiles", [0.25, 0.5, 0.75])

        values = np.quantile(numbers, quantile_levels).tolist()
        labels = [f"p{int(round(q * 100))}" for q in quantile_levels]
        quantile_table = pd.DataFrame({"value": values}, index=labels)
        self.add_log_entry(f"[RESULT] Quantiles {quantile_levels}: {values}")
        return {"quantile_table": quantile_table}

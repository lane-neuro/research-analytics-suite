"""
Operation:      PercentileCalculation
Version:        0.0.1
Description:    Calculate percentiles and quantiles of a numerical list.

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
from typing import Optional, Type, List
import numpy as np
from research_analytics_suite.operation_manager import BaseOperation


class PercentileCalculation(BaseOperation):
    """
    Calculate percentiles and quantiles of a numerical list.

    Requires:
        numbers (list): A list of numerical values to calculate percentiles from.
        percentiles (list): List of percentiles to calculate (default: [25, 50, 75]).

    Returns:
        percentile_values (dict): Dictionary mapping percentiles to their values.
        percentiles_calculated (list): List of percentiles that were calculated.
    """
    name = "PercentileCalculation"
    version = "0.0.1"
    description = "Calculate percentiles and quantiles of a numerical list."
    category_id = 103
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"numbers": list, "percentiles": List[float]}
    parent_operation: Optional[Type[BaseOperation]] = None
    inheritance: Optional[list] = []
    is_loop = False
    is_cpu_bound = False
    parallel = False

    def __init__(self, *args, **kwargs):
        """
        Initialize the operation.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)

    async def initialize_operation(self):
        """
        Initialize any resources or setup required for the operation before it starts.
        """
        await super().initialize_operation()

    async def execute(self):
        """
        Execute the operation to calculate percentiles of the provided numbers.
        """
        _inputs = self.get_inputs()
        _numbers = _inputs.get("numbers", [])
        _percentiles = _inputs.get("percentiles", [25, 50, 75])

        if _numbers is None or len(_numbers) == 0:
            raise ValueError("Cannot calculate percentiles of empty list")

        if not all(0 <= p <= 100 for p in _percentiles):
            raise ValueError("All percentiles must be between 0 and 100")

        percentile_values = {}
        for p in _percentiles:
            percentile_values[f"p{p}"] = np.percentile(_numbers, p)

        self.add_log_entry(f"[RESULT] Percentiles: {percentile_values}")
        return {
            "percentile_values": percentile_values,
            "percentiles_calculated": _percentiles
        }
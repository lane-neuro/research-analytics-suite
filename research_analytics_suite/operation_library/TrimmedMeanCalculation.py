"""
Operation:      TrimmedMeanCalculation
Version:        0.0.1
Description:    Calculate the trimmed mean of a numerical list.

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
from scipy.stats import trim_mean
from research_analytics_suite.operation_manager import BaseOperation


class TrimmedMeanCalculation(BaseOperation):
    """
    Calculate the trimmed mean of a numerical list.

    Requires:
        numbers (list): A list of numerical values to calculate the trimmed mean from.
        trim_proportion (float): The proportion of values to trim from each end (default: 0.1).

    Returns:
        trimmed_mean_value (float): The trimmed mean excluding outliers.
        trim_proportion_used (float): The actual proportion trimmed.
    """
    name = "TrimmedMeanCalculation"
    version = "0.0.1"
    description = "Calculate the trimmed mean of a numerical list."
    category_id = 101
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"numbers": list, "trim_proportion": float}
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
        Execute the operation to calculate the trimmed mean of the provided numbers.
        """
        _inputs = self.get_inputs()
        _numbers = _inputs.get("numbers", [])
        _trim_proportion = _inputs.get("trim_proportion", 0.1)

        if _numbers is None or len(_numbers) == 0:
            raise ValueError("Cannot calculate trimmed mean of empty list")

        if not 0 <= _trim_proportion < 0.5:
            raise ValueError("Trim proportion must be between 0 and 0.5")

        trimmed_mean_value = trim_mean(_numbers, _trim_proportion)

        self.add_log_entry(f"[RESULT] Trimmed Mean: {trimmed_mean_value}, Trim Proportion: {_trim_proportion}")
        return {
            "trimmed_mean_value": trimmed_mean_value,
            "trim_proportion_used": _trim_proportion
        }
"""
Operation:      GeometricMeanCalculation
Version:        0.0.1
Description:    Calculate the geometric mean of a numerical list.

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
from scipy.stats import gmean
from research_analytics_suite.operation_manager import BaseOperation


class GeometricMeanCalculation(BaseOperation):
    """
    Calculate the geometric mean of a numerical list.

    Requires:
        numbers (list): A list of positive numerical values to calculate the geometric mean from.

    Returns:
        geometric_mean_value (float): The geometric mean, useful for rates and ratios.
    """
    name = "GeometricMeanCalculation"
    version = "0.0.1"
    description = "Calculate the geometric mean of a numerical list."
    category_id = 101
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"numbers": list}
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
        Execute the operation to calculate the geometric mean of the provided numbers.
        """
        _inputs = self.get_inputs()
        _numbers = _inputs.get("numbers", [])

        if _numbers is None or len(_numbers) == 0:
            raise ValueError("Cannot calculate geometric mean of empty list")

        if any(num <= 0 for num in _numbers):
            raise ValueError("Geometric mean requires all positive values")

        geometric_mean_value = gmean(_numbers)

        self.add_log_entry(f"[RESULT] Geometric Mean: {geometric_mean_value}")
        return {"geometric_mean_value": geometric_mean_value}
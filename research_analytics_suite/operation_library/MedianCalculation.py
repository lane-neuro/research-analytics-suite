"""
Operation:      MedianCalculation
Version:        0.0.1
Description:    Calculate the median of a numerical list.

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
from statistics import median
from research_analytics_suite.operation_manager import BaseOperation


class MedianCalculation(BaseOperation):
    """
    Calculate the median of a numerical list.

    Requires:
        numbers (list): A list of numerical values to calculate the median from.

    Returns:
        median_value (float): The median value, which is the middle value when sorted.
    """
    name = "MedianCalculation"
    version = "0.0.1"
    description = "Calculate the median of a numerical list."
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
        Execute the operation to calculate the median of the provided numbers.
        """
        _inputs = self.get_inputs()
        _numbers = _inputs.get("numbers", [])

        if _numbers is None or len(_numbers) == 0:
            raise ValueError("Cannot calculate median of empty list")

        median_value = median(_numbers)

        self.add_log_entry(f"[RESULT] Median: {median_value}")
        return {"median_value": median_value}
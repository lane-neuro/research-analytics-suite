"""
Operation:      InterquartileRangeCalculation
Version:        0.0.1
Description:    Calculate the interquartile range (IQR) of a numerical list.

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
import numpy as np
from research_analytics_suite.operation_manager import BaseOperation


class InterquartileRangeCalculation(BaseOperation):
    """
    Calculate the interquartile range (IQR) of a numerical list.

    Requires:
        numbers (list): A list of numerical values to calculate the IQR from.

    Returns:
        q1 (float): The first quartile (25th percentile).
        q3 (float): The third quartile (75th percentile).
        iqr (float): The interquartile range (Q3 - Q1).
    """
    name = "InterquartileRangeCalculation"
    version = "0.0.1"
    description = "Calculate the interquartile range (IQR) of a numerical list."
    category_id = 102
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
        Execute the operation to calculate the IQR of the provided numbers.
        """
        _inputs = self.get_inputs()
        _numbers = _inputs.get("numbers", [])

        if _numbers is None or len(_numbers) == 0:
            raise ValueError("Cannot calculate IQR of empty list")

        q1 = np.percentile(_numbers, 25)
        q3 = np.percentile(_numbers, 75)
        iqr = q3 - q1

        self.add_log_entry(f"[RESULT] Q1: {q1}, Q3: {q3}, IQR: {iqr}")
        return {
            "q1": q1,
            "q3": q3,
            "iqr": iqr
        }
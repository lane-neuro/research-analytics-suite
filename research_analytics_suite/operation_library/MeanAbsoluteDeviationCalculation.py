"""
Operation:      MeanAbsoluteDeviationCalculation
Version:        0.0.1
Description:    Calculate the mean absolute deviation of a numerical list.

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
from statistics import median
from research_analytics_suite.operation_manager import BaseOperation


class MeanAbsoluteDeviationCalculation(BaseOperation):
    """
    Calculate the mean absolute deviation of a numerical list.

    Requires:
        numbers (list): A list of numerical values to calculate the MAD from.
        center (str): Center to calculate deviation from ('mean' or 'median', default: 'mean').

    Returns:
        mad (float): The mean absolute deviation.
        center_value (float): The center value used (mean or median).
        center_type (str): The type of center used.
    """
    name = "MeanAbsoluteDeviationCalculation"
    version = "0.0.1"
    description = "Calculate the mean absolute deviation of a numerical list."
    category_id = 102
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"numbers": list, "center": str}
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
        Execute the operation to calculate the mean absolute deviation.
        """
        _inputs = self.get_inputs()
        _numbers = _inputs.get("numbers", [])
        _center = _inputs.get("center", "mean")

        if _numbers is None or len(_numbers) == 0:
            raise ValueError("Cannot calculate MAD of empty list")

        if _center not in ["mean", "median"]:
            raise ValueError("Center must be 'mean' or 'median'")

        if _center == "mean":
            center_value = np.mean(_numbers)
        else:
            center_value = median(_numbers)

        mad = np.mean(np.abs(np.array(_numbers) - center_value))

        self.add_log_entry(f"[RESULT] MAD: {mad}, Center ({_center}): {center_value}")
        return {
            "mad": mad,
            "center_value": center_value,
            "center_type": _center
        }
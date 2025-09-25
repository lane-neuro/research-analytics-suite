"""
Operation:      CoefficientOfVariationCalculation
Version:        0.0.1
Description:    Calculate the coefficient of variation of a numerical list.

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


class CoefficientOfVariationCalculation(BaseOperation):
    """
    Calculate the coefficient of variation of a numerical list.

    Requires:
        numbers (list): A list of numerical values to calculate the CV from.

    Returns:
        cv (float): The coefficient of variation (std dev / mean).
        cv_percentage (float): The CV expressed as a percentage.
        mean_value (float): The mean of the dataset.
        std_dev (float): The standard deviation of the dataset.
    """
    name = "CoefficientOfVariationCalculation"
    version = "0.0.1"
    description = "Calculate the coefficient of variation of a numerical list."
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
        Execute the operation to calculate the coefficient of variation.
        """
        _inputs = self.get_inputs()
        _numbers = _inputs.get("numbers", [])

        if _numbers is None or len(_numbers) == 0:
            raise ValueError("Cannot calculate coefficient of variation of empty list")

        mean_value = np.mean(_numbers)

        if mean_value == 0:
            raise ValueError("Cannot calculate coefficient of variation when mean is zero")

        std_dev = np.std(_numbers, ddof=1)
        cv = std_dev / mean_value
        cv_percentage = cv * 100

        self.add_log_entry(f"[RESULT] CV: {cv:.4f} ({cv_percentage:.2f}%), Mean: {mean_value}, Std Dev: {std_dev}")
        return {
            "cv": cv,
            "cv_percentage": cv_percentage,
            "mean_value": mean_value,
            "std_dev": std_dev
        }
"""
Operation:      VarianceCalculation
Version:        0.0.1
Description:    Calculate the population and sample variance of a numerical list.

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


class VarianceCalculation(BaseOperation):
    """
    Calculate the population and sample variance of a numerical list.

    Requires:
        numbers (list): A list of numerical values to calculate the variance from.
        sample (bool): If True, calculate sample variance (N-1), else population variance (N).

    Returns:
        variance_value (float): The calculated variance.
        variance_type (str): Type of variance calculated (population or sample).
    """
    name = "VarianceCalculation"
    version = "0.0.1"
    description = "Calculate the population and sample variance of a numerical list."
    category_id = 102
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"numbers": list, "sample": bool}
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
        Execute the operation to calculate the variance of the provided numbers.
        """
        _inputs = self.get_inputs()
        _numbers = _inputs.get("numbers", [])
        _sample = _inputs.get("sample", True)

        if len(_numbers) < 2 and _sample:
            raise ValueError("Sample variance requires at least 2 values")

        ddof = 1 if _sample else 0
        variance_value = np.var(_numbers, ddof=ddof)
        variance_type = "sample" if _sample else "population"

        self.add_log_entry(f"[RESULT] {variance_type.capitalize()} Variance: {variance_value}")
        return {
            "variance_value": variance_value,
            "variance_type": variance_type
        }
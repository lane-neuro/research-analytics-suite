"""
Operation:      StandardDeviationCalculation
Version:        0.0.1
Description:    Calculate the standard deviation of a list of numbers.

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


class StandardDeviationCalculation(BaseOperation):
    """
    Calculate the standard deviation of a list of numbers.

    Requires:
        numbers (List[float]): The list of numbers to calculate the standard deviation.

    Returns:
        mean_value (float): The mean of the list of numbers.
        variance (float): The variance of the list of numbers.
        std_dev_value (float): The standard deviation of the list of numbers.
    """
    name = "StandardDeviationCalculation"
    version = "0.0.1"
    description = "Calculate the standard deviation of a list of numbers."
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
        Execute the operation's logic: calculate the standard deviation of the list of numbers.
        """
        _inputs = self.get_inputs()
        numbers: List[float] = _inputs.get("numbers", [])

        mean_value = sum(numbers) / len(numbers)
        variance = sum((x - mean_value) ** 2 for x in numbers) / len(numbers)
        std_dev_value = variance ** 0.5
        self.add_log_entry(f"[RESULT] Mean: {mean_value}; Variance: {variance}; Standard Deviation: {std_dev_value}")
        return {
            "mean_value": mean_value,
            "variance": variance,
            "std_dev_value": std_dev_value
        }

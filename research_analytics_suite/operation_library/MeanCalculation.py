"""
Operation:      MeanCalculation
Version:        0.0.1
Description:    Calculate the mean of a list of numbers.

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


class MeanCalculation(BaseOperation):
    """
    Calculate the mean of a list of numbers.

    Attributes:
        numbers (List[float]): The list of numbers to calculate the mean.

    Returns:
        mean_value (float): The mean of the list of numbers.
    """
    name = "MeanCalculation"
    version = "0.0.1"
    description = "Calculate the mean of a list of numbers."
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

    def __init__(self, numbers: List[float], *args, **kwargs):
        """
        Initialize the operation with the list of numbers.

        Args:
            numbers (List[float]): The list of numbers to calculate the mean.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.numbers = numbers
        super().__init__(*args, **kwargs)

    async def initialize_operation(self):
        """
        Initialize any resources or setup required for the operation before it starts.
        """
        await super().initialize_operation()

    async def execute(self):
        """
        Execute the operation's logic: calculate the mean of the list of numbers.
        """
        mean_value = sum(self.numbers) / len(self.numbers)
        print(f"Mean: {mean_value}")

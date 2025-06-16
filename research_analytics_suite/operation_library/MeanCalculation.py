"""
Operation:      MeanCalculation
Version:        0.0.1
Description:    Calculate the mean of a numerical list.

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
    Calculate the mean of a numerical list.

    Requires:
        numbers (list): A list of numerical values to calculate the mean from.

    Returns:
        mean_value (float): The mean value, which is the average of the numbers in the list.
    """
    name = "MeanCalculation"
    version = "0.0.1"
    description = "Calculate the mean of a numerical list."
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
        Execute the operation to calculate the mean of the provided numbers.
        """
        _inputs = self.get_inputs()
        _numbers = _inputs.get("numbers", [])

        mean_value = sum(_numbers) / len(_numbers)
        self.add_log_entry(f"[RESULT] Mean: {mean_value}")
        return {"mean_value": mean_value}

"""
Operation:      SumCalculation
Version:        0.0.1
Description:    Calculate the sum of a list of numbers.

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


class SumCalculation(BaseOperation):
    """
    Calculate the sum of a list of numbers.

    Requires:
        numbers (List[float]): The list of numbers to calculate the sum.

    Returns:
        sum_value (float): The sum of the list of numbers.
    """
    name = "SumCalculation"
    version = "0.0.1"
    description = "Calculate the sum of a list of numbers."
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
        Execute the operation's logic: calculate the sum of the list of numbers.
        """
        _inputs = self.get_inputs()
        numbers = _inputs.get("numbers", [])

        sum_value = sum(numbers)
        self.add_log_entry(f"[RESULT] Sum: {sum_value}")
        return {"sum_value": sum_value}

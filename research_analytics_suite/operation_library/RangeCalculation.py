"""
Operation:      RangeCalculation
Version:        0.0.1
Description:    Calculate the range, minimum, and maximum of a numerical list.

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
from research_analytics_suite.operation_manager import BaseOperation


class RangeCalculation(BaseOperation):
    """
    Calculate the range, minimum, and maximum of a numerical list.

    Requires:
        numbers (list): A list of numerical values to calculate the range from.

    Returns:
        min_value (float): The minimum value in the dataset.
        max_value (float): The maximum value in the dataset.
        range_value (float): The range (max - min) of the dataset.
    """
    name = "RangeCalculation"
    version = "0.0.1"
    description = "Calculate the range, minimum, and maximum of a numerical list."
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
        Execute the operation to calculate the range of the provided numbers.
        """
        _inputs = self.get_inputs()
        _numbers = _inputs.get("numbers", [])

        if _numbers is None or len(_numbers) == 0:
            raise ValueError("Cannot calculate range of empty list")

        min_value = min(_numbers)
        max_value = max(_numbers)
        range_value = max_value - min_value

        self.add_log_entry(f"[RESULT] Min: {min_value}, Max: {max_value}, Range: {range_value}")
        return {
            "min_value": min_value,
            "max_value": max_value,
            "range_value": range_value
        }
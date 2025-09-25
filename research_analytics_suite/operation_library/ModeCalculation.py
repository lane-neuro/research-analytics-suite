"""
Operation:      ModeCalculation
Version:        0.0.1
Description:    Calculate the mode of a list.

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
from statistics import mode
from research_analytics_suite.operation_manager import BaseOperation


class ModeCalculation(BaseOperation):
    """
    Calculate the mode of a categorical list.

    Requires:
        categories (list): A list of categorical values to calculate the mode from.

    Returns:
        mode_value (str): The mode value, which is the most frequently occurring category.
    """
    name = "ModeCalculation"
    version = "0.0.1"
    description = "Calculate the mode of a list of categories."
    category_id = 101
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"categories": list}
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
        Execute the operation's logic: calculate the mode.
        """
        _inputs = self.get_inputs()
        _categories = _inputs.get("categories", [])

        mode_value = mode(_categories)
        self.add_log_entry(f"[RESULT] Mode: {mode_value}")
        return {"mode_value": mode_value}

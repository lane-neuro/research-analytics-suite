"""
Operation:      FrequencyCount
Version:        0.0.1
Description:    Count the frequency of each category in a dataset.

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
from collections import Counter
from research_analytics_suite.operation_manager import BaseOperation


class FrequencyCount(BaseOperation):
    """
    Count the frequency of each category in a dataset.

    Requires:
        categories (list): A list of categories to count.

    Returns:
        frequency (Counter): The frequency of each category in the dataset.
    """
    name = "FrequencyCount"
    version = "0.0.1"
    description = "Count the frequency of each category in a dataset."
    category_id = 201
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
        Execute the operation's logic: count the frequency of each category.
        """
        _inputs = self.get_inputs()
        _categories = _inputs.get("categories", [])

        frequency = Counter(_categories)
        self.add_log_entry(f"[RESULT] Frequency: {frequency}")
        return {"frequency": frequency}

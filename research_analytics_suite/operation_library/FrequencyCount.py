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
Status:         Example
"""
from typing import List, Optional, Type
from collections import Counter
from research_analytics_suite.operation_manager import BaseOperation


class FrequencyCount(BaseOperation):
    """
    Count the frequency of each category in a dataset.

    Attributes:
        categories (List[str]): The list of categories to count the frequency.
    """
    name = "FrequencyCount"
    version = "0.0.1"
    description = "Count the frequency of each category in a dataset."
    category_id = 201
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    unique_id = f"{github}_{name}_{version}"
    required_inputs = {"categories": list}
    parent_operation: Optional[Type[BaseOperation]] = None
    inheritance: Optional[list] = []
    is_loop = False
    is_cpu_bound = False
    parallel = False

    def __init__(self, categories: List[str], *args, **kwargs):
        """
        Initialize the operation with the list of categories.

        Args:
            categories (List[str]): The list of categories to count the frequency.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.categories = categories
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
        frequency = Counter(self.categories)
        print(f"Frequency: {frequency}")

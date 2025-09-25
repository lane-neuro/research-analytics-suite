"""
Operation:      DescriptiveStatistics
Version:        0.0.1
Description:    Generate descriptive statistics for a dataset.

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
from statistics import mean, median, stdev
from research_analytics_suite.operation_manager import BaseOperation


class DescriptiveStatistics(BaseOperation):
    """
    Generate descriptive statistics for a dataset.

    Requires:
        data (List[float]): The dataset to generate descriptive statistics for.

    Returns:
        mean_value (float): The mean of the dataset.
        median_value (float): The median of the dataset.
        stdev_value (float): The standard deviation of the dataset.
    """
    name = "DescriptiveStatistics"
    version = "0.0.1"
    description = "Generate descriptive statistics for a dataset."
    category_id = 101
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"data": list}
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
        Execute the operation's logic: generate descriptive statistics for the dataset.
        """
        # TODO: calculate the mean, median, and standard deviation of the dataset using operations
        #  created in the operation library
        _inputs = self.get_inputs()
        _data = _inputs.get("data", [])

        mean_value = mean(_data)
        median_value = median(_data)
        stdev_value = stdev(_data)
        self.add_log_entry(f"[RESULT] Mean: {mean_value}, Median: {median_value}, Standard Deviation: {stdev_value}")
        return {
            "mean_value": mean_value,
            "median_value": median_value,
            "stdev_value": stdev_value
        }

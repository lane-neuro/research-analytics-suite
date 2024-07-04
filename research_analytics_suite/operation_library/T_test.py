"""
Operation:      T_test
Version:        0.0.1
Description:    Perform a t-test on a dataset.

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
from scipy import stats
from research_analytics_suite.operation_manager import BaseOperation


class T_test(BaseOperation):
    """
    Perform a t-test on a dataset.

    Attributes:
        sample1 (List[float]): The first sample for the t-test.
        sample2 (List[float]): The second sample for the t-test.

    Returns:
        t_stat (float): The t-statistic.
        p_value (float): The p-value.
    """
    name = "T_test"
    version = "0.0.1"
    description = "Perform a t-test on a dataset."
    category_id = 801
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    unique_id = f"{github}_{name}_{version}"
    required_inputs = {"sample1": list, "sample2": list}
    parent_operation: Optional[Type[BaseOperation]] = None
    inheritance: Optional[list] = []
    is_loop = False
    is_cpu_bound = False
    parallel = False

    def __init__(self, sample1: List[float], sample2: List[float], *args, **kwargs):
        """
        Initialize the operation with the samples.

        Args:
            sample1 (List[float]): The first sample for the t-test.
            sample2 (List[float]): The second sample for the t-test.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.sample1 = sample1
        self.sample2 = sample2
        super().__init__(*args, **kwargs)

    async def initialize_operation(self):
        """
        Initialize any resources or setup required for the operation before it starts.
        """
        await super().initialize_operation()

    async def execute(self):
        """
        Execute the operation's logic: perform the t-test on the samples.
        """
        t_stat, p_value = stats.ttest_ind(self.sample1, self.sample2)
        print(f"T-Statistic: {t_stat}, P-Value: {p_value}")

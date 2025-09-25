"""
Operation:      InferentialStatistics
Version:        0.0.1
Description:    Perform inferential statistical analysis on a dataset.

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


class InferentialStatistics(BaseOperation):
    """
    Perform inferential statistical analysis on a dataset.

    Requires:
        sample1 (list): A list of numerical values representing the first sample.
        sample2 (list): A list of numerical values representing the second sample.

    Returns:
        t_stat (float): The t-statistic value.
        p_value (float): The p-value
    """
    name = "InferentialStatistics"
    version = "0.0.1"
    description = "Perform inferential statistical analysis on a dataset."
    category_id = 201
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"sample1": list, "sample2": list}
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
        Execute the operation's logic: perform inferential statistical analysis on the samples.
        """
        _inputs = self.get_inputs()
        _sample1 = _inputs.get("sample1", [])
        _sample2 = _inputs.get("sample2", [])

        t_stat, p_value = stats.ttest_ind(_sample1, _sample2)
        self.add_log_entry(f"[RESULT] T-Statistic: {t_stat}, P-Value: {p_value}")
        return {"t_stat": t_stat, "p_value": p_value}

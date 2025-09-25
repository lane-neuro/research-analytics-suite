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
from research_analytics_suite.operation_manager import BaseOperation


class T_test(BaseOperation):
    """
    Perform a t-test on a dataset.

    Requires:
        sample1 (List[float]): The first sample for the t-test.
        sample2 (List[float]): The second sample for the t-test.

    Returns:
        t_stat (float): The t-statistic.
        p_value (float): The p-value.
    """
    name = "T_test"
    version = "0.0.1"
    description = "Perform a t-test on a dataset."
    category_id = 301
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
        Execute the operation's logic: perform the t-test on the samples.
        """
        from scipy import stats
        _inputs = self.get_inputs()
        sample1 = _inputs.get("sample1", [])
        sample2 = _inputs.get("sample2", [])

        t_stat, p_value = stats.ttest_ind(sample1, sample2)
        self.add_log_entry(f"[RESULT] t-Statistic: {t_stat}; p-Value: {p_value}")
        return {
            "t_stat": t_stat,
            "p_value": p_value
        }

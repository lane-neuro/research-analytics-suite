"""
Operation:      ChiSquareTest
Version:        0.0.1
Description:    Perform a chi-square test for independence.

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


class ChiSquareTest(BaseOperation):
    """
    Perform a chi-square test for independence.

    Attributes:
        observed (List[List[int]]): The observed frequencies.

    Returns:
        chi2_stat (float): The chi-square statistic.
        p_value (float): The p-value.
        dof (int): The degrees of freedom.
        expected (List[List[float]]): The expected frequencies.
    """
    name = "ChiSquareTest"
    version = "0.0.1"
    description = "Perform a chi-square test for independence."
    category_id = 801
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    unique_id = f"{github}_{name}_{version}"
    required_inputs = {"observed": list}
    parent_operation: Optional[Type[BaseOperation]] = None
    inheritance: Optional[list] = []
    is_loop = False
    is_cpu_bound = False
    parallel = False

    def __init__(self, observed: List[List[int]], *args, **kwargs):
        """
        Initialize the operation with the observed frequencies.

        Args:
            observed (List[List[int]]): The observed frequencies.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.observed = observed
        super().__init__(*args, **kwargs)

    async def initialize_operation(self):
        """
        Initialize any resources or setup required for the operation before it starts.
        """
        await super().initialize_operation()

    async def execute(self):
        """
        Execute the operation's logic: perform the chi-square test for independence.
        """
        chi2_stat, p_value, dof, expected = stats.chi2_contingency(self.observed)
        print(f"Chi-Square Statistic: {chi2_stat}, P-Value: {p_value}")

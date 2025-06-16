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

    Requires:
        observed (list): A 2D list of observed frequencies in a contingency table.

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
    required_inputs = {"observed": list}
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
        Execute the operation's logic: perform the chi-square test for independence.
        """
        _inputs = self.get_inputs()
        _observed = _inputs.get("observed", [])

        chi2_stat, p_value, dof, expected = stats.chi2_contingency(_observed)
        self.add_log_entry(f"[RESULT] Chi-Square Statistic: {chi2_stat}, P-Value: {p_value}, "
                           f"Degrees of Freedom: {dof}, Expected Frequencies: {expected}")
        return {
            "chi2_stat": chi2_stat,
            "p_value": p_value,
            "dof": dof,
            "expected": expected.tolist()  # Convert numpy array to list for JSON serialization
        }

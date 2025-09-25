"""
Operation:      NormalityTestCalculation
Version:        0.0.1
Description:    Test for normal distribution using the Shapiro-Wilk test.

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
from scipy.stats import shapiro
from research_analytics_suite.operation_manager import BaseOperation


class NormalityTestCalculation(BaseOperation):
    """
    Test for normal distribution using the Shapiro-Wilk test.

    Requires:
        numbers (list): A list of numerical values to test for normality.
        alpha (float): Significance level for the test (default: 0.05).

    Returns:
        statistic (float): The Shapiro-Wilk test statistic.
        p_value (float): The p-value of the test.
        is_normal (bool): Whether the data appears to be normally distributed.
        alpha_used (float): The significance level used.
        interpretation (str): Interpretation of the test result.
    """
    name = "NormalityTestCalculation"
    version = "0.0.1"
    description = "Test for normal distribution using the Shapiro-Wilk test."
    category_id = 103
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"numbers": list, "alpha": float}
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
        Execute the operation to test normality of the provided numbers.
        """
        _inputs = self.get_inputs()
        _numbers = _inputs.get("numbers", [])
        _alpha = _inputs.get("alpha", 0.05)

        if _numbers is None or len(_numbers) == 0:
            raise ValueError("Cannot test normality of empty list")

        if len(_numbers) < 3:
            raise ValueError("Shapiro-Wilk test requires at least 3 values")

        if len(_numbers) > 5000:
            raise ValueError("Shapiro-Wilk test is not reliable for samples > 5000")

        statistic, p_value = shapiro(_numbers)
        is_normal = p_value > _alpha

        if is_normal:
            interpretation = f"Data appears to be normally distributed (p > {_alpha})"
        else:
            interpretation = f"Data does not appear to be normally distributed (p ≤ {_alpha})"

        self.add_log_entry(f"[RESULT] Shapiro-Wilk: W={statistic:.4f}, p={p_value:.4f}, {interpretation}")
        return {
            "statistic": statistic,
            "p_value": p_value,
            "is_normal": is_normal,
            "alpha_used": _alpha,
            "interpretation": interpretation
        }
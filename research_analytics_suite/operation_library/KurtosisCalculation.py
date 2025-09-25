"""
Operation:      KurtosisCalculation
Version:        0.0.1
Description:    Calculate the kurtosis of a numerical list to measure distribution tail heaviness.

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
from scipy.stats import kurtosis
from research_analytics_suite.operation_manager import BaseOperation


class KurtosisCalculation(BaseOperation):
    """
    Calculate the kurtosis of a numerical list to measure distribution tail heaviness.

    Requires:
        numbers (list): A list of numerical values to calculate kurtosis from.
        fisher (bool): If True, return Fisher's kurtosis (excess kurtosis), else Pearson's (default: True).

    Returns:
        kurtosis_value (float): The kurtosis value.
        kurtosis_interpretation (str): Interpretation of the kurtosis.
        kurtosis_type (str): Type of kurtosis calculated (Fisher or Pearson).
    """
    name = "KurtosisCalculation"
    version = "0.0.1"
    description = "Calculate the kurtosis of a numerical list to measure distribution tail heaviness."
    category_id = 103
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"numbers": list, "fisher": bool}
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
        Execute the operation to calculate the kurtosis of the provided numbers.
        """
        _inputs = self.get_inputs()
        _numbers = _inputs.get("numbers", [])
        _fisher = _inputs.get("fisher", True)

        if _numbers is None or len(_numbers) == 0:
            raise ValueError("Cannot calculate kurtosis of empty list")

        if len(_numbers) < 4:
            raise ValueError("Kurtosis calculation requires at least 4 values")

        kurtosis_value = kurtosis(_numbers, fisher=_fisher)
        kurtosis_type = "Fisher (excess)" if _fisher else "Pearson"

        # Interpret kurtosis (assuming Fisher's kurtosis)
        if _fisher:
            if abs(kurtosis_value) < 0.5:
                interpretation = "mesokurtic (normal-like tails)"
            elif kurtosis_value > 0.5:
                interpretation = "leptokurtic (heavy tails)"
            else:
                interpretation = "platykurtic (light tails)"
        else:
            if 2.5 < kurtosis_value < 3.5:
                interpretation = "mesokurtic (normal-like tails)"
            elif kurtosis_value > 3.5:
                interpretation = "leptokurtic (heavy tails)"
            else:
                interpretation = "platykurtic (light tails)"

        self.add_log_entry(f"[RESULT] Kurtosis: {kurtosis_value:.4f} ({interpretation})")
        return {
            "kurtosis_value": kurtosis_value,
            "kurtosis_interpretation": interpretation,
            "kurtosis_type": kurtosis_type
        }
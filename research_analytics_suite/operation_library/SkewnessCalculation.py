"""
Operation:      SkewnessCalculation
Version:        0.0.1
Description:    Calculate the skewness of a numerical list to measure distribution asymmetry.

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
from scipy.stats import skew
from research_analytics_suite.operation_manager import BaseOperation


class SkewnessCalculation(BaseOperation):
    """
    Calculate the skewness of a numerical list to measure distribution asymmetry.

    Requires:
        numbers (list): A list of numerical values to calculate skewness from.
        bias (bool): If True, calculate biased skewness, else unbiased (default: True).

    Returns:
        skewness_value (float): The skewness value.
        skewness_interpretation (str): Interpretation of the skewness.
        bias_used (bool): Whether biased calculation was used.
    """
    name = "SkewnessCalculation"
    version = "0.0.1"
    description = "Calculate the skewness of a numerical list to measure distribution asymmetry."
    category_id = 103
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"numbers": list, "bias": bool}
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
        Execute the operation to calculate the skewness of the provided numbers.
        """
        _inputs = self.get_inputs()
        _numbers = _inputs.get("numbers", [])
        _bias = _inputs.get("bias", True)

        if _numbers is None or len(_numbers) == 0:
            raise ValueError("Cannot calculate skewness of empty list")

        if len(_numbers) < 3:
            raise ValueError("Skewness calculation requires at least 3 values")

        skewness_value = skew(_numbers, bias=_bias)

        # Interpret skewness
        if abs(skewness_value) < 0.5:
            interpretation = "approximately symmetric"
        elif skewness_value > 0.5:
            interpretation = "right-skewed (positive skew)"
        else:
            interpretation = "left-skewed (negative skew)"

        self.add_log_entry(f"[RESULT] Skewness: {skewness_value:.4f} ({interpretation})")
        return {
            "skewness_value": skewness_value,
            "skewness_interpretation": interpretation,
            "bias_used": _bias
        }